# agents/budget-agent/server.py - Budget Agent Server with A2A Protocol
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

# CORS configuration
allow_origins = [
    "http://localhost:3000",
    "http://coordinator-agent.financial-advisor.svc.cluster.local:8080",
    "*"
]

# Agent directory
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Create ADK FastAPI app
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    allow_origins=allow_origins,
    session_service_uri=None
)

app.title = "Budget Agent with A2A Protocol"
app.description = "ADK Budget Analysis Agent with A2A Protocol for GKE Hackathon"

@app.get("/health")
async def health_check():
    """Kubernetes health check"""
    return {
        "status": "healthy",
        "agent": "budget_agent",
        "model": budget_agent.model,
        "a2a_protocol": "enabled",
        "tools": [tool.__name__ for tool in budget_agent.tools],
        "project_id": project_id
    }

@app.post("/a2a/process")
async def process_a2a_message(
    message: dict,
    x_a2a_protocol: str = Header(None, alias="X-A2A-Protocol"),
    x_correlation_id: str = Header(None, alias="X-Correlation-ID")
):
    """
    A2A Protocol endpoint for inter-agent communication
    
    Handles A2A messages from the coordinator agent with financial analysis requests
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
        if x_a2a_protocol != "financial-advisor-v1":
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported A2A protocol version: {x_a2a_protocol}"
            )
        
        # Route message based on type
        message_type = message.get("message_type")
        payload = message.get("payload", {})
        
        if message_type == "analyze_spending":
            # Use the ADK agent's A2A tool for spending analysis
            from .agent import process_a2a_spending_analysis
            result = process_a2a_spending_analysis(json.dumps(payload))
            response_data = json.loads(result)
            
        elif message_type == "create_savings_plan":
            # Use the savings strategy tool
            from .agent import create_savings_strategy
            result = create_savings_strategy(json.dumps(payload))
            response_data = json.loads(result)
            
        else:
            # Default to spending analysis for unknown message types
            logger.warning(f"💰 BUDGET AGENT: Unknown message type {message_type}, defaulting to spending analysis")
            from .agent import process_a2a_spending_analysis
            result = process_a2a_spending_analysis(json.dumps(payload))
            response_data = json.loads(result)
        
        # Build A2A protocol response
        a2a_response = {
            "message_id": message.get("message_id"),
            "correlation_id": x_correlation_id or message.get("correlation_id"),
            "sender_id": "budget_agent",
            "receiver_id": message.get("sender_id"),
            "response_to": message_type,
            "timestamp": datetime.now().isoformat(),
            "status": "success" if "error" not in response_data else "error",
            "payload": response_data
        }
        
        logger.info(f"✅ BUDGET AGENT: A2A response prepared for {message.get('sender_id')}")
        return a2a_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ BUDGET AGENT: A2A processing error: {str(e)}")
        
        # Return error in A2A format
        return {
            "message_id": message.get("message_id", "unknown"),
            "correlation_id": x_correlation_id,
            "sender_id": "budget_agent",
            "receiver_id": message.get("sender_id", "unknown"),
            "response_to": message.get("message_type", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "payload": {
                "error": f"A2A processing failed: {str(e)}",
                "agent_id": "budget_agent",
                "agent_type": "budget_analysis"
            }
        }

@app.get("/a2a/capabilities")
async def get_a2a_capabilities():
    """Return A2A capabilities for service discovery"""
    return {
        "agent_id": "budget_agent",
        "agent_type": "budget_analysis",
        "protocol_version": "financial-advisor-v1",
        "supported_message_types": [
            "analyze_spending",
            "create_savings_plan"
        ],
        "capabilities": [
            "spending_pattern_analysis",
            "budget_optimization",
            "savings_strategy_creation",
            "emergency_fund_assessment"
        ],
        "tools": [tool.__name__ for tool in budget_agent.tools],
        "endpoint": "/a2a/process",
        "health_endpoint": "/health"
    }

# Legacy endpoint for backward compatibility
@app.post("/analyze")
async def analyze_budget_legacy(request: dict):
    """Legacy endpoint for direct budget analysis (non-A2A)"""
    try:
        logger.info("💰 BUDGET AGENT: Processing legacy analysis request")
        
        user_data = request.get("user_data", {})
        
        # Convert to A2A format and process
        from .agent import process_a2a_spending_analysis
        result = process_a2a_spending_analysis(json.dumps({
            "financial_data": user_data,
            "query_context": request.get("context", {}).get("query", ""),
            "correlation_id": "legacy_request"
        }))
        
        response_data = json.loads(result)
        
        # Convert back to legacy format
        return {
            "agent_type": "budget",
            "result": response_data.get("analysis_results", response_data),
            "recommendations": response_data.get("recommendations", []),
            "confidence": response_data.get("confidence", 0.8),
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ BUDGET AGENT: Legacy analysis error: {str(e)}")
        return {
            "agent_type": "budget", 
            "error": str(e),
            "confidence": 0.0,
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/status")
async def get_agent_status():
    """Get detailed agent status for monitoring"""
    return {
        "agent": {
            "name": budget_agent.name,
            "description": budget_agent.description,
            "model": budget_agent.model,
            "tools": [tool.__name__ for tool in budget_agent.tools]
        },
        "a2a_protocol": {
            "enabled": True,
            "version": "financial-advisor-v1",
            "supported_messages": ["analyze_spending", "create_savings_plan"]
        },
        "system": {
            "project_id": project_id,
            "region": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
            "vertex_ai_enabled": os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "True"
        },
        "health": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)# agents/budget-agent/server.py - ADK Budget Agent Server
import os
import json
from datetime import datetime
import google.auth
from fastapi import FastAPI, HTTPException
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

# CORS configuration
allow_origins = [
    "http://localhost:3000",
    "http://coordinator-agent.financial-advisor.svc.cluster.local:8080",
    "*"
]

# Agent directory
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Create ADK FastAPI app
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    allow_origins=allow_origins,
    session_service_uri=None
)

app.title = "Budget Agent"
app.description = "ADK Budget Analysis Agent for Financial Advisory"

@app.get("/health")
async def health_check():
    """Health check for Kubernetes"""
    return {
        "status": "healthy",
        "agent": "budget_agent",
        "model": budget_agent.model,
        "tools": [tool.__name__ for tool in budget_agent.tools]
    }

# Legacy endpoint for A2A compatibility (if needed)
@app.post("/analyze")
async def analyze_budget_legacy(request: dict):
    """Legacy endpoint for direct budget analysis"""
    try:
        user_data = request.get("user_data", {})
        
        # Use ADK agent to process
        from .agent import analyze_spending_patterns
        result = analyze_spending_patterns(json.dumps(user_data))
        
        return {
            "agent_type": "budget",
            "result": json.loads(result),
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Budget analysis error: {str(e)}")
        return {
            "agent_type": "budget", 
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
