# mcp-server/server.py - Clean version with real Bank of Anthos data only
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import httpx
from typing import Dict, Any, List, Optional
from bank_anthos_client import BankOfAnthosClient
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Bank of Anthos MCP Server - Real Data Only")

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
    logger.info("🏦 MCP Server started - Real Bank of Anthos data mode only")

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
        "mode": "real_data_only",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0-real-data"
    }

@app.post("/tools/authenticate")
async def authenticate_user(request: Dict[str, Any]):
    """Authenticate user and get JWT token - Real API only"""
    try:
        username = request.get("username")
        password = request.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="username and password are required")
        
        # Only real authentication, no fallbacks
        result = await bank_client.authenticate_user(username, password)
        logger.info(f"✅ Real authentication result for {username}: {result['success']}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Authentication failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Real authentication failed: {str(e)}")

@app.post("/tools/get_user_profile")
async def get_user_profile(request: Dict[str, Any]):
    """Get user profile from JWT token - Real data only"""
    try:
        token = request.get("token")
        
        if not token:
            raise HTTPException(status_code=400, detail="token is required")
        
        # Only real profile extraction, no fallbacks
        profile = await bank_client.get_user_profile(token)
        logger.info(f"✅ Real profile retrieved for user: {profile.get('username')}")
        return {"profile": profile}
        
    except Exception as e:
        logger.error(f"❌ Profile retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Real profile retrieval failed: {str(e)}")

@app.post("/tools/get_account_balance")
async def get_account_balance(request: Dict[str, Any]):
    """Get account balance - Real API only"""
    try:
        account_id = request.get("account_id")
        token = request.get("token")
        
        if not account_id or not token:
            raise HTTPException(status_code=400, detail="account_id and token are required")
        
        # Only real balance, no fallbacks
        balance = await bank_client.get_account_balance(account_id, token)
        logger.info(f"✅ Real balance retrieved: ${balance['balance_dollars']:.2f} for account {account_id}")
        return balance
        
    except Exception as e:
        logger.error(f"❌ Balance retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Real balance retrieval failed: {str(e)}")

@app.post("/tools/get_transaction_history")
async def get_transaction_history(request: Dict[str, Any]):
    """Get transaction history - Real API only"""
    try:
        account_id = request.get("account_id")
        token = request.get("token")
        limit = request.get("limit", 100)
        
        if not account_id or not token:
            raise HTTPException(status_code=400, detail="account_id and token are required")
        
        # Only real transactions, no fallbacks
        transactions = await bank_client.get_transaction_history(account_id, token, limit)
        logger.info(f"✅ Retrieved {len(transactions)} real transactions for account {account_id}")
        return {"transactions": transactions}
        
    except Exception as e:
        logger.error(f"❌ Transaction retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Real transaction retrieval failed: {str(e)}")

@app.post("/tools/get_user_contacts")
async def get_user_contacts(request: Dict[str, Any]):
    """Get user contacts - Real API only"""
    try:
        username = request.get("username")
        token = request.get("token")
        
        if not username or not token:
            raise HTTPException(status_code=400, detail="username and token are required")
        
        # Only real contacts, no fallbacks
        contacts = await bank_client.get_user_contacts(username, token)
        logger.info(f"✅ Retrieved {len(contacts)} real contacts for user {username}")
        return {"contacts": contacts}
        
    except Exception as e:
        logger.error(f"❌ Contacts retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Real contacts retrieval failed: {str(e)}")

@app.post("/tools/analyze_spending")
async def analyze_spending(request: Dict[str, Any]):
    """Analyze user spending patterns - Real data only"""
    try:
        account_id = request.get("account_id")
        token = request.get("token")
        days = request.get("days", 90)
        
        if not account_id or not token:
            raise HTTPException(status_code=400, detail="account_id and token are required")
        
        # Only real spending analysis, no fallbacks
        analysis = await bank_client.analyze_spending_patterns(account_id, token, days)
        logger.info(f"✅ Real spending analysis completed: {analysis['transaction_count']} transactions analyzed")
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Spending analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Real spending analysis failed: {str(e)}")

