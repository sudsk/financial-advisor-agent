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
        """GET /transactions/{accountId} - Transaction history"""
        try:
            url = f"{self.base_urls['transactionhistory']}/transactions/{account_id}"
            headers = await self._get_auth_headers(token)
            response = await self.client.get(url, headers=headers)
            
            if response.status_code == 200:
                transactions = response.json()
                # Convert to our standard format
                formatted_transactions = []
                for txn in transactions:
                    formatted_transactions.append({
                        "transactionId": txn.get("transactionId"),
                        "fromAccountNum": txn.get("fromAccountNum"),
                        "fromRoutingNum": txn.get("fromRoutingNum"),
                        "toAccountNum": txn.get("toAccountNum"),
                        "toRoutingNum": txn.get("toRoutingNum"),
                        "amount": txn.get("amount"),  # in cents
                        "amount_dollars": txn.get("amount", 0) / 100.0,
                        "timestamp": txn.get("timestamp")
                    })
                return formatted_transactions
            else:
                logger.warning(f"Failed to get transactions for {account_id}: {response.status_code}")
                # Return mock data for demo
                return self._generate_mock_transactions(account_id, limit)
                
        except Exception as e:
            logger.error(f"Error getting transactions for {account_id}: {str(e)}")
            # Return mock data for demo
            return self._generate_mock_transactions(account_id, limit)
    
    def _generate_mock_transactions(self, account_id: str, limit: int) -> List[Dict]:
        """Generate mock transaction data matching Bank of Anthos format"""
        import random
        from datetime import datetime, timedelta
        
        transactions = []
        
        # Real demo accounts from Bank of Anthos database
        demo_accounts = ["1033623433", "1055757655", "1077441377"]  # alice, bob, eve
        
        for i in range(min(limit, 20)):  # Generate up to 20 mock transactions
            date = datetime.now() - timedelta(days=random.randint(0, 30))
            amount = random.randint(500, 10000)  # Amount in cents
            is_outgoing = random.random() > 0.5
            
            if is_outgoing:
                from_account = account_id
                to_account = demo_accounts[random.randint(0, len(demo_accounts)-1)]
            else:
                from_account = demo_accounts[random.randint(0, len(demo_accounts)-1)]
                to_account = account_id
            
            transactions.append({
                "transactionId": i + 1,
                "fromAccountNum": from_account,
                "fromRoutingNum": "883745000",
                "toAccountNum": to_account,
                "toRoutingNum": "883745000",
                "amount": amount,
                "amount_dollars": amount / 100.0,
                "timestamp": date.isoformat() + "Z"
            })
        
        return sorted(transactions, key=lambda x: x["timestamp"], reverse=True)
    
    async def get_user_contacts(self, username: str, token: str) -> List[Dict]:
        """GET /contacts/{username} - User contacts"""
        try:
            url = f"{self.base_urls['contacts']}/contacts/{username}"
            headers = await self._get_auth_headers(token)
            response = await self.client.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get contacts for {username}: {response.status_code}")
                # Return mock data for demo with real account IDs
                return [
                    {"label": "Alice", "account_num": "1033623433", "routing_num": "883745000", "is_external": False},
                    {"label": "Bob", "account_num": "1055757655", "routing_num": "883745000", "is_external": False},
                    {"label": "Eve", "account_num": "1077441377", "routing_num": "883745000", "is_external": False},
                    {"label": "External Bank", "account_num": "9099791699", "routing_num": "808889588", "is_external": True}
                ]
                
        except Exception as e:
            logger.error(f"Error getting contacts for {username}: {str(e)}")
            # Return mock data for demo with real account IDs
            return [
                {"label": "Alice", "account_num": "1033623433", "routing_num": "883745000", "is_external": False},
                {"label": "Bob", "account_num": "1055757655", "routing_num": "883745000", "is_external": False},
                {"label": "Eve", "account_num": "1077441377", "routing_num": "883745000", "is_external": False}
            ]
    
    async def analyze_spending_patterns(self, account_id: str, token: str, days: int = 90) -> Dict:
        """Analyze spending patterns for budget agent"""
        try:
            transactions = await self.get_transaction_history(account_id, token, 100)
            
            # Process transactions into spending categories
            total_outgoing = 0
            total_incoming = 0
            transaction_count = 0
            
            for transaction in transactions:
                transaction_count += 1
                amount = transaction.get("amount", 0)
                
                # Check if this is an outgoing transaction (from this account)
                if transaction.get("fromAccountNum") == account_id:
                    total_outgoing += amount
                else:
                    total_incoming += amount
            
            return {
                "account_id": account_id,
                "analysis_period_days": days,
                "total_outgoing_cents": total_outgoing,
                "total_incoming_cents": total_incoming,
                "total_outgoing_dollars": total_outgoing / 100.0,
                "total_incoming_dollars": total_incoming / 100.0,
                "net_flow_cents": total_incoming - total_outgoing,
                "net_flow_dollars": (total_incoming - total_outgoing) / 100.0,
                "transaction_count": transaction_count,
                "average_transaction_amount": (total_outgoing + total_incoming) / (2 * transaction_count) if transaction_count > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing spending for {account_id}: {str(e)}")
            return {
                "account_id": account_id,
                "analysis_period_days": days,
                "total_outgoing_cents": 0,
                "total_incoming_cents": 0,
                "transaction_count": 0,
                "error": str(e)
            }
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()
            logger.info("Bank of Anthos client closed")
