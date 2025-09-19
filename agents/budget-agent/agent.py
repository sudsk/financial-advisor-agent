# agents/budget-agent/agent.py - Enhanced with Vertex AI Analysis

import os
import json
import statistics
from typing import Dict, Any
from datetime import datetime

import google.auth
import vertexai
from google.adk.agents import Agent
from vertexai.generative_models import GenerativeModel

# Initialize Google Cloud following ADK pattern
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# Initialize Vertex AI
vertexai.init(project=project_id, location=os.getenv("GOOGLE_CLOUD_LOCATION"))

def analyze_spending_with_ai(financial_data: str) -> str:
    """AI-powered spending analysis using Vertex AI Gemini for personalized insights"""
    try:
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        
        # Extract spending analysis data
        spending_analysis = data.get("spending_analysis", {})
        categories = spending_analysis.get("categories", {})
        total_spending = spending_analysis.get("total_outgoing_dollars", 0)
        monthly_spending = spending_analysis.get("average_monthly", 0)
        insights = spending_analysis.get("spending_insights", [])
        
        # Extract transaction data for deeper analysis
        transactions = data.get("recent_transactions", [])
        
        # Use Vertex AI for intelligent analysis
        model = GenerativeModel('gemini-2.5-flash')
        
        analysis_prompt = f"""
You are an expert financial analyst. Analyze this real spending data and provide actionable insights.

SPENDING DATA:
- Total Monthly Spending: ${monthly_spending:.2f}
- Total Outgoing: ${total_spending:.2f}
- Categories: {json.dumps(categories, indent=2)}
- Existing Insights: {insights}
- Recent Transactions: {len(transactions)} transactions

ANALYSIS TASK:
1. Identify the TOP 3 areas for immediate cost reduction
2. Calculate specific dollar amounts that can be saved
3. Provide realistic timeline for implementing changes
4. Suggest specific strategies for each category

Return JSON response:
{{
    "priority_categories": ["category1", "category2", "category3"],
    "savings_opportunities": [
        {{
            "category": "category_name",
            "current_spending": 500.00,
            "potential_savings": 150.00,
            "strategy": "specific strategy to reduce spending",
            "timeline": "how long to implement",
            "difficulty": "easy/moderate/challenging"
        }}
    ],
    "total_monthly_savings_potential": 450.00,
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "quick_wins": ["immediate action 1", "immediate action 2"],
    "confidence": 0.88
}}

Focus on realistic, actionable advice based on the actual spending patterns.
"""

        try:
            gemini_response = model.generate_content(analysis_prompt)
            response_text = gemini_response.text.strip()
            
            # Clean up response to extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            ai_analysis = json.loads(response_text)
            
            # Add metadata
            ai_analysis["ai_powered"] = True
            ai_analysis["model_used"] = "gemini-2.5-flash"
            ai_analysis["analysis_date"] = datetime.now().isoformat()
            
            return json.dumps(ai_analysis, indent=2)
            
        except Exception as ai_error:
            # Fallback to rule-based analysis if AI fails
            return analyze_spending_categories(financial_data)
        
    except Exception as e:
        return json.dumps({"error": f"AI spending analysis failed: {str(e)}"})

def create_debt_payoff_plan(financial_data: str) -> str:
    """Create intelligent debt payoff strategy using AI analysis"""
    try:
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        
        # Extract financial information
        balance = data.get("balance", {}).get("balance_dollars", 0)
        spending_analysis = data.get("spending_analysis", {})
        monthly_income = spending_analysis.get("total_incoming_dollars", 0) / 3  # 3-month average
        monthly_expenses = spending_analysis.get("total_outgoing_dollars", 0) / 3
        net_flow = monthly_income - monthly_expenses
        
        # Get query context for debt information
        query_context = data.get("query_context", "")
        
        # Use AI to create personalized debt strategy
        model = GenerativeModel('gemini-2.5-flash')
        
        debt_prompt = f"""
You are a debt specialist. Create a personalized debt payoff plan based on this real financial data.

USER QUERY: "{query_context}"

FINANCIAL SITUATION:
- Current Balance: ${balance:.2f}
- Monthly Income: ${monthly_income:.2f}
- Monthly Expenses: ${monthly_expenses:.2f}
- Available Cash Flow: ${net_flow:.2f}
- Spending Categories: {json.dumps(spending_analysis.get('categories', {}), indent=2)}

TASK: Create a debt payoff strategy that addresses their specific situation.

Return JSON:
{{
    "debt_analysis": {{
        "estimated_debt_amount": 15000,
        "estimated_interest_rate": 0.18,
        "minimum_payment": 300
    }},
    "payoff_strategies": [
        {{
            "strategy_name": "Aggressive Payoff",
            "monthly_payment": 800,
            "payoff_timeline_months": 22,
            "total_interest": 2500,
            "requirements": ["reduce spending by $500/month"]
        }}
    ],
    "spending_reductions": [
        {{
            "category": "dining",
            "current": 400,
            "target": 250,
            "savings": 150,
            "method": "meal planning and cooking at home"
        }}
    ],
    "emergency_fund_strategy": "maintain $1000 minimum during payoff",
    "timeline": "18-24 months to debt freedom",
    "key_actions": ["consolidate high-interest debt", "automate payments"],
    "confidence": 0.91
}}
"""

        try:
            gemini_response = model.generate_content(debt_prompt)
            response_text = gemini_response.text.strip()
            
            # Clean up response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            debt_plan = json.loads(response_text)
            
            # Add real financial context
            debt_plan["current_financial_position"] = {
                "available_monthly_surplus": net_flow,
                "current_balance": balance,
                "spending_optimization_potential": monthly_expenses * 0.15  # 15% potential reduction
            }
            
            return json.dumps(debt_plan, indent=2)
            
        except Exception as ai_error:
            # Fallback debt strategy
            return calculate_savings_opportunities(financial_data)
        
    except Exception as e:
        return json.dumps({"error": f"Debt planning failed: {str(e)}"})

