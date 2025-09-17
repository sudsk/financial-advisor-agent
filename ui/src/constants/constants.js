// ui/src/constants/index.js
export const DEMO_SCENARIOS = {
  HOUSE: {
    key: 'house',
    title: 'Save for House Down Payment',
    description: 'Plan to save $80k in 3 years with current spending analysis',
    query: "Help me save $80,000 for a house down payment in 3 years. I currently spend about $4,500 per month.",
    icon: '🏠'
  },
  RETIREMENT: {
    key: 'retirement',
    title: 'Retirement Planning Strategy',
    description: 'Long-term wealth building from age 35 to comfortable retirement',
    query: "I'm 35 years old and want to retire comfortably at 60. What's my best investment strategy?",
    icon: '🏖️'
  },
  DEBT: {
    key: 'debt',
    title: 'Debt Optimization Plan',
    description: 'Eliminate high-interest debt while maintaining emergency savings',
    query: "I have $15,000 in credit card debt at 18% interest. How should I pay this off while still saving?",
    icon: '💳'
  },
  INVESTMENT: {
    key: 'investment',
    title: 'Investment Portfolio Strategy',
    description: 'Balance growth and safety with diversified investment approach',
    query: "I have $25,000 to invest and want to balance growth with safety. What do you recommend?",
    icon: '💼'
  }
};

export const AGENT_TYPES = {
  COORDINATOR: 'coordinator',
  BUDGET: 'budget',
  INVESTMENT: 'investment',
  SECURITY: 'security'
};

export const AGENT_STATUS = {
  READY: 'ready',
  PROCESSING: 'processing',
  ACTIVE: 'active',
  ERROR: 'error'
};

export const API_ENDPOINTS = {
  ANALYZE: '/analyze',
  HEALTH: '/health',
  STATUS: '/status',
  CAPABILITIES: '/a2a/capabilities'
};

export const UI_CONFIG = {
  ANIMATION_DURATION: 300,
  PROCESSING_TIMEOUT: 60000,
  POLLING_INTERVAL: 2000
};

export const TECH_STACK = [
  {
    label: 'ADK (Agent Development Kit)',
    description: 'Agent lifecycle management and coordination framework',
    color: '#667eea'
  },
  {
    label: 'MCP (Model Context Protocol)',
    description: 'Seamless integration with Bank of Anthos APIs',
    color: '#764ba2'
  },
  {
    label: 'A2A (Agent-to-Agent)',
    description: 'Inter-agent communication and coordination protocol',
    color: '#17a2b8'
  },
  {
    label: 'Vertex AI Gemini',
    description: 'Advanced natural language processing and analysis',
    color: '#28a745'
  },
  {
    label: 'GKE Autopilot',
    description: 'Auto-scaling Kubernetes container orchestration',
    color: '#ffc107'
  },
  {
    label: 'Workload Identity',
    description: 'Secure authentication without API key management',
    color: '#dc3545'
  }
];
