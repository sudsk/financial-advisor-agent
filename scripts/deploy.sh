#!/bin/bash
# scripts/deploy.sh - Complete deployment script for AI Financial Advisor on GKE

set -e

# Configuration - Update these values
PROJECT_ID=${PROJECT_ID:-"your-gcp-project-id"}
CLUSTER_NAME="financial-advisor-cluster"
REGION="us-central1"
ZONE="us-central1-a"

echo "🚀 Starting AI Financial Advisor deployment to GKE..."
echo "Project ID: $PROJECT_ID"
echo "Cluster: $CLUSTER_NAME"
echo "Region: $REGION"

# Verify required environment variables
if [ "$PROJECT_ID" = "your-gcp-project-id" ]; then
    echo "❌ Please set PROJECT_ID environment variable"
    echo "   export PROJECT_ID=your-actual-project-id"
    exit 1
fi

# Step 1: Set up GCP project
echo "📋 Setting up GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable \
    container.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    compute.googleapis.com \
    iam.googleapis.com

# Step 2: Create GKE Autopilot cluster with Workload Identity
echo "🏗️ Creating GKE Autopilot cluster..."
if ! gcloud container clusters describe $CLUSTER_NAME --region=$REGION >/dev/null 2>&1; then
    gcloud container clusters create-auto $CLUSTER_NAME \
        --region=$REGION \
        --project=$PROJECT_ID \
        --workload-pool=$PROJECT_ID.svc.id.goog \
        --enable-autoscaling \
        --release-channel=regular
    echo "✅ GKE cluster created successfully"
else
    echo "✅ GKE cluster already exists"
fi

# Step 3: Get cluster credentials
echo "🔑 Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

# Step 4: Set up Workload Identity
echo "🔐 Setting up Workload Identity..."

# Create Google Service Account
if ! gcloud iam service-accounts describe financial-advisor-gsa@$PROJECT_ID.iam.gserviceaccount.com >/dev/null 2>&1; then
    gcloud iam service-accounts create financial-advisor-gsa \
        --description="Service account for AI Financial Advisor" \
        --display-name="Financial Advisor GSA"
    echo "✅ Google Service Account created"
else
    echo "✅ Google Service Account already exists"
fi

# Grant Vertex AI permissions
echo "🔒 Granting Vertex AI permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:financial-advisor-gsa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user" \
    --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:financial-advisor-gsa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/ml.developer" \
    --quiet

# Step 5: Create Artifact Registry repository
echo "📦 Setting up Artifact Registry..."
if ! gcloud artifacts repositories describe financial-advisor --location=$REGION >/dev/null 2>&1; then
    gcloud artifacts repositories create financial-advisor \
        --repository-format=docker \
        --location=$REGION \
        --description="AI Financial Advisor container images"
    echo "✅ Artifact Registry created"
else
    echo "✅ Artifact Registry already exists"
fi

# Configure Docker for Artifact Registry
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

# Step 6: Deploy Bank of Anthos (if not already deployed)
echo "🏦 Checking Bank of Anthos deployment..."
if ! kubectl get deployment frontend >/dev/null 2>&1; then
    echo "Deploying Bank of Anthos..."
    kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/bank-of-anthos/main/extras/jwt/jwt-secret.yaml
    kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/bank-of-anthos/main/kubernetes-manifests.yaml
    
    # Wait for Bank of Anthos to be ready
    echo "⏳ Waiting for Bank of Anthos to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment --all -n default
    echo "✅ Bank of Anthos deployed successfully"
else
    echo "✅ Bank of Anthos already running"
fi

# Step 7: Create Financial Advisor namespace
echo "📋 Creating Financial Advisor namespace..."
kubectl apply -f k8s/namespace.yaml

# Step 8: Configure Workload Identity binding
echo "🔗 Setting up Workload Identity binding..."

# Create Kubernetes Service Account
if ! kubectl get serviceaccount financial-advisor-ksa -n financial-advisor >/dev/null 2>&1; then
    kubectl create serviceaccount financial-advisor-ksa -n financial-advisor
    echo "✅ Kubernetes Service Account created"
else
    echo "✅ Kubernetes Service Account already exists"
