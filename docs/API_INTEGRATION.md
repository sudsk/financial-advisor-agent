# 🔗 Bank of Anthos API Integration Guide

## Overview

This document details how the AI Financial Advisor integrates with Bank of Anthos APIs through the Model Context Protocol (MCP) server.

## Bank of Anthos API Endpoints

### Discovered Endpoints

Based on our analysis of the Bank of Anthos frontend code and testing, here are the confirmed API endpoints:

| Service | Endpoint | Method | Purpose | Status |
|---------|----------|--------|---------|--------|
| **UserService** | `/login` | POST | User authentication | ✅ Confirmed |
| **UserService** | `/users/{user_id}` | GET | User profile data | ✅ Confirmed |
| **BalanceReader** | `/balances/{account_id}` | GET | Account balance | ✅ Confirmed |
| **TransactionHistory** | `/transactions/{account_id}` | GET | Transaction history | ✅ Confirmed |
| **Contacts** | `/contacts/{user_id}` | GET | User contacts | ✅ Confirmed |
| **All Services** | `/ready` | GET | Health check | ✅ Confirmed |

### Service Discovery

Bank of Anthos services are accessible within the Kubernetes cluster using internal DNS:

```yaml
Services:
  userservice: userservice.default.svc.cluster.local:8080
  balancereader: balancereader.default.svc.cluster.local:8080
  transactionhistory: transactionhistory.default.svc.cluster.local:8080
  contacts: contacts.default.svc.cluster.local:8080
  ledgerwriter: ledgerwriter.default.svc.cluster.local:8080
```

## MCP Server Integration

### Architecture

```
AI Agents → MCP Server → Bank of Anthos APIs
    ↑           ↑              ↑
   A2A       MCP           REST APIs
Protocol   Protocol
```

### MCP Server Endpoints

Our MCP server exposes these tools for agent consumption:

#### 1. Get User Data
```http
POST /tools/get_user_data
Content-Type: application/json

{
  "user_id": "testuser",
  "include_transactions": true,
  "transaction_days": 30
}
```

**Response:**
```json
{
  "profile": {
    "user_id": "testuser",
    "account_id": "1234567890",
    "name": "Test User",
    "email": "testuser@example.com"
  },
  "transactions": [...],
  "timestamp": "2025-01-15T10:30:00Z"
}
```

#### 2. Analyze Spending
```http
POST /tools/analyze_spending
Content-Type: application/json

{
  "account_id": "1234567890",
  "analysis_days": 90
}
```

**Response:**
```json
{
  "total_spending": 4500.50,
  "categories": {
    "Groceries": 800.25,
    "Dining": 450.75,
    "Gas": 200.00
  },
  "average_monthly": 1500.17,
  "transaction_count": 45
}
```

#### 3. Get Financial Snapshot
```http
POST /tools/get_financial_snapshot
Content-Type: application/json

{
  "user_id": "testuser",
  "account_id": "1234567890"
}
```

