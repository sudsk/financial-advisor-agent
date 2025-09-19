// ui/src/hooks/useFinancialAdvisor.js
import { useState, useCallback, useRef } from 'react';
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
const updateAgentStatus = useCallback((agentId, status, statusText, confidence = 0) => {
  console.log(`🔥 UPDATING AGENT: ${agentId} to ${status}`); // ADD THIS
  setAgentStatuses(prev => ({
    ...prev,
    [agentId]: { status, statusText, confidence }
  }));
}, []);

useEffect(() => {
  console.log(`🎯 AGENT STATUSES CHANGED:`, agentStatuses); // ADD THIS
}, [agentStatuses]);

// Mock data for demo purposes when API is unavailable
const mockResponses = {
  house: {
    summary: "Based on your house-saving goal, our AI agents recommend a balanced approach combining aggressive savings, strategic investments, and risk management to reach your down payment target.",
    detailed_plan: [
      "Reduce discretionary spending by 20% ($900/month) to increase savings rate",
      "Invest 60% in low-cost index funds, 30% in bonds, 10% in high-yield savings",
      "Set up automatic transfers to separate house fund account",
      "Consider increasing income through side projects or career advancement",
      "Target timeline: 36 months with $2,222/month savings required"
    ],
    key_insights: [
      "Budget Agent: You can save an additional $900/month through category optimization",
      "Investment Agent: Moderate-risk portfolio can achieve 6-7% annual returns",
      "Security Agent: Current spending patterns show manageable financial risk",
      "Coordinator: Goal is achievable with disciplined execution"
    ],
    next_actions: [
      "Schedule monthly budget review meetings",
      "Set up automatic investment transfers",
      "Research and compare investment platforms",
      "Track progress with financial dashboard"
    ],
    adk_metadata: {
      coordinator_id: "coordinator-001",
      agents_coordinated: ["budget-001", "investment-001", "security-001"],
      processing_time_ms: 4250,
      registry_status: 3
    }
  },
  retirement: {
    summary: "For retirement planning at age 35, our agents recommend a long-term wealth building strategy focused on tax-advantaged accounts and diversified growth investments.",
    detailed_plan: [
      "Maximize 401(k) contributions to employer match",
      "Open and fund Roth IRA with $6,000 annual contribution",
      "Invest in growth-focused portfolio: 80% stocks, 20% bonds",
      "Increase savings rate by 2% annually",
      "Plan for 25x annual expenses by age 60"
    ],
    key_insights: [
      "Budget Agent: Current spending allows for 15-20% savings rate",
      "Investment Agent: 25-year timeline allows for aggressive growth strategy",
      "Security Agent: Diversification reduces long-term risk",
      "Coordinator: On track for comfortable retirement with current plan"
    ],
    next_actions: [
      "Open retirement accounts if not already done",
      "Set up automatic contributions",
      "Review and rebalance annually",
      "Track progress toward retirement goals"
    ]
  },
  debt: {
    summary: "For debt optimization, our agents recommend the avalanche method combined with strategic budgeting to eliminate high-interest debt while maintaining emergency savings.",
    detailed_plan: [
      "Pay minimum on all debts, extra on highest interest debt first",
      "Reduce non-essential spending by 25% ($1,125/month)",
      "Apply $800/month extra to credit card debt",
      "Maintain $1,000 emergency fund during debt payoff",
      "Timeline: 18-24 months to eliminate debt"
    ],
    key_insights: [
      "Budget Agent: Identified $1,125 in potential monthly savings",
      "Investment Agent: Focus on debt elimination before investing",
      "Security Agent: High-interest debt is primary financial risk",
      "Coordinator: Debt-free status achievable within 2 years"
    ]
  },
  investment: {
    summary: "For your investment strategy, our agents recommend a balanced approach emphasizing diversification, low costs, and risk-appropriate allocation for your timeline and goals.",
    detailed_plan: [
      "Allocate across asset classes: 70% stocks, 25% bonds, 5% cash",
      "Use low-cost index funds and ETFs",
      "Dollar-cost average over 6-12 months",
      "Rebalance quarterly to maintain target allocation",
      "Consider tax-loss harvesting opportunities"
    ],
    key_insights: [
      "Budget Agent: Investment fits within available cash flow",
      "Investment Agent: Moderate allocation balances growth and safety",
      "Security Agent: Diversification reduces concentration risk",
      "Coordinator: Strategy aligns with risk tolerance and timeline"
    ]
  }
};

const getScenarioType = (query) => {
  const queryLower = query.toLowerCase();
  if (queryLower.includes('house') || queryLower.includes('home')) return 'house';
  if (queryLower.includes('retire') || queryLower.includes('retirement')) return 'retirement';
  if (queryLower.includes('debt') || queryLower.includes('credit card')) return 'debt';
  if (queryLower.includes('invest') || queryLower.includes('portfolio')) return 'investment';
  return 'house'; // default
};

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

  const updateAgentStatus = useCallback((agentId, status, statusText, confidence = 0) => {
    setAgentStatuses(prev => ({
      ...prev,
      [agentId]: { status, statusText, confidence }
    }));
  }, []);

  const resetAgentStatuses = useCallback(() => {
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

  const simulateAgentCoordination = useCallback((query) => {
    return new Promise((resolve) => {
      // Reset statuses
      resetAgentStatuses();
      
      // Simulate realistic agent coordination timing
      const timeouts = [
        setTimeout(() => updateAgentStatus('coordinator', 'processing', 'Analyzing query...', 0.1), 500),
        setTimeout(() => updateAgentStatus('budget', 'processing', 'Analyzing spending...', 0.3), 1500),
        setTimeout(() => updateAgentStatus('investment', 'processing', 'Evaluating options...', 0.5), 2500),
        setTimeout(() => updateAgentStatus('security', 'processing', 'Risk assessment...', 0.7), 3500),
        setTimeout(() => {
          updateAgentStatus('coordinator', 'active', 'Analysis complete', 0.92);
          updateAgentStatus('budget', 'active', 'Recommendations ready', 0.88);
          updateAgentStatus('investment', 'active', 'Strategy prepared', 0.91);
          updateAgentStatus('security', 'active', 'Risk evaluated', 0.95);
          
          const scenarioType = getScenarioType(query);
          const response = mockResponses[scenarioType];
          resolve(response);
        }, 5000)
      ];
      
      statusTimeoutRef.current = timeouts;
    });
  }, [updateAgentStatus, resetAgentStatuses]);

  const analyzeQuery = useCallback(async (queryData) => {
    setIsLoading(true);
    setError(null);
    setResults(null);
    
    try {
      // Try real API first
      let response;
      try {
        console.log('Attempting to call ADK Coordinator API...');
        const apiResponse = await api.post('/analyze', queryData);
        response = apiResponse.data.result || apiResponse.data;
        console.log('API call successful:', response);
      } catch (apiError) {
        console.log('API call failed, falling back to simulation:', apiError.message);
        // Fallback to simulation
        response = await simulateAgentCoordination(queryData.query);
      }
      
      setResults(response);
      
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.response?.data?.error || err.message || 'Failed to analyze query');
      resetAgentStatuses();
    } finally {
      setIsLoading(false);
    }
  }, [simulateAgentCoordination, resetAgentStatuses]);

  const resetAnalysis = useCallback(() => {
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
      return response.data;
    } catch (err) {
      console.error('Health check failed:', err);
      return null;
    }
  }, []);

  const getDetailedStatus = useCallback(async () => {
    try {
      const response = await api.get('/status');
      return response.data;
    } catch (err) {
      console.error('Status check failed:', err);
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
