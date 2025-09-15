# 🤖 AI Financial Advisor - GKE Hackathon

Multi-agent AI system that provides personalized financial advice by integrating with Bank of Anthos using modern AI and Kubernetes technologies.

## 🏆 Hackathon Entry

Built for the **Google Kubernetes Engine 10th Anniversary Hackathon** showcasing:
- **GKE**: Container orchestration and auto-scaling with Workload Identity
- **ADK**: Agent Development Kit for agent lifecycle management  
- **MCP**: Model Context Protocol for seamless Bank of Anthos integration
- **A2A**: Agent-to-Agent communication protocol
- **Vertex AI Gemini**: Intelligent financial analysis via Application Default Credentials

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GKE Autopilot Cluster                   │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │   Default Namespace │    │ Financial-Advisor Namespace │ │
│  │  (Bank of Anthos)   │    │    (Our AI System)         │ │
│  │                     │    │                             │ │
│  │ ┌─────────────────┐ │    │ ┌─────────────────────────┐ │ │
│  │ │ userservice     │◄┼────┼─┤ MCP Server              │ │ │
│  │ │ balancereader   │ │    │ │ (API Gateway)           │ │ │
│  │ │ transactionhist │ │    │ │ + Workload Identity     │ │ │
│  │ │ contacts        │ │    │ └─────────────┬───────────┘ │ │
│  │ │ ledgerwriter    │ │    │               │ A2A         │ │
│  │ └─────────────────┘ │    │ ┌─────────────▼───────────┐ │ │
│  │                     │    │ │ AI Agent Ecosystem      │ │ │
│  │ ┌─────────────────┐ │    │ │ • Coordinator (ADK)     │ │ │
│  │ │ Frontend UI     │ │    │ │ • Budget Agent          │ │ │
│  │ │ (Bank Website)  │ │    │ │ • Investment Agent      │ │ │
│  │ └─────────────────┘ │    │ │ • Security Agent        │ │ │
│  └─────────────────────┘    │ │ • Financial Advisor UI  │ │ │
│                             │ └─────────────────────────┘ │ │
│                             └─────────────────────────────┘ │
│                  Vertex AI Gemini (via Workload Identity)  │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

### 🧠 **Multi-Agent Intelligence**
- **Coordinator Agent**: Orchestrates financial queries using ADK
- **Budget Agent**: Analyzes spending patterns and optimization opportunities
- **Investment Agent**: Provides portfolio recommendations and risk assessment
- **Security Agent**: Monitors for fraud and financial security risks

### 🔗 **Seamless Integration**
- **Zero Code Changes**: Pure API integration with existing Bank of Anthos
- **MCP Protocol**: Standardized communication with banking microservices
- **A2A Protocol**: Real-time agent-to-agent coordination
- **Workload Identity**: Secure access to Vertex AI Gemini

### ⚡ **Production Ready**
- **GKE Autopilot**: Cost-optimized, auto-scaling Kubernetes
- **Cloud-native Security**: IAM, Workload Identity, network policies
- **Observability**: Integrated monitoring and logging
- **Horizontal Scaling**: Auto-scaling based on demand

## 🎯 Bank of Anthos API Endpoints 

Based on the frontend code, here are the exact API endpoints our AI agents can integrate with:

## 📋 Complete API Reference

|Service|Endpoint|Purpose|Our Integration|
|-------|--------|-------|---------------|
|UserService|POST /loginUser| authentication|✅ User verification|
|UserService|GET /usersUser| profiles|✅ Budget Agent needs this|
|BalanceReader|GET /balances|Account balances|✅ Investment Agent needs this|
|TransactionHistory|GET /transactionsTransaction| history|✅ Budget + Security |
|AgentsContacts|GET /contactsUser| contacts|✅ Nice-to-have for agents|
|LedgerWriter|POST /transactions|Create transactions|❌ Read-only for our demo|

## 🚀 Quick Start

### Prerequisites
- Google Cloud Project with billing enabled
- GKE cluster with Workload Identity enabled
- Bank of Anthos deployed (see setup instructions below)
- `gcloud` CLI configured
- `kubectl` configured for your cluster

### One-Command Deployment
```bash
# Clone and deploy everything
git clone https://github.com/sudsk/financial-advisor-agent.git
cd financial-advisor-agent
./scripts/deploy.sh
```

