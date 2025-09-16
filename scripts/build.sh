#!/bin/bash
# scripts/build.sh - Fixed build script for AI Financial Advisor

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-gcp-project-id"}
REGION=${REGION:-"us-central1"}
REGISTRY="$REGION-docker.pkg.dev/$PROJECT_ID/financial-advisor"

echo "🔨 Building AI Financial Advisor container images..."
echo "Project ID: $PROJECT_ID"
echo "Registry: $REGISTRY"

# Check PROJECT_ID
if [ "$PROJECT_ID" = "your-gcp-project-id" ]; then
    echo "❌ Please set PROJECT_ID environment variable"
    echo "   export PROJECT_ID=your-actual-project-id"
    exit 1
fi

# Function to build and push an image
build_and_push() {
    local service_name=$1
    local dockerfile_path=$2
    local context_path=$3
    
    echo "🔨 Building $service_name..."
    
    # Special handling for UI to generate package-lock.json
    if [ "$service_name" = "financial-advisor-ui" ]; then
        echo "📦 Preparing UI dependencies..."
        cd $context_path
        
        # Remove any existing package-lock.json and node_modules
        rm -f package-lock.json
        rm -rf node_modules
        
        # Generate fresh package-lock.json
        npm install
        
        cd - > /dev/null
    fi
    
    cd $context_path
    
    # Build the image
    docker build -f $dockerfile_path -t $REGISTRY/$service_name:latest .
    
    # Push the image
    echo "📤 Pushing $service_name..."
    docker push $REGISTRY/$service_name:latest
    
    echo "✅ $service_name built and pushed successfully"
    cd - > /dev/null
}

# Configure Docker for Artifact Registry
echo "🔐 Configuring Docker authentication..."
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

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

# Build UI (with special handling)
build_and_push "financial-advisor-ui" "Dockerfile" "ui"

echo ""
echo "🎉 All images built and pushed successfully!"
echo ""
echo "🚀 Ready for GKE Hackathon deployment!"
