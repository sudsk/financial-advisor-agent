# agents/investment-agent/server.py - Following Official ADK Pattern

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
bucket_name = f"gs://{project_id}-financial-advisor-investment-logs"

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
app.title = "investment-agent-adk"
app.description = "ADK-powered investment advisory agent for GKE Hackathon - Portfolio optimization and retirement planning"

@app.get("/health")
async def health_check():
    """Kubernetes health check endpoint following ADK pattern"""
    return {
        "status": "healthy",
        "agent": "investment_agent_full_adk",
        "service": "financial-advisor-investment-agent",
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
        logger.info(f"📈 INVESTMENT AGENT: Received A2A message from {message.get('sender_id')}")
        logger.info(f"📈 INVESTMENT AGENT: Protocol: {x_a2a_protocol}, Correlation: {x_correlation_id}")
        
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
        from agent import assess_risk_profile, design_portfolio_allocation, calculate_retirement_projections
        
        if message_type == "assess_risk_profile":
            financial_data = payload.get("financial_data", {})
            risk_data = {
                "balance": financial_data.get("balance", {}).get("amount", 0),
                "monthly_income": 5000,  # Default estimation
                "monthly_expenses": financial_data.get("spending_analysis", {}).get("average_monthly", 0),
                "investment_timeline": 10  # Default 10 years
            }
            result = assess_risk_profile(json.dumps(risk_data))
            
        elif message_type == "design_portfolio":
            portfolio_data = {
                "risk_profile": "moderate",
                "investment_amount": payload.get("investment_amount", 25000),
                "timeline_years": payload.get("timeline_years", 10)
            }
            result = design_portfolio_allocation(json.dumps(portfolio_data))
            
        elif message_type == "retirement_planning":
            retirement_data = {
                "current_age": payload.get("current_age", 35),
                "retirement_age": 65,
                "current_savings": payload.get("current_savings", 0),
                "monthly_contribution": payload.get("monthly_contribution", 500)
            }
            result = calculate_retirement_projections(json.dumps(retirement_data))
            
        else:
            # Default to comprehensive investment analysis using multiple ADK tools
            logger.info(f"📈 INVESTMENT AGENT: Using comprehensive analysis for message type: {message_type}")
            
            financial_data = payload.get("financial_data", {})
            
            # Use ADK tools in sequence
            risk_data = {
                "balance": financial_data.get("balance", {}).get("amount", 15000),
                "monthly_income": 5000,
                "monthly_expenses": financial_data.get("spending_analysis", {}).get("average_monthly", 1500),
                "investment_timeline": 10
            }
            risk_result = assess_risk_profile(json.dumps(risk_data))
            risk_analysis = json.loads(risk_result)
            
            portfolio_data = {
                "risk_profile": risk_analysis.get("risk_profile", "moderate"),
                "investment_amount": 25000,
                "timeline_years": 10
            }
            portfolio_result = design_portfolio_allocation(json.dumps(portfolio_data))
            portfolio_analysis = json.loads(portfolio_result)
            
            # Combine ADK tool results
            combined_result = {
                "agent_id": "investment_agent_full_adk",
                "adk_tools_used": ["assess_risk_profile", "design_portfolio_allocation"],
                "risk_assessment": risk_analysis,
                "portfolio_design": portfolio_analysis,
                "summary": "Comprehensive investment analysis completed using ADK tools and sub-agents"
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
            "sender_id": "investment_agent_full_adk",
            "receiver_id": message.get("sender_id"),
            "response_to": message_type,
            "timestamp": datetime.now().isoformat(),
            "status": "success" if "error" not in response_data else "error",
            "payload": {
                "agent_type": "investment_analysis",
                "adk_enabled": True,
                "sub_agents_coordination": True,
                "analysis_results": response_data,
                "confidence": response_data.get("confidence", 0.87),
                "recommendations": response_data.get("investment_recommendations", response_data.get("recommendations", [])),
                "processing_metadata": {
                    "adk_framework": "google.adk.agents",
                    "adk_tools_used": ["assess_risk_profile", "design_portfolio_allocation", "calculate_retirement_projections"],
                    "processing_time": datetime.now().isoformat(),
                    "gke_hackathon": True
                }
            }
        }
        
        logger.info(f"✅ INVESTMENT AGENT: A2A response prepared for {message.get('sender_id')}")
        return a2a_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ INVESTMENT AGENT: A2A processing error: {str(e)}")
        
        # Return standardized error response in A2A format
        return {
            "message_id": message.get("message_id", "unknown"),
            "correlation_id": x_correlation_id,
            "sender_id": "investment_agent_full_adk",
            "receiver_id": message.get("sender_id", "unknown"),
            "response_to": message.get("message_type", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "payload": {
                "agent_type": "investment_analysis",
                "error": f"A2A processing failed: {str(e)}",
                "adk_enabled": True
            }
        }

@app.get("/a2a/capabilities")
async def get_a2a_capabilities():
    """Return A2A capabilities for service discovery and coordination"""
    return {
        "agent_id": "investment_agent_full_adk",
        "agent_type": "investment_analysis",
        "adk_enabled": True,
        "protocol_version": "financial-advisor-v1",
        "supported_message_types": [
            "assess_risk_profile",
            "design_portfolio",
            "retirement_planning",
            "comprehensive_investment_analysis"
        ],
        "capabilities": [
            "risk_tolerance_assessment",
            "portfolio_architecture_design", 
            "retirement_savings_projections",
            "investment_recommendation_engine"
        ],
        "adk_tools": [
            "assess_risk_profile",
            "design_portfolio_allocation", 
            "calculate_retirement_projections"
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
    """Collect and log feedback following Google's pattern."""
    cloud_logger.log_struct(feedback, severity="INFO")
    return {"status": "success"}

# Main execution following Google's pattern
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