## 📋 Detailed Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/sudsk/financial-advisor-agent.git
cd financial-advisor-agent
```

### Step 2: Set Environment Variables
```bash
export PROJECT_ID="your-gcp-project-id"
export CLUSTER_NAME="financial-advisor-cluster"
export REGION="us-central1"
export ZONE="us-central1-a"

# Verify your project
gcloud config set project $PROJECT_ID
```

### Step 3: Create GKE Autopilot Cluster (if needed)
```bash
# Create cost-optimized Autopilot cluster with Workload Identity
gcloud container clusters create-auto $CLUSTER_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --workload-pool=$PROJECT_ID.svc.id.goog \
    --enable-autoscaling \
    --release-channel=regular

# Get cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION
```

### Step 4: Deploy Bank of Anthos
```bash
# Deploy Bank of Anthos to default namespace
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/bank-of-anthos/main/extras/jwt/jwt-secret.yaml
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/bank-of-anthos/main/kubernetes-manifests.yaml

# Wait for Bank of Anthos to be ready
kubectl wait --for=condition=available --timeout=300s deployment --all -n default

# Verify Bank of Anthos is running
kubectl get pods
kubectl get services
```

### Step 5: Enable Required APIs
```bash
# Enable required Google Cloud APIs
gcloud services enable \
    container.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    compute.googleapis.com \
    iam.googleapis.com
```

### Step 6: Set Up Workload Identity
```bash
# Create Google Service Account for Vertex AI access
gcloud iam service-accounts create financial-advisor-gsa \
    --description="Service account for AI Financial Advisor" \
    --display-name="Financial Advisor GSA"

# Grant Vertex AI permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:financial-advisor-gsa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:financial-advisor-gsa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/ml.developer"
```

### Step 7: Create Financial Advisor Namespace
```bash
# Create our namespace
kubectl apply -f k8s/namespace.yaml

# Verify namespace creation
kubectl get namespaces | grep financial-advisor
```

### Step 8: Configure Workload Identity Binding
```bash
# Create Kubernetes Service Account
kubectl create serviceaccount financial-advisor-ksa -n financial-advisor

# Bind Kubernetes SA to Google SA
gcloud iam service-accounts add-iam-policy-binding \
    financial-advisor-gsa@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[financial-advisor/financial-advisor-ksa]"

# Annotate Kubernetes Service Account
kubectl annotate serviceaccount financial-advisor-ksa \
    -n financial-advisor \
    iam.gke.io/gcp-service-account=financial-advisor-gsa@$PROJECT_ID.iam.gserviceaccount.com
```

### Step 9: Set Up Artifact Registry
```bash
# Create Artifact Registry repository
gcloud artifacts repositories create financial-advisor \
    --repository-format=docker \
    --location=$REGION \
    --description="AI Financial Advisor container images"

# Configure Docker authentication
gcloud auth configure-docker $REGION-docker.pkg.dev
```

### Step 10: Build and Deploy
```bash
# Build all container images
./scripts/build.sh

# Deploy AI Financial Advisor system
kubectl apply -f k8s/

# Wait for deployment to complete
kubectl wait --for=condition=available --timeout=600s deployment --all -n financial-advisor
```

### Step 11: Verify Deployment
```bash
# Check all pods are running
kubectl get pods -n financial-advisor

# Check services
kubectl get services -n financial-advisor

# Check Workload Identity setup
kubectl describe pod -l app=coordinator-agent -n financial-advisor | grep "serviceaccount\|gcp-service-account"
```

## 🎬 Demo

### Access the Application
```bash
# Get external IP for the UI
kubectl get service financial-advisor-ui -n financial-advisor

# Access the application
echo "Financial Advisor UI: http://$(kubectl get service financial-advisor-ui -n financial-advisor -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"

