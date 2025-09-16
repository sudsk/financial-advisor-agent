// ui/app.js
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8080' 
    : 'http://coordinator-agent.financial-advisor.svc.cluster.local:8080';

const demoScenarios = {
    house: "Help me save $80,000 for a house down payment in 3 years. I currently spend about $4,500 per month.",
    retirement: "I'm 35 years old and want to retire comfortably at 60. What's my best investment strategy?",
    debt: "I have $15,000 in credit card debt at 18% interest. How should I pay this off while still saving?",
    investment: "I have $25,000 to invest and want to balance growth with safety. What do you recommend?"
};

function loadDemoScenario(scenario) {
    document.getElementById('query').value = demoScenarios[scenario];
}

function updateAgentStatus(agentId, status, statusText) {
    const agent = document.getElementById(agentId);
    if (agent) {
        agent.className = `agent-card ${status}`;
        const statusElement = agent.querySelector('.agent-status-text');
        if (statusElement) {
            statusElement.textContent = statusText;
        }
    }
}

function resetAgentStatus() {
    const agents = ['coordinator-agent', 'budget-agent', 'investment-agent', 'security-agent'];
    agents.forEach(agentId => {
        updateAgentStatus(agentId, '', 'Ready');
    });
}

async function analyzeFinancialQuery() {
    const userId = document.getElementById('userId').value;
    const accountId = document.getElementById('accountId').value;
    const query = document.getElementById('query').value;
    
    if (!userId || !accountId || !query) {
        alert('Please fill in all fields');
        return;
    }
    
    // Reset UI
    document.getElementById('analyzeBtn').disabled = true;
    document.getElementById('loadingSection').classList.add('active');
    document.getElementById('resultsSection').style.display = 'none';
    resetAgentStatus();
    
    // Simulate agent coordination process with realistic timing
    setTimeout(() => updateAgentStatus('coordinator-agent', 'processing', 'Analyzing query...'), 500);
    setTimeout(() => updateAgentStatus('budget-agent', 'processing', 'Analyzing spending...'), 1500);
    setTimeout(() => updateAgentStatus('investment-agent', 'processing', 'Evaluating options...'), 2500);
    setTimeout(() => updateAgentStatus('security-agent', 'processing', 'Risk assessment...'), 3500);
    
    try {
        // Try to call the actual coordinator agent, fallback to simulation
        let response;
        try {
            const apiResponse = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    account_id: accountId,
                    query: query
                }),
                timeout: 30000 // 30 second timeout
            });
            
            if (apiResponse.ok) {
                const apiResult = await apiResponse.json();
                response = apiResult.result || apiResult;
            } else {
                throw new Error(`API returned ${apiResponse.status}`);
            }
        } catch (apiError) {
            console.log('API call failed, using simulation:', apiError.message);
            // Fallback to simulation for demo purposes
            response = await simulateAgentCoordination(userId, accountId, query);
        }
        
        // Update agent status to completed
        setTimeout(() => {
            updateAgentStatus('coordinator-agent', 'active', 'Analysis complete');
            updateAgentStatus('budget-agent', 'active', 'Recommendations ready');
            updateAgentStatus('investment-agent', 'active', 'Strategy prepared');
            updateAgentStatus('security-agent', 'active', 'Risk evaluated');
        }, 4500);
        
        // Show results
        setTimeout(() => {
            displayResults(response);
            document.getElementById('loadingSection').classList.remove('active');
            document.getElementById('resultsSection').style.display = 'block';
            document.getElementById('analyzeBtn').disabled = false;
        }, 5000);
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loadingSection').classList.remove('active');
        document.getElementById('analyzeBtn').disabled = false;
        resetAgentStatus();
        alert('Error analyzing financial query. Please try again.');
    }
}