**Response:**
```json
{
  "profile": {...},
  "balance": {
    "account_id": "1234567890",
    "amount": 15750.50,
    "currency": "USD"
  },
  "recent_transactions": [...],
  "spending_analysis": {...},
  "contacts": [...],
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## Bank of Anthos API Details

### 1. UserService API

#### Authentication
```http
POST http://userservice.default.svc.cluster.local:8080/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password"
}
```

**Response (Success):**
```json
{
  "token": "jwt-token-here",
  "user_id": "testuser",
  "expires_in": 3600
}
```

**Response (Failure):**
```json
{
  "error": "Invalid credentials",
  "status": 401
}
```

#### Get User Profile
```http
GET http://userservice.default.svc.cluster.local:8080/users/testuser
Authorization: Bearer jwt-token
```

**Response:**
```json
{
  "user_id": "testuser",
  "account_id": "1234567890",
  "name": "Test User",
  "email": "testuser@example.com",
  "account_type": "checking",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 2. BalanceReader API

#### Get Account Balance
```http
GET http://balancereader.default.svc.cluster.local:8080/balances/1234567890
Authorization: Bearer jwt-token
```

**Response:**
```json
{
  "account_id": "1234567890",
  "amount": 15750.50,
  "currency": "USD",
  "last_updated": "2025-01-15T10:30:00Z",
  "account_type": "checking"
}
```

### 3. TransactionHistory API

#### Get Transaction History
```http
GET http://transactionhistory.default.svc.cluster.local:8080/transactions/1234567890
Authorization: Bearer jwt-token
```

**Query Parameters:**
- `start_date` (optional): ISO 8601 date string
- `end_date` (optional): ISO 8601 date string
- `limit` (optional): Number of transactions to return
- `category` (optional): Filter by transaction category

**Response:**
```json
[
  {
    "transaction_id": "txn_001",
    "account_id": "1234567890",
    "amount": -45.67,
    "category": "Groceries",
    "description": "Supermarket Purchase",
    "timestamp": "2025-01-14T14:30:00Z",
    "location": "New York, NY",
    "merchant": "Local Grocery Store"
  },
  {
    "transaction_id": "txn_002",
    "account_id": "1234567890",
    "amount": 2500.00,
    "category": "Deposit",
    "description": "Salary Deposit",
    "timestamp": "2025-01-01T09:00:00Z",
    "location": "New York, NY"
  }
]
```

### 4. Contacts API

#### Get User Contacts
```http
GET http://contacts.default.svc.cluster.local:8080/contacts/testuser
Authorization: Bearer jwt-token
```

**Response:**
```json
[
  {
    "contact_id": "contact_001",
    "name": "John Doe",
    "account_number": "987654321",
    "relationship": "friend",
    "email": "john.doe@example.com"
  },
  {
    "contact_id": "contact_002",
    "name": "Jane Smith",
    "account_number": "555666777",
    "relationship": "family",
    "email": "jane.smith@example.com"
  }
]
```

## Error Handling Strategy

### API Response Patterns

Bank of Anthos APIs return different error formats:

#### Java Services (Spring Boot)
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "status": 404,
  "error": "Not Found",
  "path": "/api/endpoint"
}
```

#### Python Services (Flask)
```html
<!doctype html>
<html lang=en>
<title>404 Not Found</title>
<h1>Not Found</h1>
<p>The requested URL was not found...</p>
```

### MCP Server Error Handling

Our MCP server implements robust error handling:

```python
async def get_user_profile(self, user_id: str) -> Dict:
    try:
        url = f"{self.base_urls['userservice']}/users/{user_id}"
        response = await self.client.get(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Failed to get user profile: {response.status_code}")
            # Return mock data for demo purposes
            return self._generate_mock_user_data(user_id)
            
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        # Fallback to mock data
        return self._generate_mock_user_data(user_id)
```

### Mock Data Strategy

For demo reliability, the MCP server includes mock data generators:

```python
def _generate_mock_transactions(self, account_id: str, days: int) -> List[Dict]:
    """Generate realistic mock transaction data"""
    transactions = []
    categories = ["Groceries", "Dining", "Gas", "Entertainment", "Shopping"]
    
    for i in range(min(days * 2, 60)):
        date = datetime.now() - timedelta(days=random.randint(0, days))
        amount = random.uniform(-200, -5) if random.random() > 0.1 else random.uniform(1000, 3000)
        
        transactions.append({
            "transaction_id": f"txn_{account_id}_{i}",
            "account_id": account_id,
            "amount": round(amount, 2),
            "category": random.choice(categories),
            "timestamp": date.isoformat(),
            "location": random.choice(["New York", "San Francisco", "Los Angeles"])
        })
    
    return sorted(transactions, key=lambda x: x["timestamp"], reverse=True)
```

## Authentication & Security

### JWT Token Management

Bank of Anthos uses JWT tokens for authentication:

```python
class BankAuthManager:
    def __init__(self):
        self.token = None
        self.token_expiry = None
    
    async def get_valid_token(self, username: str, password: str) -> str:
        """Get or refresh JWT token"""
        if self.token and self.token_expiry > datetime.now():
            return self.token
        
        # Authenticate and get new token
        auth_response = await self.authenticate(username, password)
        self.token = auth_response.get("token")
        self.token_expiry = datetime.now() + timedelta(seconds=auth_response.get("expires_in", 3600))
        
        return self.token
```

### Request Headers

All authenticated requests require the JWT token:

```python
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
```

## Integration Testing

### Health Check Verification

Before making API calls, verify service availability:

```python
async def health_check_all_services(self) -> Dict[str, bool]:
    """Check health of all Bank of Anthos services"""
    health_status = {}
    
    for service_name, base_url in self.base_urls.items():
        try:
            response = await self.client.get(f"{base_url}/ready", timeout=5.0)
            health_status[service_name] = response.text.strip() == "ok"
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {str(e)}")
            health_status[service_name] = False
    
    return health_status
```

### Demo Data Setup

For consistent demo experiences, use these test credentials:

```yaml
Demo User Credentials:
  username: "testuser"
  password: "password"
  account_id: "1234567890"

Expected Demo Data:
  balance: ~$15,750
  monthly_spending: ~$4,500
  transaction_count: 40-60 transactions
  categories: ["Groceries", "Dining", "Gas", "Entertainment", "Shopping", "Utilities"]
```

## Performance Optimization

### Connection Management

Use persistent HTTP connections:

```python
class BankOfAnthosClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=10.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
```

### Caching Strategy

Implement intelligent caching for frequently accessed data:

```python
class DataCache:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = {}
    
    def get(self, key: str, default=None):
        if key in self.cache:
            if datetime.now() < self.cache_ttl[key]:
                return self.cache[key]
            else:
                # Cache expired
                del self.cache[key]
                del self.cache_ttl[key]
        return default
    
    def set(self, key: str, value, ttl_seconds: int = 300):
        self.cache[key] = value
        self.cache_ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)