# Access Bank of Anthos (for comparison)
echo "Bank of Anthos UI: http://$(kubectl get service frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
```

### Demo Scenarios

#### 1. House Down Payment Planning
**Query**: "Help me save $80,000 for a house down payment in 3 years"

**Expected Agent Flow**:
- Coordinator Agent analyzes the financial goal
- Budget Agent examines current spending from Bank of Anthos transactions
- Investment Agent calculates optimal savings strategy
- Security Agent assesses financial risks
- Coordinated response with actionable recommendations

#### 2. Retirement Planning
**Query**: "I'm 35 years old and want to retire comfortably at 60. What's my best strategy?"

#### 3. Debt Optimization
**Query**: "I have $15,000 in credit card debt at 18% interest. How should I pay this off while still saving?"

#### 4. Investment Portfolio
**Query**: "I have $25,000 to invest and want to balance growth with safety. What do you recommend?"

### Demo Login Credentials
- **Username**: `testuser`
- **Password**: `password`

## 🛠️ Development

### Local Development Setup
```bash
# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up Application Default Credentials for local development
gcloud auth application-default login
```

### Local Testing
```bash
# Test Bank of Anthos integration
./scripts/test-integration.sh

# Test individual agents
./scripts/test-agents.sh

# Run MCP server locally
cd mcp-server
python server.py
```

### Container Development
```bash
# Build individual service
docker build -t mcp-server ./mcp-server

# Build all services
./scripts/build.sh

# Push to Artifact Registry
./scripts/push.sh
```

## 🏗️ Project Structure

```
financial-advisor-agent/
├── agents/
│   ├── coordinator/              # ADK-powered orchestration agent
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   ├── agent_logic.py
│   │   └── requirements.txt
│   ├── budget-agent/             # Spending analysis agent
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── investment-agent/         # Portfolio recommendations agent
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   └── security-agent/           # Risk assessment agent
│       ├── Dockerfile
│       ├── main.py
│       └── requirements.txt
├── mcp-server/                   # Bank of Anthos integration
│   ├── Dockerfile
│   ├── server.py
│   ├── bank_anthos_client.py
│   └── requirements.txt
├── ui/                           # React frontend dashboard
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   └── public/
├── k8s/                          # Kubernetes manifests
│   ├── namespace.yaml
│   ├── mcp-server-deployment.yaml
│   ├── coordinator-deployment.yaml
│   ├── agents-deployment.yaml
│   ├── services.yaml
│   └── ingress.yaml
├── scripts/                      # Deployment and utility scripts
│   ├── deploy.sh
│   ├── build.sh
│   ├── test-integration.sh
│   └── cleanup.sh
├── docs/                         # Additional documentation
│   ├── ARCHITECTURE.md
│   ├── API_INTEGRATION.md
│   └── DEMO_SCRIPT.md
└── README.md
```

## 🔗 Integration Points

### Bank of Anthos API Endpoints
Our MCP server integrates with these Bank of Anthos endpoints:

| Service | Endpoint | Purpose | Data Format |
|---------|----------|---------|-------------|
| **UserService** | `POST /login` | User authentication | `{"username": "testuser", "password": "password"}` |
| **UserService** | `GET /users/{user_id}` | User profile data | User demographics, account info |
| **BalanceReader** | `GET /balances/{account_id}` | Current account balance | Real-time balance information |
| **TransactionHistory** | `GET /transactions/{account_id}` | Transaction history | Spending patterns, transaction details |
| **Contacts** | `GET /contacts/{user_id}` | User contacts | Payment contacts and relationships |

### Agent Communication Protocols

#### MCP (Model Context Protocol)
```
Bank of Anthos APIs ↔ MCP Server ↔ AI Agents
```

#### A2A (Agent-to-Agent Protocol)
```
Coordinator Agent ↔ Budget Agent
                  ↔ Investment Agent  
                  ↔ Security Agent
```

#### ADK (Agent Development Kit)
- Agent lifecycle management
- State coordination
- Error handling and recovery
- Performance monitoring

### Vertex AI Integration
- **Authentication**: Workload Identity (no API keys)
- **Model**: Gemini Pro via Vertex AI
- **Usage**: Financial analysis, recommendation generation, risk assessment

## ⚙️ Configuration

### Environment Variables
```bash
# Google Cloud Configuration
PROJECT_ID=your-gcp-project-id
REGION=us-central1
CLUSTER_NAME=financial-advisor-cluster

