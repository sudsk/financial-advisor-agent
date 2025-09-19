# mcp-server/bank_anthos_client.py - Real Bank of Anthos data only, no mock data
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
        self.timeout = 15.0  # Increased timeout for real API calls
    
    async def initialize(self):
        """Initialize the HTTP client"""
        self.client = httpx.AsyncClient(timeout=self.timeout)
        logger.info("Bank of Anthos client initialized - real data mode")
    
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
                logger.info(f"✅ Real authentication successful for user {username}")
                return {
                    "success": True,
                    "token": data["token"],
                    "message": "Authentication successful"
                }
            else:
                logger.error(f"❌ Authentication failed for user {username}: {response.status_code}")
                raise Exception(f"Authentication failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Authentication error for user {username}: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")
    
    def _decode_jwt_payload(self, token: str) -> Dict:
        """Decode JWT token to extract user info"""
        try:
            import jwt
            # Decode without verification for demo purposes
            payload = jwt.decode(token, options={"verify_signature": False})
            logger.info(f"✅ JWT decoded successfully for user {payload.get('user', 'unknown')}")
            return payload
        except Exception as e:
            logger.error(f"❌ JWT decode error: {str(e)}")
            raise Exception(f"Failed to decode JWT token: {str(e)}")
    
    async def get_user_profile(self, token: str) -> Dict:
        """Extract user profile from JWT token"""
        try:
            payload = self._decode_jwt_payload(token)
            
            profile = {
                "username": payload.get("user"),
                "accountid": payload.get("acct"),
                "name": payload.get("name"),
                "iat": payload.get("iat"),
                "exp": payload.get("exp")
            }
            
            logger.info(f"✅ User profile extracted: {profile['username']} (Account: {profile['accountid']})")
            return profile
                
        except Exception as e:
            logger.error(f"❌ Error getting user profile: {str(e)}")
            raise Exception(f"Failed to get user profile: {str(e)}")
    
    async def get_account_balance(self, account_id: str, token: str) -> Dict:
        """GET /balances/{accountId} - Account balance (returns Long in cents)"""
        try:
            url = f"{self.base_urls['balancereader']}/balances/{account_id}"
            headers = await self._get_auth_headers(token)
            response = await self.client.get(url, headers=headers)
            
            if response.status_code == 200:
                balance_cents = response.json()
                balance_data = {
                    "account_id": account_id,
                    "balance_cents": balance_cents,
                    "balance_dollars": balance_cents / 100.0,
                    "currency": "USD",
                    "timestamp": datetime.now().isoformat(),
                    "data_source": "Bank of Anthos API"
                }
                logger.info(f"✅ Real balance retrieved: ${balance_data['balance_dollars']:.2f} for account {account_id}")
                return balance_data
            else:
                logger.error(f"❌ Failed to get balance for {account_id}: HTTP {response.status_code}")
                raise Exception(f"Balance API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error getting balance for {account_id}: {str(e)}")
            raise Exception(f"Failed to get account balance: {str(e)}")
    
    async def get_transaction_history(self, account_id: str, token: str, limit: int = 100) -> List[Dict]:
        """GET /transactions/{accountId} - Real transaction history with enhanced categorization"""
        try:
            url = f"{self.base_urls['transactionhistory']}/transactions/{account_id}"
            headers = await self._get_auth_headers(token)
            response = await self.client.get(url, headers=headers)
            
            if response.status_code == 200:
                transactions = response.json()
                logger.info(f"✅ Retrieved {len(transactions)} real transactions for account {account_id}")
                
                # Convert to enhanced format with categorization
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
                        "category": self._categorize_real_transaction(txn, account_id),
                        "is_outgoing": txn.get("fromAccountNum") == account_id,
                        "description": self._generate_transaction_description(txn, account_id),
                        "data_source": "Bank of Anthos API"
                    }
                    formatted_transactions.append(enhanced_txn)
                
                return formatted_transactions
            else:
                logger.error(f"❌ Failed to get transactions for {account_id}: HTTP {response.status_code}")
                raise Exception(f"Transaction API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error getting transactions for {account_id}: {str(e)}")
            raise Exception(f"Failed to get transaction history: {str(e)}")
    
    def _categorize_real_transaction(self, txn: Dict, user_account: str) -> str:
        """Categorize real transactions based on amount patterns and flow direction"""
        amount_dollars = abs(float(txn.get("amount", 0)) / 100.0)
        is_outgoing = txn.get("fromAccountNum") == user_account
        to_account = txn.get("toAccountNum", "")
        from_account = txn.get("fromAccountNum", "")
        
        if not is_outgoing:
            return "income_deposit"
        
        # Categorize outgoing transactions by amount patterns
        # These are realistic categories based on typical spending amounts
        if amount_dollars >= 1500:
            return "major_payment"  # Rent, mortgage, large bills
        elif amount_dollars >= 500:
            return "significant_expense"  # Insurance, utilities, large purchases
        elif amount_dollars >= 100:
            return "moderate_expense"  # Groceries, gas, regular bills
        elif amount_dollars >= 20:
            return "daily_spending"  # Meals, coffee, small purchases
        else:
            return "small_transaction"  # Minimal purchases, fees
    
    def _generate_transaction_description(self, txn: Dict, user_account: str) -> str:
        """Generate human-readable transaction descriptions"""
        amount_dollars = abs(float(txn.get("amount", 0)) / 100.0)
        is_outgoing = txn.get("fromAccountNum") == user_account
        
        if is_outgoing:
            return f"Payment to {txn.get('toAccountNum', 'unknown account')}: ${amount_dollars:.2f}"
        else:
            return f"Deposit from {txn.get('fromAccountNum', 'unknown account')}: ${amount_dollars:.2f}"
    
    async def get_user_contacts(self, username: str, token: str) -> List[Dict]:
        """GET /contacts/{username} - Real user contacts"""
        try:
            url = f"{self.base_urls['contacts']}/contacts/{username}"
            headers = await self._get_auth_headers(token)
            response = await self.client.get(url, headers=headers)
            
            if response.status_code == 200:
                contacts = response.json()
                logger.info(f"✅ Retrieved {len(contacts)} real contacts for user {username}")
                return contacts
            else:
                logger.error(f"❌ Failed to get contacts for {username}: HTTP {response.status_code}")
                raise Exception(f"Contacts API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error getting contacts for {username}: {str(e)}")
            raise Exception(f"Failed to get user contacts: {str(e)}")
    
    async def analyze_spending_patterns(self, account_id: str, token: str, days: int = 90) -> Dict:
        """Analyze real spending patterns with categorization"""
        try:
            transactions = await self.get_transaction_history(account_id, token, 100)
            
            # Initialize analysis
            categories = {}
            total_outgoing = 0
            total_incoming = 0
            transaction_count = len(transactions)
            
            # Analyze each real transaction
            for transaction in transactions:
                amount = transaction.get("amount", 0)
                category = transaction.get("category", "unknown")
                
                if transaction.get("is_outgoing", False):
                    total_outgoing += amount
                    # Track spending by category
                    if category not in categories:
                        categories[category] = {"total": 0, "count": 0}
                    categories[category]["total"] += amount
                    categories[category]["count"] += 1
                else:
                    total_incoming += amount
            
            # Calculate category metrics (convert to dollars)
            for category in categories:
                if categories[category]["count"] > 0:
                    categories[category]["total_dollars"] = categories[category]["total"] / 100.0
                    categories[category]["avg_dollars"] = categories[category]["total_dollars"] / categories[category]["count"]
            
            # Generate insights from real data
            spending_insights = self._generate_real_spending_insights(categories, total_outgoing / 100.0)
            
            analysis_result = {
                "account_id": account_id,
                "analysis_period_days": days,
                "total_outgoing_cents": total_outgoing,
                "total_incoming_cents": total_incoming,
                "total_outgoing_dollars": total_outgoing / 100.0,
                "total_incoming_dollars": total_incoming / 100.0,
                "net_flow_cents": total_incoming - total_outgoing,
                "net_flow_dollars": (total_incoming - total_outgoing) / 100.0,
                "transaction_count": transaction_count,
                "average_monthly": (total_outgoing / 100.0) / 3,  # Assuming 3-month analysis
                "categories": categories,
                "spending_insights": spending_insights,
                "data_source": "Bank of Anthos real transaction data"
            }
            
            logger.info(f"✅ Real spending analysis completed: {transaction_count} transactions, ${analysis_result['total_outgoing_dollars']:.2f} outgoing")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing spending for {account_id}: {str(e)}")
            raise Exception(f"Failed to analyze spending patterns: {str(e)}")
    
    def _generate_real_spending_insights(self, categories: Dict, total_spending: float) -> List[str]:
        """Generate insights from real spending categories"""
        insights = []
        
        if not categories or total_spending == 0:
            return ["No outgoing transactions found for spending analysis"]
        
        # Find highest spending category
        if categories:
            top_category = max(categories.items(), key=lambda x: x[1]["total_dollars"])
            category_name, category_data = top_category
            percentage = (category_data["total_dollars"] / total_spending * 100) if total_spending > 0 else 0
            
            insights.append(f"Primary spending category: {category_name} (${category_data['total_dollars']:.2f}, {percentage:.1f}% of total)")
            insights.append(f"Transaction frequency: {category_data['count']} transactions in {category_name}")
        
        # Overall spending insights
        insights.append(f"Total analyzed spending: ${total_spending:.2f} across {len(categories)} categories")
        insights.append(f"Average per category: ${total_spending / len(categories):.2f}" if categories else "No categories to analyze")
        
        return insights
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()
            logger.info("Bank of Anthos client closed")