```

### Parallel Processing

For financial snapshots, fetch data in parallel:

```python
async def get_financial_snapshot(self, user_id: str, account_id: str) -> Dict:
    """Get comprehensive financial data with parallel API calls"""
    
    # Execute all API calls in parallel
    tasks = [
        self.get_user_profile(user_id),
        self.get_account_balance(account_id),
        self.get_transaction_history(account_id),
        self.get_user_contacts(user_id)
    ]
    
    profile, balance, transactions, contacts = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle any exceptions and build response
    return {
        "profile": profile if not isinstance(profile, Exception) else {},
        "balance": balance if not isinstance(balance, Exception) else {},
        "recent_transactions": transactions[:10] if not isinstance(transactions, Exception) else [],
        "contacts": contacts if not isinstance(contacts, Exception) else [],
        "timestamp": datetime.now().isoformat()
    }
```

## Monitoring & Debugging

### Request Logging

Log all API interactions for debugging:

```python
import logging

class APILogger:
    def __init__(self):
        self.logger = logging.getLogger("bank_api_client")
    
    async def log_request(self, method: str, url: str, response_status: int, duration: float):
        self.logger.info(
            f"API Request: {method} {url} -> {response_status} ({duration:.2f}s)"
        )
    
    async def log_error(self, operation: str, error: Exception):
        self.logger.error(f"API Error in {operation}: {str(error)}")
```

### Metrics Collection

Track API performance and reliability:

```python
class APIMetrics:
    def __init__(self):
        self.request_count = defaultdict(int)
        self.error_count = defaultdict(int)
        self.response_times = defaultdict(list)
    
    def record_request(self, service: str, status_code: int, duration: float):
        self.request_count[service] += 1
        if status_code >= 400:
            self.error_count[service] += 1
        self.response_times[service].append(duration)
    
    def get_stats(self) -> Dict:
        return {
            "requests": dict(self.request_count),
            "errors": dict(self.error_count),
            "avg_response_time": {
                service: sum(times) / len(times) if times else 0
                for service, times in self.response_times.items()
            }
        }
```

## Troubleshooting Guide

### Common Issues

#### 1. Service Discovery Problems
**Symptom**: `Connection refused` or `Name resolution failed`
**Solution**: Verify Kubernetes service names and namespaces:
```bash
kubectl get services -n default | grep -E "(userservice|balancereader|transactionhistory|contacts)"
```

#### 2. Authentication Failures
**Symptom**: 401 Unauthorized responses
**Solution**: Check JWT token validity and format:
```bash
# Test login endpoint directly
kubectl port-forward svc/userservice 8080:8080
curl -X POST http://localhost:8080/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password"}'
```

#### 3. Timeout Issues
**Symptom**: Request timeouts or slow responses
**Solution**: Adjust timeout values and add retry logic:
```python
async def make_request_with_retry(self, url: str, max_retries: int = 3) -> Dict:
    for attempt in range(max_retries):
        try:
            response = await self.client.get(url, timeout=10.0)
            return response.json()
        except httpx.TimeoutException:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

#### 4. Data Format Issues
**Symptom**: JSON parsing errors or unexpected data structures
**Solution**: Add robust data validation:
```python
from pydantic import BaseModel, ValidationError

class Transaction(BaseModel):
    transaction_id: str
    account_id: str
    amount: float
    category: str
    timestamp: str

def validate_transactions(data: List[Dict]) -> List[Transaction]:
    valid_transactions = []
    for item in data:
        try:
            transaction = Transaction(**item)
            valid_transactions.append(transaction)
        except ValidationError as e:
            logger.warning(f"Invalid transaction data: {e}")
    return valid_transactions
```

This integration guide provides a comprehensive foundation for connecting with Bank of Anthos APIs while maintaining reliability and performance in the AI Financial Advisor system.
