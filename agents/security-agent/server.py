# agents/security-agent/server.py - Full ADK Security Agent Server with A2A Protocol
import os
import json
from datetime import datetime
import google.auth
from fastapi import FastAPI, HTTPException, Header
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

# Import the security agent
from .agent import root_agent as security_agent

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
app.title = "Security Agent with Full ADK + A2A Protocol"
app.description = "Comprehensive financial security agent with ADK sub-agents and A2A protocol support"

@app.get("/health")
async def health_check():
    """Kubernetes health check endpoint"""
    return {
        "status": "healthy",
        "agent": "security_agent_full_adk",
        "model": security_agent.model,
        "sub_agents": len(security_agent.sub_agents) if security_agent.sub_agents else 0,
        "sub_agent_names": [agent.name for agent in (security_agent.sub_agents or [])],
        "tools": [tool.__name__ for tool in (security_agent.tools or [])],
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
    Handles A2A messages from coordinator with security analysis requests
    """
    try:
        logger.info(f"🛡️ SECURITY AGENT: Received A2A message from {message.get('sender_id')}")
        logger.info(f"🛡️ SECURITY AGENT: Protocol: {x_a2a_protocol}, Correlation: {x_correlation_id}")
        
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
        if message_type == "detect_fraud":
            # Use fraud detection sub-agent tool
            from .agent import detect_fraud_patterns
            financial_data = payload.get("financial_data", {})
            fraud_data = {
                "transactions": financial_data.get("recent_transactions", [])
            }
            result = detect_fraud_patterns(json.dumps(fraud_data))
            
        elif message_type == "assess_financial_health":
            # Use health assessment sub-agent tool
            from .agent import assess_financial_health
            financial_data = payload.get("financial_data", {})
            health_data = {
                "balance": financial_data.get("balance", {}).get("amount", 0),
                "monthly_income": 5000,  # Default estimation
                "monthly_expenses": financial_data.get("spending_analysis", {}).get("average_monthly", 0),
                "debt_amount": 5000,  # Default estimation
                "credit_score": 720  # Default assumption
            }
            result = assess_financial_health(json.dumps(health_data))
            
        elif message_type == "analyze_identity_protection":
            # Use identity protection sub-agent tool
            from .agent import analyze_identity_protection
            identity_data = {
                "protection_measures": payload.get("protection_measures", ["account_alerts"]),
                "financial_accounts": payload.get("financial_accounts", {}),
                "recent_changes": payload.get("recent_changes", [])
            }
            result = analyze_identity_protection(json.dumps(identity_data))
            
        elif message_type == "create_emergency_procedures":
            # Use emergency planning sub-agent tool
            from .agent import create_emergency_procedures
            emergency_data = {
                "financial_institutions": payload.get("financial_institutions", []),
                "insurance_policies": payload.get("insurance_policies", []),
                "emergency_contacts": payload.get("emergency_contacts", [])
            }
            result = create_emergency_procedures(json.dumps(emergency_data))
            
        else:
            # Default to comprehensive security analysis using multiple sub-agents
            logger.info(f"🛡️ SECURITY AGENT: Using comprehensive analysis for message type: {message_type}")
            from .agent import detect_fraud_patterns, assess_financial_health, analyze_identity_protection
            
            financial_data = payload.get("financial_data", {})
            
            # Fraud detection analysis
            fraud_data = {"transactions": financial_data.get("recent_transactions", [])}
            fraud_result = detect_fraud_patterns(json.dumps(fraud_data))
            fraud_analysis = json.loads(fraud_result)
            
            # Financial health assessment
            health_data = {
                "balance": financial_data.get("balance", {}).get("amount", 15000),
                "monthly_income": 5000,
                "monthly_expenses": financial_data.get("spending_analysis", {}).get("average_monthly", 1500),
                "debt_amount": 5000,
                "credit_score": 720
            }
            health_result = assess_financial_health(json.dumps(health_data))
            health_analysis = json.loads(health_result)
            
            # Identity protection analysis
            identity_data = {
                "protection_measures": ["account_alerts", "strong_passwords"],
                "financial_accounts": {"checking": {"alerts_enabled": True}},
                "recent_changes": []
            }
            identity_result = analyze_identity_protection(json.dumps(identity_data))
            identity_analysis = json.loads(identity_result)
            
            # Combine results
            combined_result = {
                "agent_id": "security_agent_full_adk",
                "sub_agents_used": ["fraud_detector", "health_assessor", "identity_guardian"],
                "fraud_analysis": fraud_analysis,
                "health_assessment": health_analysis,
                "identity_protection": identity_analysis,
                "overall_security_score": (
                    fraud_analysis.get("fraud_risk_score", 50) * 0.3 +
                    health_analysis.get("financial_health_score", 50) * 0.4 +
                    identity_analysis.get("identity_protection_score", 50) * 0.3
                ) / 3,
                "summary": "Comprehensive security analysis completed using ADK sub-agents"
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
            "sender_id": "security_agent_full_adk",
            "receiver_id": message.get("sender_id"),
            "response_to": message_type,
            "timestamp": datetime.now().isoformat(),
            "status": "success" if "error" not in response_data else "error",
            "payload": {
                "agent_type": "security_analysis",
                "sub_agents_coordination": True,
                "adk_enabled": True,
                "analysis_results": response_data,
                "confidence": response_data.get("confidence", 0.91),
                "recommendations": (
                    response_data.get("recommendations", []) or
                    response_data.get("priority_actions", []) or
                    response_data.get("monitoring_alerts", [])
                ),
                "processing_metadata": {
                    "adk_sub_agents": [agent.name for agent in (security_agent.sub_agents or [])],
                    "tools_used": [tool.__name__ for tool in (security_agent.tools or [])],
                    "processing_time": datetime.now().isoformat()
                }
            }
        }
        
        logger.info(f"✅ SECURITY AGENT: A2A response prepared for {message.get('sender_id')}")
        return a2a_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ SECURITY AGENT: A2A processing error: {str(e)}")
        
        # Return standardized error response in A2A format
        return {
            "message_id": message.get("message_id", "unknown"),
            "correlation_id": x_correlation_id,
            "sender_id": "security_agent_full_adk",
            "receiver_id": message.get("sender_id", "unknown"),
            "response_to": message.get("message_type", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "payload": {
                "agent_type": "security_analysis",
                "error": f"A2A processing failed: {str(e)}",
                "adk_enabled": True,
                "sub_agents_available": len(security_agent.sub_agents) if security_agent.sub_agents else 0
            }
        }

@app.get("/a2a/capabilities")
async def get_a2a_capabilities():
    """Return A2A capabilities for service discovery and coordination"""
    return {
        "agent_id": "security_agent_full_adk",
        "agent_type": "security_analysis",
        "adk_enabled": True,
        "protocol_version": "financial-advisor-v1",
        "supported_message_types": [
            "detect_fraud",
            "assess_financial_health",
            "analyze_identity_protection",
            "create_emergency_procedures",
            "comprehensive_security_analysis"
        ],
        "capabilities": [
            "fraud_pattern_detection",
            "financial_health_assessment",
            "identity_protection_analysis",
            "emergency_response_planning",
            "security_risk_evaluation"
        ],
        "sub_agents": [
            {
                "name": agent.name,
                "description": agent.description,
                "tools": [tool.__name__ for tool in (agent.tools or [])]
            } for agent in (security_agent.sub_agents or [])
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
            "name": security_agent.name,
            "description": security_agent.description,
            "model": security_agent.model,
            "adk_architecture": "full_sub_agent_coordination"
        },
        "sub_agents": [
            {
                "name": agent.name,
                "description": agent.description,
                "model": agent.model,
                "tools": [tool.__name__ for tool in (agent.tools or [])]
            } for agent in (security_agent.sub_agents or [])
        ],
        "a2a_protocol": {
            "enabled": True,
            "version": "financial-advisor-v1",
            "supported_messages": [
                "detect_fraud",
                "assess_financial_health",
                "analyze_identity_protection",
                "create_emergency_procedures"
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
@app.post("/assess")
async def assess_security_legacy(request: dict):
    """Legacy endpoint for direct security assessment (backward compatibility)"""
    try:
        logger.info("🛡️ SECURITY AGENT: Processing legacy assessment request")
        
        user_data = request.get("user_data", {})
        
        # Use ADK sub-agents for comprehensive analysis
        from .agent import detect_fraud_patterns, assess_financial_health
        
        # Fraud detection
        fraud_data = {"transactions": user_data.get("recent_transactions", [])}
        fraud_result = detect_fraud_patterns(json.dumps(fraud_data))
        fraud_analysis = json.loads(fraud_result)
        
        # Health assessment
        health_data = {
            "balance": user_data.get("balance", {}).get("amount", 15000),
            "monthly_expenses": user_data.get("spending_analysis", {}).get("average_monthly", 1500),
            "debt_amount": 5000,
            "credit_score": 720
        }
        health_result = assess_financial_health(json.dumps(health_data))
        health_analysis = json.loads(health_result)
        
        # Convert to legacy format for backward compatibility
        return {
            "agent_type": "security",
            "adk_enabled": True,
            "sub_agents_used": ["fraud_detector", "health_assessor"],
            "result": {
                "fraud_analysis": fraud_analysis,
                "financial_health": health_analysis,
                "overall_security_assessment": "Comprehensive security evaluation completed"
            },
            "recommendations": (
                fraud_analysis.get("recommendations", []) +
                health_analysis.get("improvement_recommendations", [])
            )[:5],  # Top 5 recommendations
            "confidence": 0.93,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ SECURITY AGENT: Legacy assessment error: {str(e)}")
        return {
            "agent_type": "security",
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
