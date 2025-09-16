#!/bin/sh
# ui/docker-entrypoint.sh
set -e

echo "🚀 Starting AI Financial Advisor UI..."
echo "Environment: ${NODE_ENV:-production}"
echo "Coordinator API: ${COORDINATOR_API_URL:-coordinator-agent.financial-advisor.svc.cluster.local:8080}"

# Inject runtime environment variables into built React app
if [ -f /usr/share/nginx/html/static/js/main.*.js ]; then
    echo "📝 Injecting runtime environment variables..."
    
    # Replace environment placeholders in the built JS files
    find /usr/share/nginx/html/static/js -name "*.js" -exec sed -i \
        "s|COORDINATOR_API_URL_PLACEHOLDER|${COORDINATOR_API_URL:-coordinator-agent.financial-advisor.svc.cluster.local:8080}|g" {} \;
fi

echo "✅ UI initialization complete"

# Execute the CMD
exec "$@"
