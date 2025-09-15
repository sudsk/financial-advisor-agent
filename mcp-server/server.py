# mcp-server/server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import httpx
from typing import Dict, Any, List
from bank_anthos_client import BankOfAnthosClient
import os
from datetime import datetime

# Initialize FastAPI app (using FastAPI instead of MCP for simplicity)
app = FastAPI(title="Financial Advisor MCP Server")

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
        "service": "mcp-server",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/tools/get_user_data")
async def get_user_data(request: Dict[str, Any]):
    """Get comprehensive user financial data"""
    try:
        user_id = request.get("user_id")
        include_transactions = request.get("include_transactions", True)
        transaction_days = request.get("transaction_days", 30)
        
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")
        
        # Get user profile
        profile = await bank_client.get_user_profile(user_id)
        
        result = {"profile": profile}
        
        if include_transactions and profile.get("account_id"):
            transactions = await bank_client.get_transaction_history(
                profile["account_id"]
            )
            result["transactions"] = transactions
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user data: {str(e)}")

@app.post("/tools/analyze_spending")
async def analyze_spending(request: Dict[str, Any]):
    """Analyze user spending patterns for budgeting"""
    try:
        account_id = request.get("account_id")
        analysis_days = request.get("analysis_days", 90)
        
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        analysis = await bank_client.analyze_spending_patterns(account_id, analysis_days)
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze spending: {str(e)}")

@app.post("/tools/get_financial_snapshot")
async def get_financial_snapshot(request: Dict[str, Any]):
    """Get complete financial snapshot for investment analysis"""
    try:
        user_id = request.get("user_id")
        account_id = request.get("account_id")
        
        if not user_id or not account_id:
            raise HTTPException(status_code=400, detail="user_id and account_id are required")
        
        # Get comprehensive financial data
        profile = await bank_client.get_user_profile(user_id)
        balance = await bank_client.get_account_balance(account_id)
        transactions = await bank_client.get_transaction_history(account_id)
        spending_analysis = await bank_client.analyze_spending_patterns(account_id, 90)
        contacts = await bank_client.get_user_contacts(user_id)
        
        snapshot = {
            "profile": profile,
            "balance": balance,
            "recent_transactions": transactions[:10] if transactions else [],
            "spending_analysis": spending_analysis,
            "contacts": contacts,
            "timestamp": datetime.now().isoformat()
        }
        
        return snapshot
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get financial snapshot: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
