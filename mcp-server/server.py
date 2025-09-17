# mcp-server/server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import httpx
from typing import Dict, Any, List, Optional
from bank_anthos_client import BankOfAnthosClient
import os
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(title="Bank of Anthos MCP Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Bank of Anthos client
bank_client = BankOfAnthosClient()

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    await bank_client.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up connections on shutdown"""
    await bank_client.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "bank-of-anthos-mcp-server",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/tools/authenticate")
async def authenticate_user(request: Dict[str, Any]):
    """Authenticate user and get JWT token"""
    try:
        username = request.get("username")
        password = request.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="username and password are required")
        
        result = await bank_client.authenticate_user(username, password)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to authenticate user: {str(e)}")

@app.post("/tools/get_user_profile")
async def get_user_profile(request: Dict[str, Any]):
    """Get user profile from JWT token"""
    try:
        token = request.get("token")
        
        if not token:
            raise HTTPException(status_code=400, detail="token is required")
        
        profile = await bank_client.get_user_profile(token)
        return {"profile": profile}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")

@app.post("/tools/get_account_balance")
async def get_account_balance(request: Dict[str, Any]):
    """Get account balance"""
    try:
        account_id = request.get("account_id")
        token = request.get("token")
        
        if not account_id or not token:
            raise HTTPException(status_code=400, detail="account_id and token are required")
        
        balance = await bank_client.get_account_balance(account_id, token)
        return balance
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get account balance: {str(e)}")

@app.post("/tools/get_transaction_history")
async def get_transaction_history(request: Dict[str, Any]):
    """Get transaction history"""
    try:
        account_id = request.get("account_id")
        token = request.get("token")
        limit = request.get("limit", 100)
        
        if not account_id or not token:
            raise HTTPException(status_code=400, detail="account_id and token are required")
        
        transactions = await bank_client.get_transaction_history(account_id, token, limit)
        return {"transactions": transactions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get transaction history: {str(e)}")

@app.post("/tools/get_user_contacts")
async def get_user_contacts(request: Dict[str, Any]):
    """Get user contacts"""
    try:
        username = request.get("username")
        token = request.get("token")
        
        if not username or not token:
            raise HTTPException(status_code=400, detail="username and token are required")
        
        contacts = await bank_client.get_user_contacts(username, token)
        return {"contacts": contacts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user contacts: {str(e)}")

@app.post("/tools/analyze_spending")
async def analyze_spending(request: Dict[str, Any]):
    """Analyze user spending patterns for budgeting"""
    try:
        account_id = request.get("account_id")
        token = request.get("token")
        days = request.get("days", 90)
        
        if not account_id or not token:
            raise HTTPException(status_code=400, detail="account_id and token are required")
        
        analysis = await bank_client.analyze_spending_patterns(account_id, token, days)
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze spending: {str(e)}")

@app.post("/tools/get_financial_snapshot")
async def get_financial_snapshot(request: Dict[str, Any]):
    """Get complete financial snapshot for AI agents"""
    try:
        token = request.get("token")
        
        if not token:
            raise HTTPException(status_code=400, detail="token is required")
        
        # Get user profile first to extract account info
        profile = await bank_client.get_user_profile(token)
        account_id = profile.get("accountid")
        username = profile.get("username")
        
        if not account_id:
            raise HTTPException(status_code=400, detail="Could not extract account_id from token")
        
        # Get comprehensive financial data
        balance = await bank_client.get_account_balance(account_id, token)
        transactions = await bank_client.get_transaction_history(account_id, token, 50)
        spending_analysis = await bank_client.analyze_spending_patterns(account_id, token, 90)
        contacts = await bank_client.get_user_contacts(username, token) if username else []
        
        snapshot = {
            "profile": profile,
            "balance": balance,
            "recent_transactions": transactions[:10] if transactions else [],
            "spending_analysis": spending_analysis,
            "contacts": contacts,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "account_id": account_id,
                "username": username,
                "current_balance_dollars": balance.get("balance_dollars", 0),
                "transaction_count": len(transactions),
                "contact_count": len(contacts)
            }
        }
        
        return snapshot
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get financial snapshot: {str(e)}")

# Demo endpoint for testing with default credentials
@app.post("/tools/demo_auth")
async def demo_auth(request: Dict[str, Any] = None):
    """Demo authentication with default Bank of Anthos credentials"""
    try:
        # Use demo credentials from Bank of Anthos config
        username = "testuser"
        password = "bankofanthos"  # From demo-data-config
        
        result = await bank_client.authenticate_user(username, password)
        return {
            "demo": True,
            "credentials_used": {"username": username, "password": "[hidden]"},
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed demo authentication: {str(e)}")

@app.get("/tools/list")
async def list_available_tools():
    """List all available MCP tools"""
    return {
        "tools": [
            {
                "name": "authenticate",
                "description": "Authenticate user with Bank of Anthos",
                "parameters": ["username", "password"]
            },
            {
                "name": "demo_auth", 
                "description": "Demo authentication with default credentials",
                "parameters": []
            },
            {
                "name": "get_user_profile",
                "description": "Get user profile from JWT token",
                "parameters": ["token"]
            },
            {
                "name": "get_account_balance",
                "description": "Get current account balance",
                "parameters": ["account_id", "token"]
            },
            {
                "name": "get_transaction_history",
                "description": "Get transaction history for account",
                "parameters": ["account_id", "token", "limit?"]
            },
            {
                "name": "get_user_contacts",
                "description": "Get user's contact list",
                "parameters": ["username", "token"]
            },
            {
                "name": "analyze_spending",
                "description": "Analyze spending patterns for budgeting",
                "parameters": ["account_id", "token", "days?"]
            },
            {
                "name": "get_financial_snapshot",
                "description": "Get complete financial snapshot for AI analysis",
                "parameters": ["token"]
            }
        ],
        "demo_credentials": {
            "username": "testuser",
            "password": "bankofanthos"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
