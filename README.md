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

## 🚀 Quick Start

### Prerequisites
- Google Cloud Project with billing enabled
- GKE cluster with Workload Identity enabled
- `gcloud` CLI configured
- `kubectl` configured for your cluster

### One-Command Deployment
```bash
# Clone and deploy everything
git clone https://github.com/sudsk/financial-advisor-agent.git
cd financial-advisor-agent

# Set your project ID
export PROJECT_ID="your-gcp-project-id"

# Deploy everything
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

# Verify your project
gcloud config set project $PROJECT_ID
```

### Step 3: Deploy with Script
```bash
# Run the complete deployment script
./scripts/deploy.sh
```

This will:
- Create GKE Autopilot cluster with Workload Identity
- Deploy Bank of Anthos to default namespace
- Set up Google Service Account with Vertex AI permissions
- Create Artifact Registry and build/push container images
- Deploy AI Financial Advisor system to financial-advisor namespace
- Configure Workload Identity binding
- Provision all services with LoadBalancer access

### Step 4: Verify Deployment
```bash
# Check all pods are running
kubectl get pods -n financial-advisor

# Get external IP
kubectl get service financial-advisor-ui -n financial-advisor

# Check services health
kubectl get pods -n default | grep -E "(userservice|balancereader|transactionhistory|contacts)"
```

## 🎬 Demo

### Access the Application
```bash
# Get external IP for the UI
EXTERNAL_IP=$(kubectl get service financial-advisor-ui -n financial-advisor -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Financial Advisor UI: http://$EXTERNAL_IP"

# Bank of Anthos URL for comparison
BANK_IP=$(kubectl get service frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Bank of Anthos UI: http://$BANK_IP"
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
- **Password**: `bankofanthos`

## 🛠️ Development

### Local Development Setup
```bash
# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies for each agent
cd agents/coordinator && pip install -r requirements.txt && cd ../..
cd agents/budget-agent && pip install -r requirements.txt && cd ../..

# Set up Application Default Credentials for local development
gcloud auth application-default login
```

### Local Testing
```bash
# Test Bank of Anthos integration
curl -X GET http://userservice.default.svc.cluster.local:8080/ready

# Test MCP server locally
cd mcp-server
python server.py
```

### Container Development
```bash
# Build individual service
docker build -t mcp-server ./mcp-server

# Build all services
./scripts/build.sh
```

## 🏗️ Project Structure

```
financial-advisor-agent/
├── agents/
│   ├── coordinator/              # ADK-powered orchestration agent
│   │   ├── Dockerfile
│   │   ├── agent.py             # ADK agent with Vertex AI integration
│   │   ├── server.py            # FastAPI server following ADK pattern
│   │   └── requirements.txt
│   ├── budget-agent/             # Spending analysis agent
│   ├── investment-agent/         # Portfolio recommendations agent
│   └── security-agent/           # Risk assessment agent
├── mcp-server/                   # Bank of Anthos integration
│   ├── Dockerfile
│   ├── server.py                # MCP protocol server
│   ├── bank_anthos_client.py    # Bank API client
│   └── requirements.txt
├── ui/                           # React frontend dashboard
│   ├── Dockerfile
│   ├── package.json
│   ├── nginx.conf               # Nginx proxy configuration
│   └── src/
├── k8s/                          # Kubernetes manifests
│   ├── namespace.yaml
│   ├── mcp-server-deployment.yaml
│   ├── coordinator-deployment.yaml
│   ├── agents-deployment.yaml
│   ├── services.yaml
│   └── ui-deployment.yaml
├── scripts/                      # Deployment and utility scripts
│   ├── deploy.sh
│   └── build.sh
├── docs/                         # Additional documentation
│   ├── API_INTEGRATION.md
│   └── frontend_ui.html
└── README.md
```

## 🔗 Integration Points

### Bank of Anthos API Endpoints
Our MCP server integrates with these Bank of Anthos endpoints:

| Service | Endpoint | Purpose | Data Format |
|---------|----------|---------|-------------|
| **UserService** | `GET /login` | User authentication | Query params: username, password |
| **UserService** | `GET /users/{user_id}` | User profile data | User demographics, account info |
| **BalanceReader** | `GET /balances/{account_id}` | Current account balance | Real-time balance in cents |
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
- **Model**: Gemini 2.5 Flash via Vertex AI
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
MCP_SERVER_URL=http://mcp-server.financial-advisor.svc.cluster.local:8080

# Vertex AI Configuration
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True
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

## 🧪 Testing

### Integration Tests
```bash
# Test Bank of Anthos integration
kubectl exec -n financial-advisor deployment/mcp-server -- curl -f http://localhost:8080/health

# Test agent coordination
kubectl logs -f deployment/coordinator-agent -n financial-advisor

# End-to-end demo test
curl -X POST http://$EXTERNAL_IP/api/analyze -H "Content-Type: application/json" -d '{"user_id":"testuser","account_id":"1234567890","query":"test"}'
```

### Load Testing
```bash
# Scale up for load testing
kubectl scale deployment coordinator-agent --replicas=3 -n financial-advisor
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Follow ADK patterns for Python agent code
- Use TypeScript for frontend development
- Include unit tests for new features
- Update documentation for API changes

## 🧹 Cleanup

To remove all resources:

```bash
# Delete the financial advisor namespace
kubectl delete namespace financial-advisor

# Delete Bank of Anthos (optional)
kubectl delete -f https://raw.githubusercontent.com/GoogleCloudPlatform/bank-of-anthos/main/kubernetes-manifests.yaml

# Delete the GKE cluster
gcloud container clusters delete $CLUSTER_NAME --region=$REGION

# Delete Artifact Registry
gcloud artifacts repositories delete financial-advisor --location=$REGION

# Delete Google Service Account
gcloud iam service-accounts delete financial-advisor-gsa@$PROJECT_ID.iam.gserviceaccount.com
```

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
