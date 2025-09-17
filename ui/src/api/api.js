// ui/src/api/api.js
import axios from 'axios';

// API Configuration
const API_CONFIG = {
  development: 'http://localhost:8080',
  production: 'http://coordinator-agent.financial-advisor.svc.cluster.local:8080',
  timeout: 60000 // 60 seconds for AI processing
};

// Create axios instance
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'development' 
    ? API_CONFIG.development 
    : API_CONFIG.production,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
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