# Bank of Anthos Integration
BANK_ANTHOS_NAMESPACE=default
USERSERVICE_URL=http://userservice.default.svc.cluster.local:8080
BALANCEREADER_URL=http://balancereader.default.svc.cluster.local:8080
TRANSACTIONHISTORY_URL=http://transactionhistory.default.svc.cluster.local:8080
CONTACTS_URL=http://contacts.default.svc.cluster.local:8080

# Vertex AI Configuration
VERTEX_AI_PROJECT=$PROJECT_ID
VERTEX_AI_LOCATION=us-central1
MODEL_NAME=gemini-pro
```

### Kubernetes ConfigMaps
```yaml
# Example: Agent configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-config
  namespace: financial-advisor
data:
  coordinator_replicas: "2"
  agent_timeout: "30"
  vertex_ai_model: "gemini-pro"
  bank_api_timeout: "10"
```

## 🔐 Security

### Workload Identity Benefits
- ✅ **No API Key Management**: Eliminates credential storage in containers
- ✅ **Automatic Rotation**: Google manages credential lifecycle
- ✅ **Least Privilege**: Fine-grained IAM permissions
- ✅ **Audit Trail**: Cloud Audit Logs for all API calls

### Security Features
- **Network Policies**: Restrict pod-to-pod communication
- **Pod Security Standards**: Enforce security constraints
- **Service Mesh**: mTLS between services (optional)
- **Resource Limits**: Prevent resource exhaustion

## 📊 Monitoring

### Observability Stack
- **GKE Monitoring**: Built-in cluster and workload monitoring
- **Cloud Logging**: Centralized log aggregation
- **Cloud Trace**: Distributed tracing for agent interactions
- **Custom Metrics**: Agent performance and business metrics

### Key Metrics
- Agent response times
- API call success rates
- Financial recommendation accuracy
- User satisfaction scores

## 💰 Cost Optimization

### GKE Autopilot Benefits
- **Pay-per-Pod**: Only pay for running workloads
- **Auto-scaling**: Scales to zero during inactivity
- **Optimized Resource Usage**: Right-sizing without over-provisioning

### Estimated Costs (US Central1)
```
Development (8 hours/day): ~$3/day
Demo (3 hours): ~$1
Idle (nights/weekends): ~$0.10/hour
Total Hackathon (10 days): ~$35
```

## 🧪 Testing

### Unit Tests
```bash
# Run unit tests for all components
pytest agents/tests/
pytest mcp-server/tests/
```

### Integration Tests
```bash
# Test Bank of Anthos integration
./scripts/test-integration.sh

# Test agent coordination
./scripts/test-agents.sh

# End-to-end demo test
./scripts/test-demo.sh
```

### Load Testing
```bash
# Simulate multiple concurrent users
./scripts/load-test.sh --users 10 --duration 300s
```

## 📚 Documentation

- [Architecture Deep Dive](docs/ARCHITECTURE.md)
- [API Integration Guide](docs/API_INTEGRATION.md)
- [Demo Script](docs/DEMO_SCRIPT.md)
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

## 🏆 Hackathon Highlights

### Innovation
- ✅ **Multi-Agent Coordination**: First-of-its-kind A2A protocol implementation
- ✅ **Zero-Code Integration**: Seamless connection to existing banking systems
- ✅ **Production Architecture**: Enterprise-ready design patterns

### Technical Excellence
- ✅ **Cloud-Native**: Full GKE and Google Cloud integration
- ✅ **Security First**: Workload Identity and IAM best practices  
- ✅ **Scalable Design**: Auto-scaling, resilient architecture
- ✅ **Modern Protocols**: MCP, A2A, ADK implementation

### Business Value
- ✅ **Real Banking Integration**: Works with actual financial data
- ✅ **Practical AI**: Solves real financial planning problems
- ✅ **Production Ready**: Banks could deploy this today
- ✅ **Cost Effective**: Optimized for real-world economics

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Include unit tests for new features
- Update documentation for API changes

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Cloud**: For providing GKE and Vertex AI platforms
- **Bank of Anthos Team**: For the excellent sample banking application
- **Hackathon Organizers**: For creating this amazing challenge
- **Open Source Community**: For the tools and libraries that made this possible

---

**Built with ❤️ for the Google Kubernetes Engine 10th Anniversary Hackathon**

🚀 **Ready to revolutionize financial services with AI?** Deploy now and see the future of banking! 🤖💰

