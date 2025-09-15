# mcp-server/bank_anthos_client.py
import httpx
import asyncio
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta

class BankOfAnthosClient:
    def __init__(self):
        self.base_urls = {
            "userservice": "http://userservice.default.svc.cluster.local:8080",
            "balancereader": "http://balancereader.default.svc.cluster.local:8080",
            "transactionhistory": "http://transactionhistory.default.svc.cluster.local:8080",
            "contacts": "http://contacts.default.svc.cluster.local:8080"
        }
    
    async def authenticate_user(self, username: str, password: str):
        """POST /login - User authentication"""
        url = f"{self.base_urls['userservice']}/login"
        payload = {"username": username, "password": password}
        response = await self.client.post(url, json=payload)
        return response.json()
    
    async def get_user_profile(self, user_id: str):
        """GET /users/{user_id} - User profile"""
        url = f"{self.base_urls['userservice']}/users/{user_id}"
        response = await self.client.get(url)
        return response.json()
    
    async def get_account_balance(self, account_id: str):
        """GET /balances/{account_id} - Account balance"""  
        url = f"{self.base_urls['balancereader']}/balances/{account_id}"
        response = await self.client.get(url)
        return response.json()
        
    async def get_transaction_history(self, account_id: str):
        """GET /transactions/{account_id} - Transaction history"""
        url = f"{self.base_urls['transactionhistory']}/transactions/{account_id}"
        response = await self.client.get(url)
        return response.json()
        
    async def get_user_contacts(self, user_id: str):
        """GET /contacts/{user_id} - User contacts"""
        url = f"{self.base_urls['contacts']}/contacts/{user_id}"
        response = await self.client.get(url)
        return response.json()
    
    async def analyze_spending_patterns(self, account_id: str, days: int = 90) -> Dict:
        """Analyze spending patterns for budget agent"""
        transactions = await self.get_transaction_history(account_id, days)
        
        # Process transactions into spending categories
        categories = {}
        total_spending = 0
        monthly_spending = []
        
        for transaction in transactions:
            if transaction.get("amount", 0) < 0:  # Outgoing transaction
                amount = abs(transaction["amount"])
                category = transaction.get("category", "Other")
                
                if category not in categories:
                    categories[category] = 0
                categories[category] += amount
                total_spending += amount
        
        return {
            "total_spending": total_spending,
            "categories": categories,
            "average_monthly": total_spending / (days / 30),
            "transaction_count": len(transactions)
        }
    
    async def close(self):
        await self.client.aclose()