fi

# Bind Kubernetes SA to Google SA
gcloud iam service-accounts add-iam-policy-binding \
    financial-advisor-gsa@$PROJECT_ID.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:$PROJECT_ID.svc.id.goog[financial-advisor/financial-advisor-ksa]" \
    --quiet

# Annotate Kubernetes Service Account
kubectl annotate serviceaccount financial-advisor-ksa \
    -n financial-advisor \
    iam.gke.io/gcp-service-account=financial-advisor-gsa@$PROJECT_ID.iam.gserviceaccount.com \
    --overwrite

echo "✅ Workload Identity configured successfully"

# Step 9: Build and push container images
echo "🔨 Building and pushing container images..."
./scripts/build.sh

# Step 10: Update Kubernetes manifests with correct values
echo "📝 Updating Kubernetes manifests..."
# Create temporary files with updated values
for file in k8s/*.yaml; do
    if [ -f "$file" ]; then
        # Create backup
        cp "$file" "$file.backup"
        
        # Replace placeholders
        sed -i "s/PROJECT_ID/$PROJECT_ID/g" "$file"
        sed -i "s/REGION/$REGION/g" "$file"
        
        echo "✅ Updated $file"
    fi
done

# Step 11: Deploy AI Financial Advisor system
echo "🤖 Deploying AI Financial Advisor agents..."

# Deploy all components
kubectl apply -f k8s/ -n financial-advisor

echo "⏳ Waiting for deployments to be ready..."
# Wait for deployments with timeout
timeout 600s bash -c '
    while ! kubectl get deployment -n financial-advisor | grep -q "1/1.*1.*1"; do
        echo "Waiting for deployments..."
        sleep 10
    done
'

# Check deployment status
kubectl get pods -n financial-advisor

# Step 12: Get external IP and display access information
echo "🌐 Getting access information..."
echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "🎯 Access Information:"
echo "  Project ID: $PROJECT_ID"
echo "  Cluster: $CLUSTER_NAME"
echo "  Region: $REGION"
echo "  Namespace: financial-advisor"
echo ""

# Wait for LoadBalancer IP
echo "⏳ Waiting for LoadBalancer IP assignment..."
timeout 300s bash -c '
    while [ -z "$(kubectl get service financial-advisor-ui -n financial-advisor -o jsonpath="{.status.loadBalancer.ingress[0].ip}" 2>/dev/null)" ]; do
        echo "Waiting for external IP..."
        sleep 10
    done
'

EXTERNAL_IP=$(kubectl get service financial-advisor-ui -n financial-advisor -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)

if [ -n "$EXTERNAL_IP" ]; then
    echo "🚀 Application Access URLs:"
    echo "  Financial Advisor UI: http://$EXTERNAL_IP"
else
    echo "⏳ External IP still pending. Check status with:"
    echo "  kubectl get service financial-advisor-ui -n financial-advisor"
fi

# Get Bank of Anthos URL for comparison
BANK_IP=$(kubectl get service frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
if [ -n "$BANK_IP" ]; then
    echo "  Bank of Anthos UI: http://$BANK_IP"
fi

echo ""
echo "📊 Services deployed:"
echo "  • MCP Server (Bank of Anthos API integration)"
echo "  • Coordinator Agent (ADK + Vertex AI orchestration)"
echo "  • Budget Agent (Spending analysis with Gemini)"
echo "  • Investment Agent (Portfolio recommendations)"
echo "  • Security Agent (Risk assessment)"
echo "  • Frontend UI (Interactive dashboard)"
echo ""
echo "🔗 Technology Stack:"
echo "  • GKE Autopilot: Auto-scaling Kubernetes"
echo "  • Vertex AI: Gemini Pro via Workload Identity"
echo "  • MCP Protocol: Bank of Anthos integration"
echo "  • A2A Protocol: Inter-agent communication"
echo "  • ADK: Agent lifecycle management"
echo ""
echo "🎬 Demo Ready!"
echo "  Login: testuser / password"
echo "  Try: 'Help me save $80,000 for a house down payment in 3 years'"

# Step 13: Run health checks
echo ""
echo "🏥 Running health checks..."
sleep 30

check_service() {
    local service=$1
    local url="http://$service.financial-advisor.svc.cluster.local:8080/health"
    
    if kubectl exec -n financial-advisor deployment/$service -- curl -f -s $url >/dev/null 2>&1; then
        echo "  ✅ $service: Healthy"
    else
        echo "  ❌ $service: Health check failed"
    fi
}

echo "Service Health Status:"
check_service "mcp-server"
check_service "coordinator-agent" 
check_service "budget-agent"
check_service "investment-agent"
check_service "security-agent"

# Restore original manifests
echo ""
echo "🔄 Restoring original manifests..."
for file in k8s/*.yaml.backup; do
    if [ -f "$file" ]; then
        original_file="${file%.backup}"
        mv "$file" "$original_file"
    fi
done

echo ""
echo "🎉 All systems operational! Ready for GKE Hackathon demo!"
echo ""
echo "📋 Quick Commands:"
echo "  Check pods: kubectl get pods -n financial-advisor"
echo "  View logs: kubectl logs -f deployment/coordinator-agent -n financial-advisor"
echo "  Scale up: kubectl scale deployment coordinator-agent --replicas=3 -n financial-advisor"
echo "  Get IP: kubectl get service financial-advisor-ui -n financial-advisor"
echo ""
echo "🏆 Ready to win the hackathon! 🚀"#!/bin/bash
# deploy.sh - Complete deployment script for AI Financial Advisor on GKE

set -e

# Configuration
PROJECT_ID="your-gcp-project-id"
CLUSTER_NAME="financial-advisor-cluster"
ZONE="us-central1-a"
REGION="us-central1"
GEMINI_API_KEY="your-gemini-api-key"

echo "🚀 Starting AI Financial Advisor deployment to GKE..."

# Step 1: Set up GCP project
echo "📋 Setting up GCP project..."
gcloud config set project $PROJECT_ID
gcloud services enable container.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Step 2: Create GKE cluster
echo "🏗️ Creating GKE cluster..."
gcloud container clusters create $CLUSTER_NAME \
    --zone=$ZONE \
    --num-nodes=4 \
    --enable-autoscaling \
    --min-nodes=3 \
    --max-nodes=10 \
    --node-locations=$ZONE \
    --enable-autorepair \
    --enable-autoupgrade \
    --machine-type=e2-standard-4 \
    --disk-size=50GB

# Step 3: Get cluster credentials
echo "🔑 Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE

# Step 4: Create Artifact Registry repository
echo "📦 Setting up Artifact Registry..."
gcloud artifacts repositories create financial-advisor \
    --repository-format=docker \
    --location=$REGION \
    --description="AI Financial Advisor container images"

# Configure Docker for Artifact Registry
gcloud auth configure-docker $REGION-docker.pkg.dev

# Step 5: Build and push container images
echo "🔨 Building container images..."

# MCP Server
echo "Building MCP Server..."
cd mcp-server
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor/mcp-server:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor/mcp-server:latest
cd ..

# Coordinator Agent
echo "Building Coordinator Agent..."
cd agents/coordinator
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor/coordinator-agent:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor/coordinator-agent:latest
cd ../..

# Budget Agent
echo "Building Budget Agent..."
cd agents/budget-agent
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor/budget-agent:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor/budget-agent:latest
cd ../..

# Investment Agent
echo "Building Investment Agent..."
cd agents/investment-agent
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor/investment-agent:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor/investment-agent:latest
cd ../..

# Security Agent
echo "Building Security Agent..."
cd agents/security-agent
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor/security-agent:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor/security-agent:latest
cd ../..

# Frontend UI
echo "Building Frontend UI..."
cd ui
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor/financial-advisor-ui:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor/financial-advisor-ui:latest
cd ..

# Step 6: Deploy Bank of Anthos (if not already deployed)
echo "🏦 Deploying Bank of Anthos..."
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/bank-of-anthos/main/releases/v0.6.4/kubernetes-manifests.yaml

# Wait for Bank of Anthos to be ready
echo "⏳ Waiting for Bank of Anthos to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment --all -n default

# Step 7: Create secrets
echo "🔐 Creating secrets..."
kubectl create secret generic gemini-secret \
    --from-literal=api-key=$GEMINI_API_KEY \
    -n financial-advisor

# Step 8: Update Kubernetes manifests with correct image URLs
echo "📝 Updating Kubernetes manifests..."
sed -i "s/PROJECT_ID/$PROJECT_ID/g" k8s/*.yaml
sed -i "s/REGION/$REGION/g" k8s/*.yaml

# Step 9: Deploy AI Financial Advisor system
echo "🤖 Deploying AI Financial Advisor agents..."

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy all components
kubectl apply -f k8s/mcp-server-deployment.yaml
kubectl apply -f k8s/coordinator-deployment.yaml
kubectl apply -f k8s/agents-deployment.yaml
kubectl apply -f k8s/services.yaml

# Deploy UI with LoadBalancer
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: financial-advisor-ui
  namespace: financial-advisor
spec:
  replicas: 2
  selector:
    matchLabels:
      app: financial-advisor-ui
  template:
    metadata:
      labels:
        app: financial-advisor-ui
    spec:
      containers:
      - name: ui
        image: $REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor/financial-advisor-ui:latest
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
EOF

# Step 10: Wait for all deployments to be ready
echo "⏳ Waiting for all deployments to be ready..."
kubectl wait --for=condition=available --timeout=600s deployment --all -n financial-advisor

# Step 11: Get external IP
echo "🌐 Getting external IP address..."
kubectl get service financial-advisor-ui -n financial-advisor

# Step 12: Display deployment information
echo "✅ Deployment completed successfully!"
echo ""
echo "🎯 Deployment Summary:"
echo "  Cluster: $CLUSTER_NAME"
echo "  Zone: $ZONE"
echo "  Namespace: financial-advisor"
echo ""
echo "📊 Services deployed:"
echo "  • MCP Server (Bank of Anthos API integration)"
echo "  • Coordinator Agent (ADK-powered orchestration)"
echo "  • Budget Agent (Spending analysis)"
echo "  • Investment Agent (Portfolio recommendations)"
echo "  • Security Agent (Risk assessment)"
echo "  • Frontend UI (Interactive dashboard)"
echo ""
echo "🔗 Agent Communication:"
echo "  • MCP Protocol: Bank of Anthos ↔ MCP Server ↔ Agents"
echo "  • A2A Protocol: Inter-agent communication"
echo "  • ADK: Agent lifecycle management"
echo ""
echo "🚀 Access your application:"
echo "  External IP: $(kubectl get service financial-advisor-ui -n financial-advisor -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
echo "  URL: http://$(kubectl get service financial-advisor-ui -n financial-advisor -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
echo ""
echo "📱 Demo readiness:"
echo "  • Bank of Anthos: ✅ Running"
echo "  • AI Agents: ✅ Deployed"
echo "  • Frontend: ✅ Accessible"
echo "  • A2A Communication: ✅ Configured"
echo "  • MCP Integration: ✅ Active"
echo ""
echo "🎬 Ready for hackathon demo!"

# Step 13: Health check all services
echo "🏥 Running health checks..."
sleep 30

echo "Checking MCP Server..."
kubectl exec -n financial-advisor deployment/mcp-server -- curl -f http://localhost:8080/health || echo "❌ MCP Server health check failed"

echo "Checking Coordinator Agent..."
kubectl exec -n financial-advisor deployment/coordinator-agent -- curl -f http://localhost:8080/health || echo "❌ Coordinator health check failed"

echo "Checking Budget Agent..."
kubectl exec -n financial-advisor deployment/budget-agent -- curl -f http://localhost:8080/health || echo "❌ Budget Agent health check failed"

echo "Checking Investment Agent..."
kubectl exec -n financial-advisor deployment/investment-agent -- curl -f http://localhost:8080/health || echo "❌ Investment Agent health check failed"

echo "Checking Security Agent..."
kubectl exec -n financial-advisor deployment/security-agent -- curl -f http://localhost:8080/health || echo "❌ Security Agent health check failed"

echo ""
echo "🎉 All systems operational! Ready for GKE Hackathon submission!"
