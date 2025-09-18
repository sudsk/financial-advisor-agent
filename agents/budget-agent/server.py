# agents/budget-agent/server.py - Following Official ADK Pattern

import os
import json
import logging
from datetime import datetime

import google.auth
from fastapi import FastAPI, HTTPException, Header
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

# Initialize Google Cloud following official pattern
_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
cloud_logger = logging_client.logger(__name__)

# Set up standard Python logger for local use
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment setup (following Google's pattern)
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# CORS configuration for hackathon demo
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else [
        "http://localhost:3000",
        "http://coordinator-agent.financial-advisor.svc.cluster.local:8080",
        "http://financial-advisor-ui.financial-advisor.svc.cluster.local:80",
        "*"  # Allow all for demo
    ]
)

# GCS bucket for logs (following Google's pattern)
bucket_name = f"gs://{project_id}-financial-advisor-budget-logs"

# Agent directory
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# In-memory session configuration (following Google's pattern)
session_service_uri = None

# Create ADK FastAPI app following official pattern
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=bucket_name,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
)

# Update app metadata (following Google's pattern)
app.title = "budget-agent-adk"
app.description = "ADK-powered budget analysis agent for GKE Hackathon - Bank of Anthos integration"

@app.get("/health")
async def health_check():
    """Kubernetes health check endpoint following ADK pattern"""
    return {
        "status": "healthy",
        "agent": "budget_agent_full_adk",
        "service": "financial-advisor-budget-agent",
        "adk_enabled": True,
        "project_id": project_id,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/a2a/process")
async def process_a2a_message(
    message: dict,
    x_a2a_protocol: str = Header(None, alias="X-A2A-Protocol"),
    x_correlation_id: str = Header(None, alias="X-Correlation-ID")
):
    """
    A2A Protocol endpoint for inter-agent communication
    Following the hackathon A2A protocol specification
    """
    try:
        logger.info(f"💰 BUDGET AGENT: Received A2A message from {message.get('sender_id')}")
        logger.info(f"💰 BUDGET AGENT: Protocol: {x_a2a_protocol}, Correlation: {x_correlation_id}")
        
        # Validate A2A message format
        required_fields = ["message_id", "sender_id", "receiver_id", "message_type", "payload"]
        missing_fields = [field for field in required_fields if field not in message]
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid A2A message format. Missing fields: {missing_fields}"
            )
        
        # Validate protocol version
        if x_a2a_protocol and x_a2a_protocol != "financial-advisor-v1":
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported A2A protocol version: {x_a2a_protocol}"
            )
        
        # Extract message details
        message_type = message.get("message_type")
        payload = message.get("payload", {})
        
        # Route message to appropriate ADK tools (following the pattern)
        from agent import analyze_spending_categories, calculate_savings_opportunities, assess_emergency_fund
        
        if message_type == "analyze_spending":
            financial_data = payload.get("financial_data", {})
            spending_data = {
                "categories": financial_data.get("spending_analysis", {}).get("categories", {}),
                "balance": financial_data.get("balance", {}).get("amount", 0),
                "monthly_spending": financial_data.get("spending_analysis", {}).get("average_monthly", 0)
            }
            result = analyze_spending_categories(json.dumps(spending_data))
            
        elif message_type == "create_savings_plan":
            result = calculate_savings_opportunities(json.dumps(payload))
            
        elif message_type == "assess_emergency_fund":
            result = assess_emergency_fund(json.dumps(payload))
            
        else:
            # Default to comprehensive budget analysis using multiple ADK tools
            logger.info(f"💰 BUDGET AGENT: Using comprehensive analysis for message type: {message_type}")
            
            financial_data = payload.get("financial_data", {})
            
            # Use ADK tools in sequence
            spending_analysis = analyze_spending_categories(json.dumps(financial_data))
            savings_analysis = calculate_savings_opportunities(json.dumps(financial_data))
            emergency_analysis = assess_emergency_fund(json.dumps(financial_data))
            
            # Combine ADK tool results
            spending_result = json.loads(spending_analysis)
            savings_result = json.loads(savings_analysis)
            emergency_result = json.loads(emergency_analysis)
            
            combined_result = {
                "agent_id": "budget_agent_full_adk",
                "adk_tools_used": ["analyze_spending_categories", "calculate_savings_opportunities", "assess_emergency_fund"],
                "spending_analysis": spending_result,
                "savings_analysis": savings_result,
                "emergency_fund_analysis": emergency_result,
                "summary": "Comprehensive budget analysis completed using ADK tools and sub-agents"
            }
            result = json.dumps(combined_result)
        
        # Parse result and build A2A response
        try:
            response_data = json.loads(result)
        except json.JSONDecodeError:
            response_data = {"raw_result": result}
        
        # Build standardized A2A protocol response
        a2a_response = {
            "message_id": message.get("message_id"),
            "correlation_id": x_correlation_id or message.get("correlation_id"),
            "sender_id": "budget_agent_full_adk",
            "receiver_id": message.get("sender_id"),
            "response_to": message_type,
            "timestamp": datetime.now().isoformat(),
            "status": "success" if "error" not in response_data else "error",
            "payload": {
                "agent_type": "budget_analysis",
                "adk_enabled": True,
                "sub_agents_coordination": True,
                "analysis_results": response_data,
                "confidence": response_data.get("confidence", 0.85),
                "recommendations": response_data.get("recommendations", response_data.get("optimization_opportunities", [])),
                "processing_metadata": {
                    "adk_framework": "google.adk.agents",
                    "adk_tools_used": ["analyze_spending_categories", "calculate_savings_opportunities", "assess_emergency_fund"],
                    "processing_time": datetime.now().isoformat(),
                    "gke_hackathon": True
                }
            }
        }
        
        logger.info(f"✅ BUDGET AGENT: A2A response prepared for {message.get('sender_id')}")
        return a2a_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ BUDGET AGENT: A2A processing error: {str(e)}")
        
        # Return standardized error response in A2A format
        return {
            "message_id": message.get("message_id", "unknown"),
            "correlation_id": x_correlation_id,
            "sender_id": "budget_agent_full_adk",
            "receiver_id": message.get("sender_id", "unknown"),
            "response_to": message.get("message_type", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "payload": {
                "agent_type": "budget_analysis",
                "error": f"A2A processing failed: {str(e)}",
                "adk_enabled": True
            }
        }

@app.get("/a2a/capabilities")
async def get_a2a_capabilities():
    """Return A2A capabilities for service discovery and coordination"""
    return {
        "agent_id": "budget_agent_full_adk",
        "agent_type": "budget_analysis",
        "adk_enabled": True,
        "protocol_version": "financial-advisor-v1",
        "supported_message_types": [
            "analyze_spending",
            "create_savings_plan", 
            "assess_emergency_fund",
            "comprehensive_budget_analysis"
        ],
        "capabilities": [
            "spending_pattern_analysis",
            "category_optimization",
            "savings_strategy_creation", 
            "emergency_fund_assessment",
            "budget_plan_creation"
        ],
        "adk_tools": [
            "analyze_spending_categories",
            "calculate_savings_opportunities", 
            "assess_emergency_fund"
        ],
        "endpoints": {
            "a2a_process": "/a2a/process",
            "capabilities": "/a2a/capabilities", 
            "health": "/health",
            "feedback": "/feedback"
        }
    }

@app.post("/feedback")
def collect_feedback(feedback: dict) -> dict[str, str]:
    """Collect and log feedback following Google's pattern.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    cloud_logger.log_struct(feedback, severity="INFO")
    return {"status": "success"}

# Main execution following Google's pattern
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
