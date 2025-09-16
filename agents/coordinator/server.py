# agents/coordinator/server.py - ADK FastAPI Server
import os
import google.auth
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

# Import our agent
from .agent import coordinator_agent

# Set up Google Cloud authentication and project
_, project_id = google.auth.default()
logging_client = google_cloud_logging.Client()
logger = logging_client.logger(__name__)

# Environment configuration
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# CORS configuration for frontend
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else [
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Local testing
        "*"  # Allow all origins for demo
    ]
)

# GCS bucket for logs (optional)
bucket_name = f"gs://{project_id}-financial-advisor-logs"

# Agent directory
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Create ADK FastAPI app
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=bucket_name,
    allow_origins=allow_origins,
    session_service_uri=None,  # In-memory sessions for demo
)

# Update app metadata
app.title = "AI Financial Advisor Coordinator"
app.description = "ADK-powered financial advisor agent coordinator for GKE Hackathon"

@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes"""
    return {
        "status": "healthy",
        "service": "financial-advisor-coordinator",
        "adk_enabled": True,
        "project_id": project_id,
        "agent_name": coordinator_agent.name
    }

@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents in the system"""
    return {
        "coordinator": {
            "name": coordinator_agent.name,
            "description": coordinator_agent.description,
            "model": coordinator_agent.model,
            "sub_agents": [agent.name for agent in coordinator_agent.sub_agents] if coordinator_agent.sub_agents else [],
            "tools": [tool.__name__ for tool in coordinator_agent.tools] if coordinator_agent.tools else []
        },
        "sub_agents": {
            agent.name: {
                "description": agent.description,
                "model": agent.model,
                "tools": [tool.__name__ for tool in agent.tools] if agent.tools else []
            } for agent in (coordinator_agent.sub_agents or [])
        }
    }

# Custom endpoint for direct financial analysis (backward compatibility)
@app.post("/analyze")
async def analyze_financial_query_endpoint(request: dict):
    """Direct endpoint for financial query analysis"""
    try:
        user_id = request.get("user_id")
        account_id = request.get("account_id") 
        query = request.get("query")
        
        if not all([user_id, account_id, query]):
            return {"error": "Missing required fields: user_id, account_id, query"}
        
        # Use ADK agent to process the request
        # This would typically be handled by the ADK framework
        # For now, we'll call our tool function directly
        from .agent import analyze_financial_query
        
        result = analyze_financial_query(query, {
            "user_id": user_id,
            "account_id": account_id
        })
        
        import json
        return {
            "status": "success",
            "result": json.loads(result),
            "adk_agent": coordinator_agent.name
        }
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return {"error": f"Analysis failed: {str(e)}"}

# Feedback collection
@app.post("/feedback")
def collect_feedback(feedback: dict):
    """Collect user feedback"""
    logger.log_struct(feedback, severity="INFO")
    return {"status": "success"}

# Main execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
