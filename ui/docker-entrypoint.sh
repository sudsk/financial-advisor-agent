#!/bin/sh
# ui/docker-entrypoint.sh - Fixed version without file modification
set -e

echo "🚀 Starting AI Financial Advisor UI..."
echo "Environment: ${NODE_ENV:-production}"
echo "Coordinator API: ${COORDINATOR_API_URL:-coordinator-agent.financial-advisor.svc.cluster.local:8080}"

# Skip the sed injection since it causes permission issues
# The React app will use environment variables at build time instead
echo "📝 Environment variables configured at build time"

echo "✅ UI initialization complete"

# Execute the CMD
exec "$@"