async function simulateAgentCoordination(userId, accountId, query) {
    // Simulate realistic delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Generate contextual response based on query
    const queryLower = query.toLowerCase();
    let scenarioType = 'general';
    
    if (queryLower.includes('house') || queryLower.includes('home')) {
        scenarioType = 'house';
    } else if (queryLower.includes('retire') || queryLower.includes('retirement')) {
        scenarioType = 'retirement';
    } else if (queryLower.includes('debt') || queryLower.includes('credit card')) {
        scenarioType = 'debt';
    } else if (queryLower.includes('invest') || queryLower.includes('portfolio')) {
        scenarioType = 'investment';
    }
    
    const responses = {
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
            ]
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
        },
        general: {
            summary: "Based on your financial situation, our AI agents recommend a comprehensive approach combining budget optimization, strategic investments, and risk management.",
            detailed_plan: [
                "Create detailed budget tracking all income and expenses",
                "Build emergency fund covering 6 months of expenses",
                "Invest in diversified portfolio matching risk tolerance",
                "Review and adjust plan quarterly",
                "Consider tax optimization strategies"
            ],
            key_insights: [
                "Budget Agent: Spending patterns show opportunities for optimization",
                "Investment Agent: Balanced approach recommended for current situation",
                "Security Agent: Overall financial health appears stable",
                "Coordinator: Foundation exists for achieving financial goals"
            ]
        }
    };
    
    const response = responses[scenarioType];
    response.next_actions = [
        "Schedule monthly budget review meetings",
        "Set up automatic investment transfers",
        "Research and compare investment platforms",
        "Track progress with financial dashboard"
    ];
    
    response.monitoring = "We'll track your progress monthly and adjust recommendations based on changing circumstances";
    response.metadata = {
        agents_used: ["coordinator", "budget", "investment", "security"],
        confidence_scores: {
            budget: 0.92,
            investment: 0.88,
            security: 0.95,
            coordinator: 0.90
        },
        scenario_type: scenarioType
    };
    
    return response;
}

function displayResults(results) {
    const content = document.getElementById('resultsContent');
    
    if (!results || typeof results !== 'object') {
        content.innerHTML = '<div class="error">Error: Invalid response from agents</div>';
        return;
    }
    
    const summary = results.summary || 'Analysis completed by our AI agents.';
    const detailed_plan = results.detailed_plan || [];
    const key_insights = results.key_insights || [];
    const next_actions = results.next_actions || [];
    const metadata = results.metadata || {};
    const confidence_scores = metadata.confidence_scores || {};
    
    content.innerHTML = `
        <div class="recommendation-card">
            <div class="recommendation-title">💡 Executive Summary</div>
            <div class="recommendation-content">${summary}</div>
        </div>
        
        <div class="recommendation-card">
            <div class="recommendation-title">📋 Action Plan</div>
            <div class="recommendation-content">
                <ul>
                    ${detailed_plan.map(plan => `<li>${plan}</li>`).join('')}
                </ul>
            </div>
        </div>
        
        <div class="recommendation-card">
            <div class="recommendation-title">🔍 Agent Insights</div>
            <div class="recommendation-content">
                <ul>
                    ${key_insights.map(insight => `<li>${insight}</li>`).join('')}
                </ul>
            </div>
            <div style="margin-top: 15px;">
                ${Object.entries(confidence_scores).map(([agent, score]) => 
                    `<span class="confidence-score">${agent}: ${Math.round(score * 100)}% confidence</span>`
                ).join(' ')}
            </div>
        </div>
        
        ${next_actions.length > 0 ? `
        <div class="recommendation-card">
            <div class="recommendation-title">🎯 Next Steps</div>
            <div class="recommendation-content">
                <ul>
                    ${next_actions.map(action => `<li>${action}</li>`).join('')}
                </ul>
            </div>
        </div>
        ` : ''}
    `;
}

// Initialize demo when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadDemoScenario('house');
    
    // Add keyboard support for demo buttons
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.id === 'query') {
            analyzeFinancialQuery();
        }
    });
    
    // Auto-resize textarea
    const textarea = document.getElementById('query');
    if (textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
});