@app.post("/tools/get_financial_snapshot")
async def get_financial_snapshot(request: Dict[str, Any]):
    """Get complete financial snapshot - Real data only"""
    try:
        token = request.get("token")
        
        if not token:
            raise HTTPException(status_code=400, detail="token is required")
        
        # Get real user profile first
        profile = await bank_client.get_user_profile(token)
        account_id = profile.get("accountid")
        username = profile.get("username")
        
        if not account_id:
            raise HTTPException(status_code=400, detail="Could not extract account_id from token")
        
        logger.info(f"🔍 Getting comprehensive real financial data for {username} (Account: {account_id})")
        
        # Get all real financial data - no fallbacks
        balance = await bank_client.get_account_balance(account_id, token)
        transactions = await bank_client.get_transaction_history(account_id, token, 50)
        spending_analysis = await bank_client.analyze_spending_patterns(account_id, token, 90)
        contacts = await bank_client.get_user_contacts(username, token) if username else []
        
        # Build comprehensive real data snapshot
        snapshot = {
            "profile": profile,
            "balance": balance,
            "recent_transactions": transactions[:10],  # Most recent 10
            "spending_analysis": spending_analysis,
            "contacts": contacts,
            "timestamp": datetime.now().isoformat(),
            "data_source": "Bank of Anthos real-time API integration",
            "summary": {
                "account_id": account_id,
                "username": username,
                "current_balance_dollars": balance.get("balance_dollars", 0),
                "total_transactions_analyzed": len(transactions),
                "spending_categories": len(spending_analysis.get("categories", {})),
                "contact_count": len(contacts),
                "net_monthly_flow": spending_analysis.get("net_flow_dollars", 0) / 3
            }
        }
        
        logger.info(f"✅ Complete real financial snapshot prepared: ${balance.get('balance_dollars', 0):.2f} balance, {len(transactions)} transactions")
        return snapshot
        
    except Exception as e:
        logger.error(f"❌ Financial snapshot failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Real financial snapshot failed: {str(e)}")

@app.post("/tools/demo_auth")
async def demo_auth(request: Dict[str, Any] = None):
    """Demo authentication with Bank of Anthos credentials - Real API only"""
    try:
        # Use real Bank of Anthos demo credentials
        username = "testuser"
        password = "bankofanthos"  # Real demo password from Bank of Anthos
        
        logger.info(f"🔐 Attempting real demo authentication for {username}")
        
        # Only real authentication, no fallbacks
        result = await bank_client.authenticate_user(username, password)
        
        response = {
            "demo": True,
            "credentials_used": {"username": username, "password": "[hidden]"},
            "result": result,
            "data_source": "Real Bank of Anthos authentication API"
        }
        
        logger.info(f"✅ Real demo authentication completed: {result['success']}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Demo authentication failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Real demo authentication failed: {str(e)}")

@app.get("/tools/list")
async def list_available_tools():
    """List all available MCP tools - Real data only"""
    return {
        "tools": [
            {
                "name": "authenticate",
                "description": "Authenticate user with real Bank of Anthos API",
                "parameters": ["username", "password"],
                "data_source": "real"
            },
            {
                "name": "demo_auth", 
                "description": "Demo authentication with real Bank of Anthos credentials",
                "parameters": [],
                "data_source": "real"
            },
            {
                "name": "get_user_profile",
                "description": "Get real user profile from JWT token",
                "parameters": ["token"],
                "data_source": "real"
            },
            {
                "name": "get_account_balance",
                "description": "Get real current account balance",
                "parameters": ["account_id", "token"],
                "data_source": "real"
            },
            {
                "name": "get_transaction_history",
                "description": "Get real transaction history for account",
                "parameters": ["account_id", "token", "limit?"],
                "data_source": "real"
            },
            {
                "name": "get_user_contacts",
                "description": "Get real user's contact list",
                "parameters": ["username", "token"],
                "data_source": "real"
            },
            {
                "name": "analyze_spending",
                "description": "Analyze real spending patterns for budgeting",
                "parameters": ["account_id", "token", "days?"],
                "data_source": "real"
            },
            {
                "name": "get_financial_snapshot",
                "description": "Get complete real financial snapshot for AI analysis",
                "parameters": ["token"],
                "data_source": "real"
            }
        ],
        "demo_credentials": {
            "username": "testuser",
            "password": "bankofanthos"
        },
        "note": "All tools use real Bank of Anthos API data only - no mock/fallback data"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
