# ui/Dockerfile - Simplified version without complex entrypoint
# Stage 1: Build the React application
FROM node:18-alpine as build

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install ALL dependencies (including devDependencies) for build
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built React app from previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Create a simple health check file
RUN echo "healthy" > /usr/share/nginx/html/health.txt

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Start nginx directly without custom entrypoint
CMD ["nginx", "-g", "daemon off;"]
