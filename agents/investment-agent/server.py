# agents/investment-agent/server.py - Full ADK Investment Agent Server with A2A Protocol
import os
import json
from datetime import datetime
import google.auth
from fastapi import FastAPI, HTTPException, Header
from google.adk.cli.fast_api import get_fast_api_app
from google.cloud import logging as google_cloud_logging

# Import the investment agent
from .agent import root_agent as investment_agent

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
app.title = "Investment Agent with Full ADK + A2A Protocol"
app.description = "Comprehensive investment advisory agent with ADK sub-agents and A2A protocol support"

@app.get("/health")
async def health_check():
    """Kubernetes health check endpoint"""
    return {
        "status": "healthy",
        "agent": "investment_agent_full_adk",
        "model": investment_agent.model,
        "sub_agents": len(investment_agent.sub_agents) if investment_agent.sub_agents else 0,
        "sub_agent_names": [agent.name for agent in (investment_agent.sub_agents or [])],
        "tools": [tool.__name__ for tool in (investment_agent.tools or [])],
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
    Handles A2A messages from coordinator with investment analysis requests
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
        
        # Route message to appropriate ADK sub-agent tools
        if message_type == "assess_risk_profile":
            # Use risk assessment sub-agent tool
            from .agent import assess_risk_profile
            financial_data = payload.get("financial_data", {})
            risk_data = {
                "balance": financial_data.get("balance", {}).get("amount", 0),
                "monthly_income": 5000,  # Default estimation
                "monthly_expenses": financial_data.get("spending_analysis", {}).get("average_monthly", 0),
                "investment_timeline": 10  # Default 10 years
            }
            result = assess_risk_profile(json.dumps(risk_data))
            
        elif message_type == "design_portfolio":
            # Use portfolio architect sub-agent tool
            from .agent import design_portfolio_allocation
            portfolio_data = {
                "risk_profile": "moderate",
                "investment_amount": payload.get("investment_amount", 25000),
                "timeline_years": payload.get("timeline_years", 10)
            }
            result = design_portfolio_allocation(json.dumps(portfolio_data))
            
        elif message_type == "retirement_planning":
            # Use retirement planner sub-agent tool
            from .agent import calculate_retirement_projections
            retirement_data = {
                "current_age": payload.get("current_age", 35),
                "retirement_age": 65,
                "current_savings": payload.get("current_savings", 0),
                "monthly_contribution": payload.get("monthly_contribution", 500)
            }
            result = calculate_retirement_projections(json.dumps(retirement_data))
            
        elif message_type == "optimize_taxes":
            # Use tax optimizer sub-agent tool
            from .agent import optimize_tax_strategy
            tax_data = {
                "current_income": payload.get("current_income", 75000),
                "investment_accounts": payload.get("investment_accounts", {}),
                "tax_bracket": 0.22
            }
            result = optimize_tax_strategy(json.dumps(tax_data))
            
        else:
            # Default to comprehensive investment analysis using multiple sub-agents
            logger.info(f"📈 INVESTMENT AGENT: Using comprehensive analysis for message type: {message_type}")
            from .agent import assess_risk_profile, design_portfolio_allocation
            
            financial_data = payload.get("financial_data", {})
            
            # Risk assessment
            risk_data = {
                "balance": financial_data.get("balance", {}).get("amount", 15000),
                "monthly_income": 5000,  # Estimated from financial data
                "monthly_expenses": financial_data.get("spending_analysis", {}).get("average_monthly", 1500),
                "investment_timeline": 10
            }
            risk_result = assess_risk_profile(json.dumps(risk_data))
            risk_analysis = json.loads(risk_result)
            
            # Portfolio design based on risk profile
            portfolio_data = {
                "risk_profile": risk_analysis.get("risk_profile", "moderate"),
                "investment_amount": 25000,  # Default investment amount
                "timeline_years": 10
            }
            portfolio_result = design_portfolio_allocation(json.dumps(portfolio_data))
            portfolio_analysis = json.loads(portfolio_result)
            
            # Combine results
            combined_result = {
                "agent_id": "investment_agent_full_adk",
                "sub_agents_used": ["risk_assessor", "portfolio_architect"],
                "risk_assessment": risk_analysis,
                "portfolio_design": portfolio_analysis,
                "summary": "Comprehensive investment analysis completed using ADK sub-agents"
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
                "sub_agents_coordination": True,
                "adk_enabled": True,
                "analysis_results": response_data,
                "confidence": response_data.get("confidence", 0.87),
                "recommendations": response_data.get("investment_recommendations", 
                                response_data.get("recommendations", [])),
                "processing_metadata": {
                    "adk_sub_agents": [agent.name for agent in (investment_agent.sub_agents or [])],
                    "tools_used": [tool.__name__ for tool in (investment_agent.tools or [])],
                    "processing_time": datetime.now().isoformat()
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
                "adk_enabled": True,
                "sub_agents_available": len(investment_agent.sub_agents) if investment_agent.sub_agents else 0
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
            "optimize_taxes",
            "comprehensive_investment_analysis"
        ],
        "capabilities": [
            "risk_tolerance_assessment",
            "portfolio_architecture_design", 
            "retirement_savings_projections",
            "tax_optimization_strategies",
            "investment_recommendation_engine"
        ],
        "sub_agents": [
            {
                "name": agent.name,
                "description": agent.description,
                "tools": [tool.__name__ for tool in (agent.tools or [])]
            } for agent in (investment_agent.sub_agents or [])
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
            "name": investment_agent.name,
            "description": investment_agent.description,
            "model": investment_agent.model,
            "adk_architecture": "full_sub_agent_coordination"
        },
        "sub_agents": [
            {
                "name": agent.name,
                "description": agent.description,
                "model": agent.model,
                "tools": [tool.__name__ for tool in (agent.tools or [])]
            } for agent in (investment_agent.sub_agents or [])
        ],
        "a2a_protocol": {
            "enabled": True,
            "version": "financial-advisor-v1",
            "supported_messages": [
                "assess_risk_profile",
                "design_portfolio", 
                "retirement_planning",
                "optimize_taxes"
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
@app.post("/recommend")
async def recommend_investments_legacy(request: dict):
    """Legacy endpoint for direct investment recommendations (backward compatibility)"""
    try:
        logger.info("📈 INVESTMENT AGENT: Processing legacy recommendation request")
        
        user_data = request.get("user_data", {})
        
        # Use ADK sub-agents for comprehensive analysis
        from .agent import assess_risk_profile, design_portfolio_allocation
        
        # Risk assessment
        risk_data = {
            "balance": user_data.get("balance", {}).get("amount", 15000),
            "monthly_expenses": user_data.get("spending_analysis", {}).get("average_monthly", 1500),
            "investment_timeline": 10
        }
        risk_result = assess_risk_profile(json.dumps(risk_data))
        risk_analysis = json.loads(risk_result)
        
        # Portfolio design
        portfolio_data = {
            "risk_profile": risk_analysis.get("risk_profile", "moderate"),
            "investment_amount": 25000,
            "timeline_years": 10
        }
        portfolio_result = design_portfolio_allocation(json.dumps(portfolio_data))
        portfolio_analysis = json.loads(portfolio_result)
        
        # Convert to legacy format for backward compatibility
        return {
            "agent_type": "investment",
            "adk_enabled": True,
            "sub_agents_used": ["risk_assessor", "portfolio_architect"],
            "result": {
                "risk_assessment": risk_analysis,
                "portfolio_recommendation": portfolio_analysis,
                "investment_strategy": f"Recommended {risk_analysis.get('risk_profile', 'moderate')} portfolio"
            },
            "recommendations": portfolio_analysis.get("investment_recommendations", []),
            "confidence": 0.89,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ INVESTMENT AGENT: Legacy recommendation error: {str(e)}")
        return {
            "agent_type": "investment",
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
