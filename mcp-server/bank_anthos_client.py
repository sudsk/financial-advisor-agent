# mcp-server/bank_anthos_client.py
import httpx
import asyncio
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta

class BankOfAnthosClient:
    def __init__(self, base_url: str = "http://bank-of-anthos-frontend:80"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def get_user_profile(self, user_id: str) -> Dict:
        """Get user profile from userservice"""
        try:
            response = await self.client.get(f"{self.base_url}/api/user/{user_id}")
            return response.json()
        except Exception as e:
            return {"error": f"Failed to get user profile: {str(e)}"}
    
    async def get_account_balance(self, account_id: str) -> Dict:
        """Get account balance from balancereader"""
        try:
            response = await self.client.get(f"{self.base_url}/api/balance/{account_id}")
            return response.json()
        except Exception as e:
            return {"error": f"Failed to get balance: {str(e)}"}
    
    async def get_transaction_history(self, account_id: str, days: int = 30) -> List[Dict]:
        """Get transaction history from ledgerwriter"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            response = await self.client.get(
                f"{self.base_url}/api/transactions/{account_id}",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
            return response.json()
        except Exception as e:
            return [{"error": f"Failed to get transactions: {str(e)}"}]
    
    async def get_user_contacts(self, user_id: str) -> List[Dict]:
        """Get user contacts from contacts service"""
        try:
            response = await self.client.get(f"{self.base_url}/api/contacts/{user_id}")
            return response.json()
        except Exception as e:
            return [{"error": f"Failed to get contacts: {str(e)}"}]
    
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
