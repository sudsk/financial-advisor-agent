# agents/budget-agent/server.py - Full ADK Budget Agent Server with A2A Protocol
import os
import json
from datetime import datetime
import google.auth
from fastapi import FastAPI, HTTPException, Header
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

# Import the budget agent
from .agent import root_agent as budget_agent

# Set up Google Cloud
_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)

# Environment setup
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1") 
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# CORS configuration for cross-pod communication
allow_origins = [
    "http://localhost:3000",
    "http://coordinator-agent.financial-advisor.svc.cluster.local:8080",
    "http://financial-advisor-ui.financial-advisor.svc.cluster.local:80",
    "*"  # Allow all for demo purposes
]

# Agent directory for ADK
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Create ADK FastAPI app with automatic agent endpoint generation
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    allow_origins=allow_origins,
    session_service_uri=None  # In-memory sessions for demo
)

# Update app metadata
app.title = "Budget Agent with Full ADK + A2A Protocol"
app.description = "Comprehensive budget analysis agent with ADK sub-agents and A2A protocol support"

@app.get("/health")
async def health_check():
    """Kubernetes health check endpoint"""
    return {
        "status": "healthy",
        "agent": "budget_agent_full_adk",
        "model": budget_agent.model,
        "sub_agents": len(budget_agent.sub_agents) if budget_agent.sub_agents else 0,
        "sub_agent_names": [agent.name for agent in (budget_agent.sub_agents or [])],
        "tools": [tool.__name__ for tool in (budget_agent.tools or [])],
        "a2a_protocol": "enabled",
        "project_id": project_id,
        "adk_enabled": True
    }

@app.post("/a2a/process")
async def process_a2a_message(
    message: dict,
    x_a2a_protocol: str = Header(None, alias="X-A2A-Protocol"),
    x_correlation_id: str = Header(None, alias="X-Correlation-ID")
):
    """
    A2A Protocol endpoint for inter-agent communication
    Handles A2A messages from coordinator with budget analysis requests
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
        
        # Route message to appropriate ADK sub-agent tools
        if message_type == "analyze_spending":
            # Use spending analyzer sub-agent tool
            from .agent import analyze_spending_categories
            financial_data = payload.get("financial_data", {})
            spending_data = {
                "categories": financial_data.get("spending_analysis", {}).get("categories", {}),
                "balance": financial_data.get("balance", {}).get("amount", 0),
                "monthly_spending": financial_data.get("spending_analysis", {}).get("average_monthly", 0)
            }
            result = analyze_spending_categories(json.dumps(spending_data))
            
        elif message_type == "create_savings_plan":
            # Use savings strategist sub-agent tool
            from .agent import calculate_savings_opportunities
            result = calculate_savings_opportunities(json.dumps(payload))
            
        elif message_type == "assess_emergency_fund":
            # Use emergency fund advisor sub-agent tool
            from .agent import assess_emergency_fund
            result = assess_emergency_fund(json.dumps(payload))
            
        else:
            # Default to comprehensive budget analysis
            logger.info(f"💰 BUDGET AGENT: Using comprehensive analysis for message type: {message_type}")
            from .agent import analyze_spending_categories, calculate_savings_opportunities
            
            financial_data = payload.get("financial_data", {})
            spending_analysis = analyze_spending_categories(json.dumps(financial_data))
            savings_analysis = calculate_savings_opportunities(json.dumps(financial_data))
            
            # Combine results
            spending_result = json.loads(spending_analysis)
            savings_result = json.loads(savings_analysis)
            
            combined_result = {
                "agent_id": "budget_agent_full_adk",
                "sub_agents_used": ["spending_analyzer", "savings_strategist"],
                "spending_analysis": spending_result,
                "savings_analysis": savings_result,
                "summary": "Comprehensive budget analysis completed using ADK sub-agents"
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
                "sub_agents_coordination": True,
                "adk_enabled": True,
                "analysis_results": response_data,
                "confidence": response_data.get("confidence", 0.85),
                "recommendations": response_data.get("recommendations", response_data.get("optimization_opportunities", [])),
                "processing_metadata": {
                    "adk_sub_agents": [agent.name for agent in (budget_agent.sub_agents or [])],
                    "tools_used": [tool.__name__ for tool in (budget_agent.tools or [])],
                    "processing_time": datetime.now().isoformat()
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
                "adk_enabled": True,
                "sub_agents_available": len(budget_agent.sub_agents) if budget_agent.sub_agents else 0
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
        "sub_agents": [
            {
                "name": agent.name,
                "description": agent.description,
                "tools": [tool.__name__ for tool in (agent.tools or [])]
            } for agent in (budget_agent.sub_agents or [])
        ],
        "endpoints": {
            "a2a_process": "/a2a/process",
            "capabilities": "/a2a/capabilities", 
            "health": "/health",
            "status": "/status"
        }
    }

@app.get("/status")
async def get_detailed_agent_status():
    """Get comprehensive agent status for monitoring and debugging"""
    return {
        "agent": {
            "name": budget_agent.name,
            "description": budget_agent.description,
            "model": budget_agent.model,
            "adk_architecture": "full_sub_agent_coordination"
        },
        "sub_agents": [
            {
                "name": agent.name,
                "description": agent.description,
                "model": agent.model,
                "tools": [tool.__name__ for tool in (agent.tools or [])]
            } for agent in (budget_agent.sub_agents or [])
        ],
        "a2a_protocol": {
            "enabled": True,
            "version": "financial-advisor-v1",
            "supported_messages": [
                "analyze_spending", 
                "create_savings_plan",
                "assess_emergency_fund"
            ]
        },
        "system": {
            "project_id": project_id,
            "region": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
            "vertex_ai_enabled": os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "True",
            "adk_enabled": True
        },
        "health": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Legacy endpoint for backward compatibility (non-A2A direct calls)
@app.post("/analyze")
async def analyze_budget_legacy(request: dict):
    """Legacy endpoint for direct budget analysis (backward compatibility)"""
    try:
        logger.info("💰 BUDGET AGENT: Processing legacy analysis request")
        
        user_data = request.get("user_data", {})
        
        # Use ADK sub-agents for comprehensive analysis
        from .agent import analyze_spending_categories, calculate_savings_opportunities
        
        spending_result = analyze_spending_categories(json.dumps(user_data))
        savings_result = calculate_savings_opportunities(json.dumps(user_data))
        
        # Parse results
        spending_data = json.loads(spending_result)
        savings_data = json.loads(savings_result)
        
        # Convert to legacy format for backward compatibility
        return {
            "agent_type": "budget",
            "adk_enabled": True,
            "sub_agents_used": ["spending_analyzer", "savings_strategist"],
            "result": {
                "spending_analysis": spending_data,
                "savings_opportunities": savings_data.get("savings_strategies", []),
                "total_savings_potential": savings_data.get("total_monthly_savings_potential", 0)
            },
            "recommendations": savings_data.get("savings_strategies", [])[:3],  # Top 3
            "confidence": 0.90,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ BUDGET AGENT: Legacy analysis error: {str(e)}")
        return {
            "agent_type": "budget",
            "adk_enabled": True,
            "error": str(e),
            "confidence": 0.0,
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }

# Main execution for development/testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