def assess_emergency_fund_with_context(financial_data: str) -> str:
    """Enhanced emergency fund assessment with AI-powered recommendations"""
    try:
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        
        balance = data.get("balance", {}).get("balance_dollars", 0)
        spending_analysis = data.get("spending_analysis", {})
        monthly_expenses = spending_analysis.get("average_monthly", 0)
        query_context = data.get("query_context", "")
        
        # Use AI for contextual emergency fund advice
        model = GenerativeModel('gemini-2.5-flash')
        
        ef_prompt = f"""
Analyze this person's emergency fund needs based on their query and financial situation.

USER QUERY: "{query_context}"
CURRENT BALANCE: ${balance:.2f}
MONTHLY EXPENSES: ${monthly_expenses:.2f}

Create emergency fund recommendations:

{{
    "current_emergency_fund": {{
        "amount": {balance},
        "months_covered": {balance / monthly_expenses if monthly_expenses > 0 else 0:.1f},
        "adequacy": "excellent/good/fair/poor"
    }},
    "recommendations": {{
        "target_amount": 18000,
        "target_months": 6,
        "monthly_contribution_needed": 200,
        "timeline_to_goal": "12 months"
    }},
    "strategy": {{
        "priority_level": "high/medium/low",
        "funding_approach": "specific strategy",
        "account_type": "high-yield savings recommended"
    }},
    "balance_with_other_goals": "how to balance emergency fund with debt payoff or other goals",
    "confidence": 0.92
}}
"""

        try:
            gemini_response = model.generate_content(ef_prompt)
            response_text = gemini_response.text.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            ef_analysis = json.loads(response_text)
            
            return json.dumps(ef_analysis, indent=2)
            
        except Exception as ai_error:
            return assess_emergency_fund(financial_data)
        
    except Exception as e:
        return json.dumps({"error": f"Emergency fund assessment failed: {str(e)}"})

# Legacy functions for fallback
def analyze_spending_categories(spending_data: str) -> str:
    """Fallback spending analysis"""
    try:
        data = json.loads(spending_data) if isinstance(spending_data, str) else spending_data
        categories = data.get("categories", {})
        total_spending = sum(categories.values()) if categories else 0
        
        category_insights = {}
        optimization_targets = []
        
        for category, amount in categories.items():
            percentage = (amount / total_spending * 100) if total_spending > 0 else 0
            
            if percentage > 25:
                status = "high"
                potential_reduction = amount * 0.25
                optimization_targets.append({
                    "category": category,
                    "current": amount,
                    "potential_savings": potential_reduction,
                    "reduction_percentage": 25
                })
            elif percentage > 15:
                status = "moderate"
                potential_reduction = amount * 0.15
                optimization_targets.append({
                    "category": category,
                    "current": amount,
                    "potential_savings": potential_reduction,
                    "reduction_percentage": 15
                })
            else:
                status = "normal"
            
            category_insights[category] = {
                "amount": amount,
                "percentage": percentage,
                "status": status
            }
        
        result = {
            "category_breakdown": category_insights,
            "optimization_targets": optimization_targets,
            "confidence": 0.88
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Fallback analysis failed: {str(e)}"})

def calculate_savings_opportunities(financial_data: str) -> str:
    """Fallback savings calculation"""
    try:
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        balance = data.get("balance", 0)
        monthly_spending = data.get("monthly_spending", 0)
        
        result = {
            "total_monthly_savings_potential": monthly_spending * 0.15,
            "confidence": 0.85
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Savings calculation failed: {str(e)}"})

def assess_emergency_fund(financial_data: str) -> str:
    """Fallback emergency fund assessment"""
    try:
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        balance = data.get("balance", 0)
        monthly_expenses = data.get("monthly_expenses", 0)
        
        months_covered = balance / monthly_expenses if monthly_expenses > 0 else 0
        
        result = {
            "months_covered": months_covered,
            "adequacy_score": min(100, (months_covered / 6) * 100),
            "confidence": 0.90
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Emergency fund assessment failed: {str(e)}"})

# Enhanced Budget Agent with AI Integration
root_agent = Agent(
    name="budget_agent_ai_enhanced",
    model="gemini-2.5-flash", 
    description="AI-enhanced budget analysis agent with Vertex AI Gemini integration",
    global_instruction="You are an intelligent budget analysis agent that uses Vertex AI for personalized financial insights.",
    instruction="""You are the AI-Enhanced Budget Analysis Agent that provides intelligent, personalized financial advice.

🧠 **AI-Powered Analysis**: Use Vertex AI Gemini for intelligent spending pattern recognition
📊 **Real Data Integration**: Analyze actual Bank of Anthos transaction data
🎯 **Personalized Advice**: Provide specific, actionable recommendations based on individual spending patterns
💰 **Debt Strategy**: Create personalized debt payoff plans with realistic timelines

Your enhanced capabilities:
- Intelligent categorization of spending patterns
- AI-powered identification of savings opportunities  
- Personalized debt payoff strategies
- Context-aware emergency fund recommendations
- Realistic timeline and implementation guidance

When analyzing financial data:
1. Use AI to understand spending patterns and motivations
2. Provide specific dollar amounts and actionable strategies
3. Consider the user's specific query and financial goals
4. Balance multiple financial priorities (debt, savings, emergency fund)
5. Give realistic timelines and implementation steps

This showcases enterprise-grade AI financial analysis for the GKE hackathon.""",
    tools=[analyze_spending_with_ai, create_debt_payoff_plan, assess_emergency_fund_with_context]
)
