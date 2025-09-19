// ui/src/hooks/useFinancialAdvisor.js - Updated with decoupled visual simulation
import { useState, useCallback, useRef, useEffect } from 'react';
import axios from 'axios';

// Configure axios defaults
const api = axios.create({
  baseURL: process.env.NODE_ENV === 'development' 
    ? 'http://localhost:8080'
    : '/api', // Use nginx proxy instead of direct K8s DNS
  timeout: 60000, // 60 second timeout for AI processing
  headers: {
    'Content-Type': 'application/json',
  }
});

export function useFinancialAdvisor() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [agentStatuses, setAgentStatuses] = useState({
    coordinator: { status: 'ready', statusText: 'Ready', confidence: 0 },
    budget: { status: 'ready', statusText: 'Ready', confidence: 0 },
    investment: { status: 'ready', statusText: 'Ready', confidence: 0 },
    security: { status: 'ready', statusText: 'Ready', confidence: 0 }
  });

  const statusTimeoutRef = useRef([]);

  // 🔍 DEBUG: Monitor agent status changes
  useEffect(() => {
    console.log(`🎯 AGENT STATUSES CHANGED:`, agentStatuses);
  }, [agentStatuses]);

  const updateAgentStatus = useCallback((agentId, status, statusText, confidence = 0) => {
    console.log(`🔥 UPDATING AGENT: ${agentId} to ${status}`); // DEBUG
    setAgentStatuses(prev => ({
      ...prev,
      [agentId]: { status, statusText, confidence }
    }));
  }, []);

  const resetAgentStatuses = useCallback(() => {
    console.log('🔄 RESETTING AGENT STATUSES'); // DEBUG
    setAgentStatuses({
      coordinator: { status: 'ready', statusText: 'Ready', confidence: 0 },
      budget: { status: 'ready', statusText: 'Ready', confidence: 0 },
      investment: { status: 'ready', statusText: 'Ready', confidence: 0 },
      security: { status: 'ready', statusText: 'Ready', confidence: 0 }
    });
    
    // Clear any existing timeouts
    statusTimeoutRef.current.forEach(clearTimeout);
    statusTimeoutRef.current = [];
  }, []);

  const startVisualSimulation = useCallback(() => {
    console.log('🎬 STARTING VISUAL SIMULATION'); // DEBUG
    
    // Reset statuses first
    resetAgentStatuses();
    
    // Create realistic agent coordination timing for demo
    const timeouts = [
      setTimeout(() => {
        console.log('🎬 Coordinator starts processing'); // DEBUG
        updateAgentStatus('coordinator', 'processing', 'Analyzing query...', 0.1);
      }, 500),
      
      setTimeout(() => {
        console.log('🎬 Budget agent processing'); // DEBUG
        updateAgentStatus('budget', 'processing', 'Analyzing spending...', 0.3);
      }, 1500),
      
      setTimeout(() => {
        console.log('🎬 Investment agent processing'); // DEBUG
        updateAgentStatus('investment', 'processing', 'Evaluating options...', 0.5);
      }, 2500),
      
      setTimeout(() => {
        console.log('🎬 Security agent processing'); // DEBUG
        updateAgentStatus('security', 'processing', 'Risk assessment...', 0.7);
      }, 3500),
      
      // Agents complete, coordinator starts synthesis
      setTimeout(() => {
        console.log('🎬 Agents completing, coordinator synthesizing'); // DEBUG
        updateAgentStatus('budget', 'active', 'Analysis complete', 0.88);
        updateAgentStatus('investment', 'active', 'Strategy ready', 0.91);
        updateAgentStatus('security', 'active', 'Risk evaluated', 0.95);
        updateAgentStatus('coordinator', 'processing', 'Synthesizing results...', 0.8);
      }, 4500),
      
      // Coordinator completes synthesis (set when real API completes)
      setTimeout(() => {
        console.log('🎬 Coordinator synthesis complete'); // DEBUG
        updateAgentStatus('coordinator', 'active', 'Analysis complete', 0.92);
      }, 6000)
    ];
    
    statusTimeoutRef.current = timeouts;
  }, [updateAgentStatus, resetAgentStatuses]);

  const analyzeQuery = useCallback(async (queryData) => {
    console.log('🚀 STARTING ANALYSIS:', queryData); // DEBUG
    
    setIsLoading(true);
    setError(null);
    setResults(null);
    
    // 🎭 ALWAYS start visual simulation for demo purposes
    startVisualSimulation();
    
    try {
      console.log('📡 Calling real API...'); // DEBUG
      
      // Try real API call to coordinator
      const apiResponse = await api.post('/analyze', queryData);
      const response = apiResponse.data.result || apiResponse.data;
      
      console.log('✅ Real API successful:', response); // DEBUG
      setResults(response);
      
    } catch (err) {
      console.error('❌ API Error:', err.message); // DEBUG
      
      // On API failure, create a basic fallback response
      const fallbackResponse = {
        summary: `Analysis request received for: ${queryData.query}. Unable to connect to AI agents at this time.`,
        detailed_plan: [
          "API connection to coordinator agent failed",
          "Please check that all services are running",
          "Try again in a few moments"
        ],
        key_insights: [
          "System is in demo mode",
          "Visual agent coordination is simulated",
          "Backend services may be starting up"
        ],
        next_actions: [
          "Verify GKE deployment status",
          "Check coordinator agent logs",
          "Ensure MCP server connectivity"
        ],
        monitoring: "Check kubectl get pods -n financial-advisor for service status",
        timeline: "Services should be available within 2-3 minutes",
        coordination_metadata: {
          error: true,
          message: "Demo mode - visual simulation only",
          timestamp: new Date().toISOString()
        }
      };
      
      setResults(fallbackResponse);
      setError(`API unavailable: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [startVisualSimulation]);

  const resetAnalysis = useCallback(() => {
    console.log('🔄 RESETTING ANALYSIS'); // DEBUG
    setResults(null);
    setError(null);
    resetAgentStatuses();
    
    // Clear timeouts
    statusTimeoutRef.current.forEach(clearTimeout);
    statusTimeoutRef.current = [];
  }, [resetAgentStatuses]);

  const getAgentHealth = useCallback(async () => {
    try {
      const response = await api.get('/health');
      console.log('💊 Health check successful:', response.data); // DEBUG
      return response.data;
    } catch (err) {
      console.error('💊 Health check failed:', err); // DEBUG
      return null;
    }
  }, []);

  const getDetailedStatus = useCallback(async () => {
    try {
      const response = await api.get('/status');
      console.log('📊 Status check successful:', response.data); // DEBUG
      return response.data;
    } catch (err) {
      console.error('📊 Status check failed:', err); // DEBUG
      return null;
    }
  }, []);

  return {
    isLoading,
    results,
    error,
    agentStatuses,
    analyzeQuery,
    resetAnalysis,
    getAgentHealth,
    getDetailedStatus
  };
}
