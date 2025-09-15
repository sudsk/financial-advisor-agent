# agents/budget-agent/main.py
from flask import Flask, request, jsonify
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
from google import generativeai as genai

app = Flask(__name__)

class BudgetAgent:
    def __init__(self, gemini_api_key: str):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_spending_patterns(self, spending_data: Dict) -> Dict:
        """Analyze spending patterns and identify optimization opportunities"""
        
        categories = spending_data.get("categories", {})
        total_spending = spending_data.get("total_spending", 0)
        average_monthly = spending_data.get("average_monthly", 0)
        
        # Calculate category percentages
        category_percentages = {}
        for category, amount in categories.items():
            category_percentages[category] = (amount / total_spending * 100) if total_spending > 0 else 0
        
        # Identify high-spending categories
        high_spend_categories = {k: v for k, v in category_percentages.items() if v > 15}
        
        # Budget recommendations
        recommendations = []
        
        # Dining/Entertainment optimization
        if "Dining" in categories and category_percentages.get("Dining", 0) > 20:
            recommendations.append("Consider reducing dining expenses - currently over 20% of spending")
        
        if "Entertainment" in categories and category_percentages.get("Entertainment", 0) > 15:
            recommendations.append("Entertainment spending could be optimized for better savings")
        
        # Subscription audit
        if "Subscriptions" in categories:
            recommendations.append("Review and cancel unused subscriptions")
        
        return {
            "category_breakdown": category_percentages,
            "high_spend_areas": high_spend_categories,
            "monthly_average": average_monthly,
            "optimization_opportunities": recommendations
        }
    
    def create_savings_plan(self, current_spending: float, savings_goal: float, timeline_months: int) -> Dict:
        """Create a realistic savings plan"""
        
        monthly_savings_needed = savings_goal / timeline_months
        current_monthly_spending = current_spending
        
        # Calculate required spending reduction
        spending_reduction_needed = monthly_savings_needed
        reduction_percentage = (spending_reduction_needed / current_monthly_spending * 100) if current_monthly_spending > 0 else 0
        
        plan = {
            "monthly_savings_target": monthly_savings_needed,
            "spending_reduction_needed": spending_reduction_needed,
            "reduction_percentage": reduction_percentage,
            "feasibility": "high" if reduction_percentage < 15 else "medium" if reduction_percentage < 25 else "challenging"
        }
        
        return plan
    
    async def generate_budget_recommendations(self, user_data: Dict, context: Dict) -> Dict:
        """Generate personalized budget recommendations using Gemini"""
        
        spending_analysis = user_data.get("spending_analysis", {})
        balance = user_data.get("balance", {})
        
        prompt = f"""
        As a financial budget expert, analyze this user's spending and provide recommendations:
        
        Current Financial Situation:
        - Account Balance: ${balance.get('amount', 0)}
        - Monthly Spending: ${spending_analysis.get('average_monthly', 0)}
        - Spending Categories: {spending_analysis.get('categories', {})}
        
        User Context: {json.dumps(context, indent=2)}
        
        Provide budget advice in JSON format:
        {{
            "budget_assessment": "Overall assessment of current budget health",
            "spending_insights": ["Key insights about spending patterns"],
            "optimization_areas": ["Specific areas where user can save money"],
            "recommended_budget": {{"category": monthly_amount}},
            "savings_opportunities": ["Actionable ways to save money"],
            "budget_targets": {{"category": "recommended_percentage_of_income"}},
            "confidence": 0.85
        }}
        
        Focus on practical, achievable recommendations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            
            # Add our analysis
            spending_pattern_analysis = self.analyze_spending_patterns(spending_analysis)
            result.update({
                "detailed_analysis": spending_pattern_analysis,
                "agent_type": "budget",
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            return {
                "error": f"Budget analysis failed: {str(e)}",
                "confidence": 0.0,
                "recommendations": ["Unable to analyze budget at this time"]
            }

# Global agent instance
budget_agent = BudgetAgent(gemini_api_key="YOUR_GEMINI_API_KEY")  # Replace with actual key

@app.route('/analyze', methods=['POST'])
async def analyze_budget():
    """A2A Protocol endpoint for budget analysis"""
    try:
        data = request.get_json()
        
        user_data = data.get("user_data", {})
        context = data.get("context", {})
        requesting_agent = data.get("requesting_agent", "unknown")
        
        # Perform budget analysis
        result = await budget_agent.generate_budget_recommendations(user_data, context)
        
        # A2A Protocol response format
        response = {
            "agent_type": "budget",
            "requesting_agent": requesting_agent,
            "result": result,
            "confidence": result.get("confidence", 0.8),
            "recommendations": result.get("savings_opportunities", []),
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "agent_type": "budget", 
            "error": str(e),
            "confidence": 0.0,
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "agent": "budget",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
