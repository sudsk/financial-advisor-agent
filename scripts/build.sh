#!/bin/bash
# scripts/build.sh - Build all container images for AI Financial Advisor

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-gcp-project-id"}
REGION=${REGION:-"us-central1"}
REGISTRY="$REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor"

echo "🔨 Building AI Financial Advisor container images..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Registry: $REGISTRY"

# Function to build and push an image
build_and_push() {
    local service_name=$1
    local dockerfile_path=$2
    local context_path=$3
    
    echo "🔨 Building $service_name..."
    
    cd $context_path
    
    # Build the image
    docker build -f $dockerfile_path -t $REGISTRY/$service_name:latest .
    
    # Push the image
    echo "📤 Pushing $service_name..."
    docker push $REGISTRY/$service_name:latest
    
    echo "✅ $service_name built and pushed successfully"
    cd - > /dev/null
}

# Ensure we're in the project root
if [ ! -f "README.md" ] || [ ! -d "agents" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if we're authenticated to Google Cloud
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated to Google Cloud. Please run 'gcloud auth login'"
    exit 1
fi

# Configure Docker for Artifact Registry
echo "🔐 Configuring Docker authentication..."
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

# Create missing Dockerfiles if they don't exist
echo "📝 Creating missing Dockerfiles..."

# Create Coordinator Agent Dockerfile
if [ ! -f "agents/coordinator/Dockerfile" ]; then
    echo "❌ Missing Coordinator Agent Dockerfile. Please create."
    exit 1    
fi

# Create Budget Agent Dockerfile
if [ ! -f "agents/budget-agent/Dockerfile" ]; then
    echo "❌ Missing Budget Agent Dockerfile. Please create."
    exit 1    
fi

# Create Investment Agent Dockerfile
if [ ! -f "agents/investment-agent/Dockerfile" ]; then
    echo "❌ Missing Investment Agent Dockerfile. Please create."
    exit 1    
fi

# Create Security Agent Dockerfile
if [ ! -f "agents/security-agent/Dockerfile" ]; then
    echo "❌ Missing Security Agent Dockerfile. Please create."
    exit 1    
fi

# Create UI Dockerfile
if [ ! -f "ui/Dockerfile" ]; then
    cat << 'EOF' > ui/Dockerfile
FROM nginx:alpine

# Copy the HTML files
COPY index.html /usr/share/nginx/html/
COPY styles.css /usr/share/nginx/html/ 
COPY app.js /usr/share/nginx/html/

# Copy custom nginx config if needed
# COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF
    echo "✅ Created ui/Dockerfile"
fi

# Create missing requirements.txt files
if [ ! -f "agents/budget-agent/requirements.txt" ]; then
    cat << 'EOF' > agents/budget-agent/requirements.txt
flask==3.0.0
google-cloud-aiplatform==1.38.0
vertexai==1.38.0
asyncio==3.4.3
python-dateutil==2.8.2
gunicorn==21.2.0
EOF
    echo "✅ Created agents/budget-agent/requirements.txt"
fi

if [ ! -f "agents/investment-agent/requirements.txt" ]; then
    cat << 'EOF' > agents/investment-agent/requirements.txt
flask==3.0.0
google-cloud-aiplatform==1.38.0
vertexai==1.38.0
asyncio==3.4.3
python-dateutil==2.8.2
gunicorn==21.2.0
EOF
    echo "✅ Created agents/investment-agent/requirements.txt"
fi

if [ ! -f "agents/security-agent/requirements.txt" ]; then
    cat << 'EOF' > agents/security-agent/requirements.txt
flask==3.0.0
google-cloud-aiplatform==1.38.0
vertexai==1.38.0
asyncio==3.4.3
python-dateutil==2.8.2
gunicorn==21.2.0
EOF
    echo "✅ Created agents/security-agent/requirements.txt"
fi

if [ ! -f "mcp-server/requirements.txt" ]; then
    cat << 'EOF' > mcp-server/requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.0
pydantic==2.5.0
python-multipart==0.0.6
gunicorn==21.2.0
EOF
    echo "✅ Created mcp-server/requirements.txt"
fi

if [ ! -f "agents/coordinator/requirements.txt" ]; then
    cat << 'EOF' > agents/coordinator/requirements.txt
flask==3.0.0
httpx==0.25.0
google-cloud-aiplatform==1.38.0
vertexai==1.38.0
asyncio==3.4.3
python-dateutil==2.8.2
gunicorn==21.2.0
EOF
    echo "✅ Created agents/coordinator/requirements.txt"
fi

# Build all services
echo "🚀 Starting build process..."

# Build MCP Server
build_and_push "mcp-server" "Dockerfile" "mcp-server"

# Build Coordinator Agent  
build_and_push "coordinator-agent" "Dockerfile" "agents/coordinator"

# Build Budget Agent
build_and_push "budget-agent" "Dockerfile" "agents/budget-agent"

# Build Investment Agent
build_and_push "investment-agent" "Dockerfile" "agents/investment-agent"

# Build Security Agent
build_and_push "security-agent" "Dockerfile" "agents/security-agent"

# Build UI
build_and_push "financial-advisor-ui" "Dockerfile" "ui"

echo ""
echo "🎉 All images built and pushed successfully!"
echo ""
echo "📋 Built images:"
echo "  • $REGISTRY/mcp-server:latest"
echo "  • $REGISTRY/coordinator-agent:latest"
echo "  • $REGISTRY/budget-agent:latest"
echo "  • $REGISTRY/investment-agent:latest"
echo "  • $REGISTRY/security-agent:latest"
echo "  • $REGISTRY/financial-advisor-ui:latest"
echo ""
echo "🚀 Ready for deployment to GKE!"
