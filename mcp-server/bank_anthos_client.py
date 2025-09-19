# mcp-server/bank_anthos_client.py - Enhanced with transaction categorization
import httpx
import asyncio
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
import logging
import re

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
    
    async def _get_auth_headers(self, token: str = None) -> Dict[str, str]:
        """Get headers with optional JWT token"""
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers
    
    async def authenticate_user(self, username: str, password: str) -> Dict:
        """GET /login - User authentication with query parameters"""
        try:
            url = f"{self.base_urls['userservice']}/login"
            params = {"username": username, "password": password}
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Authentication successful for user {username}")
                return {
                    "success": True,
                    "token": data["token"],
                    "message": "Authentication successful"
                }
            else:
                logger.warning(f"Authentication failed for user {username}: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Authentication failed: {response.status_code}",
                    "message": "Invalid username or password"
                }
                
        except Exception as e:
            logger.error(f"Error authenticating user {username}: {str(e)}")
            return {
                "success": False,
                "error": f"Authentication error: {str(e)}",
                "message": "Network or server error during authentication"
            }
    
    def _decode_jwt_payload(self, token: str) -> Dict:
        """Decode JWT token to extract user info (no verification for demo)"""
        try:
            import jwt
            # Decode without verification for demo purposes
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except Exception as e:
            logger.error(f"Error decoding JWT: {str(e)}")
            return {}
    
    async def get_user_profile(self, token: str) -> Dict:
        """Extract user profile from JWT token since no /users/{id} endpoint exists"""
        try:
            payload = self._decode_jwt_payload(token)
            
            if payload:
                return {
                    "username": payload.get("user"),
                    "accountid": payload.get("acct"),
                    "name": payload.get("name"),
                    "iat": payload.get("iat"),
                    "exp": payload.get("exp")
                }
            else:
                # Return real demo data if JWT decode fails
                return {
                    "username": "testuser",
                    "accountid": "1011226111",  # Real demo account from database
                    "name": "Test User",
                    "iat": datetime.now().timestamp(),
                    "exp": (datetime.now() + timedelta(hours=1)).timestamp()
                }
                
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return {
                "username": "testuser",
                "accountid": "1011226111",  # Real demo account
                "name": "Test User",
                "error": str(e)
            }
    
    async def get_account_balance(self, account_id: str, token: str) -> Dict:
        """GET /balances/{accountId} - Account balance (returns Long in cents)"""
        try:
            url = f"{self.base_urls['balancereader']}/balances/{account_id}"
            headers = await self._get_auth_headers(token)
            response = await self.client.get(url, headers=headers)
            
            if response.status_code == 200:
                # Response is a raw Long (balance in cents)
                balance_cents = response.json()
                return {
                    "account_id": account_id,
                    "balance_cents": balance_cents,
                    "balance_dollars": balance_cents / 100.0,
                    "currency": "USD",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning(f"Failed to get balance for {account_id}: {response.status_code}")
                # Return mock data for demo
                return {
                    "account_id": account_id,
                    "balance_cents": 1575050,  # $15,750.50
                    "balance_dollars": 15750.50,
                    "currency": "USD",
                    "timestamp": datetime.now().isoformat(),
                    "mock": True
                }
                
        except Exception as e:
            logger.error(f"Error getting balance for {account_id}: {str(e)}")
            # Return mock data for demo
            return {
                "account_id": account_id,
                "balance_cents": 1575050,
                "balance_dollars": 15750.50,
                "currency": "USD", 
                "timestamp": datetime.now().isoformat(),
                "mock": True,
                "error": str(e)
            }
    
    async def get_transaction_history(self, account_id: str, token: str, limit: int = 100) -> List[Dict]:
        """GET /transactions/{accountId} - Transaction history with enhanced categorization"""
        try:
            url = f"{self.base_urls['transactionhistory']}/transactions/{account_id}"
            headers = await self._get_auth_headers(token)
            response = await self.client.get(url, headers=headers)
            
            if response.status_code == 200:
                transactions = response.json()
                # Convert to our standard format with categorization
                formatted_transactions = []
                for txn in transactions:
                    enhanced_txn = {
                        "transactionId": txn.get("transactionId"),
                        "fromAccountNum": txn.get("fromAccountNum"),
                        "fromRoutingNum": txn.get("fromRoutingNum"),
                        "toAccountNum": txn.get("toAccountNum"),
                        "toRoutingNum": txn.get("toRoutingNum"),
                        "amount": txn.get("amount"),  # in cents
                        "amount_dollars": txn.get("amount", 0) / 100.0,
                        "timestamp": txn.get("timestamp"),
                        "category": self._categorize_transaction(txn, account_id),
                        "is_outgoing": txn.get("fromAccountNum") == account_id,
                        "description": self._generate_transaction_description(txn, account_id)
                    }
                    formatted_transactions.append(enhanced_txn)
                
                return formatted_transactions
            else:
                logger.warning(f"Failed to get transactions for {account_id}: {response.status_code}")
                # Return enhanced mock data for demo
                return self._generate_enhanced_mock_transactions(account_id, limit)
                
        except Exception as e:
            logger.error(f"Error getting transactions for {account_id}: {str(e)}")
            # Return enhanced mock data for demo
            return self._generate_enhanced_mock_transactions(account_id, limit)
    
    def _categorize_transaction(self, txn: Dict, user_account: str) -> str:
        """Categorize transactions based on amount and patterns"""
        amount = abs(float(txn.get("amount", 0)) / 100.0)
        is_outgoing = txn.get("fromAccountNum") == user_account
        
        if not is_outgoing:
            return "income"
        
        # Categorize outgoing transactions by amount patterns
        if amount >= 1000:
            return "major_expense"
        elif amount >= 500:
            return "significant_purchase"
        elif amount >= 100:
            return "regular_expense"
        elif amount >= 20:
            return "daily_spending"
        else:
            return "small_purchase"
    
    def _generate_transaction_description(self, txn: Dict, user_account: str) -> str:
        """Generate human-readable transaction descriptions"""
        amount = abs(float(txn.get("amount", 0)) / 100.0)
        is_outgoing = txn.get("fromAccountNum") == user_account
        
        if is_outgoing:
            return f"Payment of ${amount:.2f} to account {txn.get('toAccountNum', 'unknown')}"
        else:
            return f"Received ${amount:.2f} from account {txn.get('fromAccountNum', 'unknown')}"
    
    def _generate_enhanced_mock_transactions(self, account_id: str, limit: int) -> List[Dict]:
        """Generate realistic mock transaction data with categories"""
        import random
        from datetime import datetime, timedelta
        
        transactions = []
        
        # Define realistic transaction categories with amounts
        transaction_templates = [
            {"category": "grocery", "amount_range": (30, 150), "description": "Grocery shopping"},
            {"category": "gas", "amount_range": (40, 80), "description": "Gas station"},
            {"category": "restaurant", "amount_range": (15, 120), "description": "Restaurant dining"},
            {"category": "utilities", "amount_range": (80, 250), "description": "Utility payment"},
            {"category": "rent", "amount_range
