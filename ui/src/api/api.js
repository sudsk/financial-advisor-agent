// ui/src/api/api.js - Fixed for browser access
import axios from 'axios';

// API Configuration - Fixed for browser environment
const API_CONFIG = {
  development: 'http://localhost:8080',
  // For production, use the LoadBalancer IP or proxy through nginx
  production: '/api', // Will be proxied by nginx to coordinator agent
  timeout: 60000 // 60 seconds for AI processing
};

// Create axios instance
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'development' 
    ? API_CONFIG.development 
    : API_CONFIG.production, // Use nginx proxy in production
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging and error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.message);
    
    // Handle specific error cases
    if (error.code === 'ECONNABORTED') {
      error.message = 'Request timeout - AI agents may be processing';
    } else if (error.response?.status === 404) {
      error.message = 'API endpoint not found';
    } else if (error.response?.status >= 500) {
      error.message = 'Server error - agents may be unavailable';
    } else if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      error.message = 'Network error - falling back to simulation mode';
    }
    
    return Promise.reject(error);
  }
);

// API Methods
export const financialAPI = {
  // Analyze financial query with AI agents
  analyzeQuery: async (queryData) => {
    const response = await api.post('/analyze', queryData);
    return response.data;
  },

  // Get agent health status
  getHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Get detailed agent status
  getStatus: async () => {
    const response = await api.get('/status');
    return response.data;
  },

  // Get agent capabilities (A2A)
  getCapabilities: async () => {
    const response = await api.get('/a2a/capabilities');
    return response.data;
  }
};

export default api;
