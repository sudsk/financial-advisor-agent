# agents/coordinator/server.py - Following Official ADK Pattern

import os
import json
from datetime import datetime

import google.auth
from fastapi import FastAPI, HTTPException, Header
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

# Initialize Google Cloud following official pattern
_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)

# Environment setup (following Google's pattern)
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# CORS configuration for hackathon demo
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else [
        "http://localhost:3000",
        "http://financial-advisor-ui.financial-advisor.svc.cluster.local:80",
        "*"  # Allow all for demo
    ]
)

# GCS bucket for logs (following Google's pattern)
bucket_name = f"gs://{project_id}-financial-advisor-coordinator-logs"

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
app.title = "coordinator-agent-adk"
app.description = "ADK-powered financial coordinator agent for GKE Hackathon - MCP + A2A integration"

@app.get("/health")
async def health_check():
    """Kubernetes health check endpoint following ADK pattern"""
    return {
        "status": "healthy",
        "agent": "financial_coordinator_a2a",
        "service": "financial-advisor-coordinator-agent",
        "adk_enabled": True,
        "mcp_integration": True,
        "a2a_protocol": True,
        "project_id": project_id,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze")
async def analyze_financial_query(request: dict):
    """Main endpoint for financial query analysis using ADK coordination"""
    try:
        logger.info(f"🎯 COORDINATOR: Received analysis request")
        
        user_id = request.get("user_id")
        account_id = request.get("account_id") 
        query = request.get("query")
        
        if not all([user_id, account_id, query]):
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: user_id, account_id, query"
            )
        
        # Use ADK agent to process the request
        from agent import coordinate_financial_analysis
        
        user_data = {
            "user_id": user_id,
            "account_id": account_id
        }
        
        result = coordinate_financial_analysis(query, json.dumps(user_data))
        
        try:
            parsed_result = json.loads(result)
        except json.JSONDecodeError:
            parsed_result = {"raw_result": result}
        
        return {
            "status": "success",
            "result": parsed_result,
            "adk_agent": "financial_coordinator_a2a",
            "coordination_metadata": {
                "mcp_protocol": "✅ Bank of Anthos integration",
                "a2a_protocol": "✅ Multi-agent coordination",
                "adk_framework": "✅ Intelligent orchestration",
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ COORDINATOR: Analysis error: {str(e)}")
        return {
            "status": "error",
            "error": f"Analysis failed: {str(e)}",
            "adk_agent": "financial_coordinator_a2a",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/status")
async def get_detailed_status():
    """Get comprehensive coordinator status for monitoring"""
    try:
        from agent import root_agent
        
        return {
            "coordinator": {
                "name": root_agent.name,
                "description": root_agent.description,
                "model": root_agent.model,
                "tools": [tool.__name__ for tool in (root_agent.tools or [])]
            },
            "protocols": {
                "mcp": {
                    "enabled": True,
                    "server_url": os.getenv("MCP_SERVER_URL", "http://mcp-server.financial-advisor.svc.cluster.local:8080"),
                    "description": "Bank of Anthos API integration"
                },
                "a2a": {
                    "enabled": True,
                    "version": "financial-advisor-v1",
                    "agents": ["budget-agent", "investment-agent", "security-agent"]
                },
                "adk": {
                    "enabled": True,
                    "framework": "google.adk.agents",
                    "vertex_ai": True
                }
            },
            "system": {
                "project_id": project_id,
                "region": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
                "namespace": "financial-advisor",
                "gke_hackathon": True
            },
            "health": "healthy",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ COORDINATOR: Status error: {str(e)}")
        return {
            "error": f"Status check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/a2a/capabilities")
async def get_a2a_capabilities():
    """Return A2A capabilities for service discovery"""
    return {
        "agent_id": "financial_coordinator_a2a",
        "agent_type": "coordination",
        "adk_enabled": True,
        "protocol_version": "financial-advisor-v1",
        "coordination_capabilities": [
            "mcp_integration",
            "multi_agent_orchestration",
            "response_synthesis",
            "query_analysis"
        ],
        "supported_protocols": {
            "mcp": "Model Context Protocol for Bank of Anthos",
            "a2a": "Agent-to-Agent communication",
            "adk": "Agent Development Kit framework"
        },
        "distributed_agents": [
            "budget_agent_full_adk",
            "investment_agent_full_adk", 
            "security_agent_full_adk"
        ],
        "endpoints": {
            "analyze": "/analyze",
            "status": "/status",
            "capabilities": "/a2a/capabilities",
            "health": "/health"
        }
    }

@app.post("/a2a/process")
async def process_a2a_message(
    message: dict,
    x_a2a_protocol: str = Header(None, alias="X-A2A-Protocol"),
    x_correlation_id: str = Header(None, alias="X-Correlation-ID")
):
    """
    A2A Protocol endpoint for coordinator requests
    (Usually coordinators initiate, but this allows for agent-to-coordinator communication)
    """
    try:
        logger.info(f"🎯 COORDINATOR: Received A2A message from {message.get('sender_id')}")
        
        # Validate A2A message format
        required_fields = ["message_id", "sender_id", "receiver_id", "message_type", "payload"]
        missing_fields = [field for field in required_fields if field not in message]
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid A2A message format. Missing fields: {missing_fields}"
            )
        
        message_type = message.get("message_type")
        payload = message.get("payload", {})
        
        if message_type == "coordination_request":
            # Handle coordination requests from other agents
            query = payload.get("query", "")
            user_data = payload.get("user_data", {})
            
            from agent import coordinate_financial_analysis
            result = coordinate_financial_analysis(query, json.dumps(user_data))
            
            try:
                response_data = json.loads(result)
            except json.JSONDecodeError:
                response_data = {"raw_result": result}
        
        elif message_type == "status_request":
            # Return coordinator status
            response_data = {
                "coordinator_status": "active",
                "agents_available": ["budget", "investment", "security"],
                "protocols_enabled": ["mcp", "a2a", "adk"]
            }
        
        else:
            response_data = {
                "error": f"Unsupported message type: {message_type}",
                "supported_types": ["coordination_request", "status_request"]
            }
        
        # Build A2A response
        a2a_response = {
            "message_id": message.get("message_id"),
            "correlation_id": x_correlation_id or message.get("correlation_id"),
            "sender_id": "financial_coordinator_a2a",
            "receiver_id": message.get("sender_id"),
            "response_to": message_type,
            "timestamp": datetime.now().isoformat(),
            "status": "success" if "error" not in response_data else "error",
            "payload": {
                "agent_type": "coordination",
                "adk_enabled": True,
                "coordination_results": response_data,
                "processing_metadata": {
                    "adk_framework": "google.adk.agents",
                    "mcp_integration": True,
                    "a2a_coordination": True,
                    "processing_time": datetime.now().isoformat(),
                    "gke_hackathon": True
                }
            }
        }
        
        logger.info(f"✅ COORDINATOR: A2A response prepared for {message.get('sender_id')}")
        return a2a_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ COORDINATOR: A2A processing error: {str(e)}")
        
        return {
            "message_id": message.get("message_id", "unknown"),
            "correlation_id": x_correlation_id,
            "sender_id": "financial_coordinator_a2a",
            "receiver_id": message.get("sender_id", "unknown"),
            "response_to": message.get("message_type", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "payload": {
                "agent_type": "coordination",
                "error": f"A2A processing failed: {str(e)}",
                "adk_enabled": True
            }
        }

@app.post("/feedback")
def collect_feedback(feedback: dict) -> dict[str, str]:
    """Collect and log feedback following Google's pattern."""
    logger.log_struct(feedback, severity="INFO")
    return {"status": "success"}

# Main execution following Google's pattern
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
