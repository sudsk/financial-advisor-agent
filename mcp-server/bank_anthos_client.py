# mcp-server/bank_anthos_client.py
import httpx
import asyncio
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BankOfAnthosClient:
    def __init__(self):
        self.base_urls = {
            "userservice": "http://userservice.default.svc.cluster.local:8080",
            "balancereader": "http://balancereader.default.svc.cluster.local:8080", 
            "transactionhistory": "http://transactionhistory.default.svc.cluster.local:8080",
            "contacts": "http://contacts.default.svc.cluster.local:8080"
        }
        self.client = None
        self.timeout = 10.0
    
    async def initialize(self):
        """Initialize the HTTP client"""
        self.client = httpx.AsyncClient(timeout=self.timeout)
        logger.info("Bank of Anthos client initialized")
    
    async def authenticate_user(self, username: str, password: str) -> Dict:
        """POST /login - User authentication"""
        try:
            url = f"{self.base_urls['userservice']}/login"
            payload = {"username": username, "password": password}
            response = await self.client.post(url, json=payload)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Authentication failed for user {username}: {response.status_code}")
                return {"error": f"Authentication failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {str(e)}")
            return {"error": f"Authentication error: {str(e)}"}
    
    async def get_user_profile(self, user_id: str) -> Dict:
        """GET /users/{user_id} - User profile"""
        try:
            url = f"{self.base_urls['userservice']}/users/{user_id}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get user profile for {user_id}: {response.status_code}")
                # Return mock data for demo purposes
                return {
                    "user_id": user_id,
                    "account_id": "1234567890",
                    "name": "Test User",
                    "email": "testuser@example.com",
                    "account_type": "checking"
                }
                
        except Exception as e:
            logger.error(f"Error getting user profile for {user_id}: {str(e)}")
            # Return mock data for demo
            return {
                "user_id": user_id,
                "account_id": "1234567890", 
                "name": "Test User",
                "email": "testuser@example.com",
                "account_type": "checking"
            }
    
    async def get_account_balance(self, account_id: str) -> Dict:
        """GET /balances/{account_id} - Account balance"""
        try:
            url = f"{self.base_urls['balancereader']}/balances/{account_id}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get balance for {account_id}: {response.status_code}")
                # Return mock data for demo
                return {
                    "account_id": account_id,
                    "amount": 15750.50,
                    "currency": "USD",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting balance for {account_id}: {str(e)}")
            # Return mock data for demo
            return {
                "account_id": account_id,
                "amount": 15750.50,
                "currency": "USD", 
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_transaction_history(self, account_id: str, days: int = 30) -> List[Dict]:
        """GET /transactions/{account_id} - Transaction history"""
        try:
            url = f"{self.base_urls['transactionhistory']}/transactions/{account_id}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get transactions for {account_id}: {response.status_code}")
                # Return mock data for demo
                return self._generate_mock_transactions(account_id, days)
                
        except Exception as e:
            logger.error(f"Error getting transactions for {account_id}: {str(e)}")
            # Return mock data for demo
            return self._generate_mock_transactions(account_id, days)
    
    def _generate_mock_transactions(self, account_id: str, days: int) -> List[Dict]:
        """Generate mock transaction data for demo purposes"""
        import random
        from datetime import datetime, timedelta
        
        transactions = []
        categories = ["Groceries", "Dining", "Gas", "Entertainment", "Shopping", "Utilities", "Rent"]
        
        for i in range(min(days * 2, 60)):  # Generate 2 transactions per day, max 60
            date = datetime.now() - timedelta(days=random.randint(0, days))
            amount = random.uniform(-200, -5) if random.random() > 0.1 else random.uniform(1000, 3000)  # Mostly expenses
            
            transactions.append({
                "transaction_id": f"txn_{account_id}_{i}",
                "account_id": account_id,
                "amount": round(amount, 2),
                "category": random.choice(categories),
                "description": f"Transaction at {random.choice(['Store A', 'Restaurant B', 'Gas Station C'])}",
                "timestamp": date.isoformat(),
                "location": random.choice(["New York", "San Francisco", "Los Angeles"])
            })
        
        return sorted(transactions, key=lambda x: x["timestamp"], reverse=True)
    
    async def get_user_contacts(self, user_id: str) -> List[Dict]:
        """GET /contacts/{user_id} - User contacts"""
        try:
            url = f"{self.base_urls['contacts']}/contacts/{user_id}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get contacts for {user_id}: {response.status_code}")
                # Return mock data for demo
                return [
                    {"name": "John Doe", "account": "987654321", "relationship": "friend"},
                    {"name": "Jane Smith", "account": "555666777", "relationship": "family"}
                ]
                
        except Exception as e:
            logger.error(f"Error getting contacts for {user_id}: {str(e)}")
            # Return mock data for demo
            return [
                {"name": "John Doe", "account": "987654321", "relationship": "friend"},
                {"name": "Jane Smith", "account": "555666777", "relationship": "family"}
            ]
    
    async def analyze_spending_patterns(self, account_id: str, days: int = 90) -> Dict:
        """Analyze spending patterns for budget agent"""
        try:
            transactions = await self.get_transaction_history(account_id, days)
            
            # Process transactions into spending categories
            categories = {}
            total_spending = 0
            
            for transaction in transactions:
                amount = transaction.get("amount", 0)
                if amount < 0:  # Outgoing transaction
                    amount = abs(amount)
                    category = transaction.get("category", "Other")
                    
                    if category not in categories:
                        categories[category] = 0
                    categories[category] += amount
                    total_spending += amount
            
            return {
                "total_spending": total_spending,
                "categories": categories,
                "average_monthly": total_spending / (days / 30) if days > 0 else 0,
                "transaction_count": len(transactions),
                "analysis_period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error analyzing spending for {account_id}: {str(e)}")
            return {
                "total_spending": 0,
                "categories": {},
                "average_monthly": 0,
                "transaction_count": 0,
                "error": str(e)
            }
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()
            logger.info("Bank of Anthos client closed")
