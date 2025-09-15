# agents/coordinator/main.py
from flask import Flask, request, jsonify
import asyncio
from datetime import datetime
from typing import Dict, List, Any
import json
import os
import httpx
from agent_logic import FinancialCoordinator

app = Flask(__name__)

# Initialize coordinator with environment variables
PROJECT_ID = os.getenv('PROJECT_ID', 'your-project-id')
REGION = os.getenv('REGION', 'us-central1')
MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'http://mcp-server.financial-advisor.svc.cluster.local:8080')

# Initialize coordinator
coordinator = FinancialCoordinator(
    project_id=PROJECT_ID,
    region=REGION,
    mcp_server_url=MCP_SERVER_URL
)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "agent": "coordinator",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "project_id": PROJECT_ID,
        "region": REGION
    })

@app.route('/analyze', methods=['POST'])
async def analyze_financial_query():
    """Main endpoint for financial query analysis"""
    try:
        data = request.get_json()
        
        user_id = data.get("user_id")
        account_id = data.get("account_id")
        query = data.get("query")
        
        if not all([user_id, account_id, query]):
            return jsonify({
                "error": "user_id, account_id, and query are required",
                "status": "error"
            }), 400
        
        # Process the financial query
        result = await coordinator.process_financial_query(user_id, account_id, query)
        
        return jsonify({
            "status": "success",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to analyze query: {str(e)}",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get coordinator status and agent health"""
    return jsonify({
        "coordinator": "healthy",
        "agents": {
            "budget": "ready",
            "investment": "ready", 
            "security": "ready"
        },
        "mcp_server": MCP_SERVER_URL,
        "timestamp": datetime.now().isoformat()
    })

@app.before_first_request
async def startup():
    """Initialize coordinator on startup"""
    await coordinator.initialize()

@app.teardown_appcontext
async def cleanup(error):
    """Cleanup on shutdown"""
    if error:
        print(f"Application error: {error}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
