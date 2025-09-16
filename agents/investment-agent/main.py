# agents/investment-agent/main.py
from flask import Flask, request, jsonify
import asyncio
from datetime import datetime
from typing import Dict, List, Any
import json
import os
import vertexai
from vertexai.generative_models import GenerativeModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class InvestmentAgent:
    def __init__(self, project_id: str, region: str):
        self.project_id = project_id
        self.region = region
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=region)
        self.model = GenerativeModel('gemini-pro')
        logger.info(f"Investment Agent initialized with project {project_id} in region {region}")
    
    def calculate_investment_capacity(self, user_data: Dict) -> Dict:
        """Calculate user's investment capacity based on financial data"""
        
        balance = user_data.get("balance", {}).get("amount", 0)
        spending_analysis = user_data.get("spending_analysis", {})
        monthly_spending = spending_analysis.get("average_monthly", 0)
        
        # Calculate disposable income (simplified)
        emergency_fund_needed = monthly_spending * 6  # 6 months emergency fund
        available_for_investment = max(0, balance - emergency_fund_needed)
        
        # Calculate monthly investment capacity (20% of remaining after expenses)
        monthly_investment_capacity = max(0, (monthly_spending * 0.2))
        
        return {
            "current_investable_amount": available_for_investment,
            "monthly_investment_capacity": monthly_investment_capacity,
            "emergency_fund_status": balance >= emergency_fund_needed,
            "emergency_fund_gap": max(0, emergency_fund_needed - balance),
            "investment_readiness_score": min(1.0, balance / (monthly_spending * 3)) if monthly_spending > 0 else 0
        }
    
    def generate_portfolio_allocation(self, risk_profile: str, investment_amount: float, time_horizon: int) -> Dict:
        """Generate portfolio allocation based on risk profile and time horizon"""
        
        allocations = {
            "conservative": {
                "stocks": 30,
                "bonds": 50,
                "cash": 20,
                "expected_return": 0.05
            },
            "moderate": {
                "stocks": 60,
                "bonds": 30,
                "cash": 10,
                "expected_return": 0.07
            },
            "aggressive": {
                "stocks": 80,
                "bonds": 15,
                "cash": 5,
                "expected_return": 0.09
            }
        }
        
        # Adjust allocation based on time horizon
        allocation = allocations.get(risk_profile, allocations["moderate"]).copy()
        
        if time_horizon < 3:  # Short term - more conservative
            allocation["cash"] += 10
            allocation["stocks"] -= 10
            allocation["expected_return"] -= 0.01
        elif time_horizon > 10:  # Long term - can be more aggressive
            allocation["stocks"] += 5
            allocation["bonds"] -= 5
            allocation["expected_return"] += 0.005
        
        return allocation
    
    async def generate_investment_recommendations(self, user_data: Dict, context: Dict) -> Dict:
        """Generate personalized investment recommendations using Vertex AI Gemini"""
        
        balance = user_data.get("balance", {})
        spending_analysis = user_data.get("spending_analysis", {})
        profile = user_data.get("profile", {})
        
        # Calculate investment capacity
        investment_capacity = self.calculate_investment_capacity(user_data)
        
        prompt = f"""
        As an expert investment advisor, analyze this user's financial situation and provide investment recommendations:
        
        Financial Situation:
        - Current Balance: ${balance.get('amount', 0)}
        - Monthly Spending: ${spending_analysis.get('average_monthly', 0)}
        - Investment Capacity: ${investment_capacity['current_investable_amount']}
        - Monthly Investment Capacity: ${investment_capacity['monthly_investment_capacity']}
        - Emergency Fund Status: {investment_capacity['emergency_fund_status']}
        
        User Profile: {json.dumps(profile, indent=2)}
        Context: {json.dumps(context, indent=2)}
        
        Provide investment advice in JSON format:
        {{
            "investment_assessment": "Overall assessment of investment readiness",
            "recommended_strategy": "Primary investment strategy recommendation",
            "portfolio_allocation": {{"asset_class": "percentage"}},
            "specific_recommendations": ["Specific investment products or actions"],
            "risk_considerations": ["Important risks to consider"],
            "timeline_strategy": {{"timeframe": "strategy"}},
            "tax_optimization": ["Tax-efficient investment strategies"],
            "rebalancing_schedule": "How often to review and rebalance",
            "confidence": 0.85
        }}
        
        Focus on practical, low-cost, diversified investment strategies.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            
            # Add our calculated data
            result.update({
                "investment_capacity_analysis": investment_capacity,
                "agent_type": "investment",
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Investment analysis failed: {str(e)}")
            return {
                "error": f"Investment analysis failed: {str(e)}",
                "confidence": 0.0,
                "recommendations": ["Unable to provide investment recommendations at this time"]
            }

# Initialize agent with environment variables
PROJECT_ID = os.getenv('PROJECT_ID', 'your-project-id')
REGION = os.getenv('REGION', 'us-central1')

investment_agent = InvestmentAgent(PROJECT_ID, REGION)

@app.route('/recommend', methods=['POST'])
async def recommend_investments():
    """A2A Protocol endpoint for investment recommendations"""
    try:
        data = request.get_json()
        
        user_data = data.get("user_data", {})
        context = data.get("context", {})
        requesting_agent = data.get("requesting_agent", "unknown")
        
        # Perform investment analysis
        result = await investment_agent.generate_investment_recommendations(user_data, context)
        
        # A2A Protocol response format
        response = {
            "agent_type": "investment",
            "requesting_agent": requesting_agent,
            "result": result,
            "confidence": result.get("confidence", 0.8),
            "recommendations": result.get("specific_recommendations", []),
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Investment recommendation error: {str(e)}")
        return jsonify({
            "agent_type": "investment",
            "error": str(e),
            "confidence": 0.0,
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "agent": "investment",
        "status": "healthy",
        "project_id": PROJECT_ID,
        "region": REGION,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
