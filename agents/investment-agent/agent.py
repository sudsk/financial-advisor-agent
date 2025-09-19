# agents/investment-agent/agent.py - Enhanced with Vertex AI Intelligence

import os
import json
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

def analyze_investment_profile_with_ai(financial_data: str) -> str:
    """AI-powered investment profile analysis using real financial data and user context"""
    try:
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        
        # Extract financial context
        balance = data.get("balance", {}).get("balance_dollars", 0)
        spending_analysis = data.get("spending_analysis", {})
        monthly_income = spending_analysis.get("total_incoming_dollars", 0) / 3
        monthly_expenses = spending_analysis.get("total_outgoing_dollars", 0) / 3
        net_flow = monthly_income - monthly_expenses
        query_context = data.get("query_context", "")
        
        # Analyze spending patterns for investment insights
        categories = spending_analysis.get("categories", {})
        spending_stability = analyze_spending_stability(categories)
        
        # Use Vertex AI for intelligent investment analysis
        model = GenerativeModel('gemini-2.5-flash')
        
        investment_prompt = f"""
You are an expert investment advisor. Analyze this person's real financial situation and provide personalized investment recommendations.

USER QUERY: "{query_context}"

REAL FINANCIAL DATA:
- Current Balance: ${balance:.2f}
- Monthly Income: ${monthly_income:.2f}
- Monthly Expenses: ${monthly_expenses:.2f}
- Available Cash Flow: ${net_flow:.2f}
- Spending Categories: {json.dumps(categories, indent=2)}
- Spending Stability: {spending_stability}

TASK: Create personalized investment strategy based on their specific situation and query.

Return JSON response:
{{
    "risk_profile": {{
        "risk_tolerance": "conservative/moderate/aggressive",
        "risk_capacity": "low/medium/high",
        "time_horizon": "short/medium/long",
        "reasoning": "why this risk profile fits their situation"
    }},
    "investment_strategy": {{
        "recommended_allocation": {{
            "stocks": 70,
            "bonds": 25,
            "cash": 5
        }},
        "monthly_investment_amount": 500,
        "investment_priority": "emergency fund/debt payoff/retirement/house fund",
        "specific_recommendations": ["recommendation 1", "recommendation 2"]
    }},
    "portfolio_suggestions": [
        {{
            "investment_type": "index fund",
            "allocation_percentage": 40,
            "rationale": "why this fits their situation",
            "specific_funds": ["fund suggestions"]
        }}
    ],
    "timeline_strategy": {{
        "immediate_actions": ["action 1", "action 2"],
        "6_month_goals": ["goal 1", "goal 2"],
        "1_year_targets": ["target 1", "target 2"]
    }},
    "risk_considerations": ["specific risk for their situation"],
    "confidence": 0.91
}}

Focus on their specific query: "{query_context}"
Consider their actual spending patterns and financial stability.
"""

        try:
            gemini_response = model.generate_content(investment_prompt)
            response_text = gemini_response.text.strip()
            
            # Clean up response to extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            investment_analysis = json.loads(response_text)
            
            # Add financial context
            investment_analysis["financial_context"] = {
                "available_monthly_surplus": net_flow,
                "current_liquidity": balance,
                "spending_pattern_analysis": spending_stability,
                "investment_readiness_score": calculate_investment_readiness(balance, net_flow, categories)
            }
            
            investment_analysis["ai_powered"] = True
            investment_analysis["model_used"] = "gemini-2.5-flash"
            
            return json.dumps(investment_analysis, indent=2)
            
        except Exception as ai_error:
            # Fallback to rule-based analysis
            return assess_risk_profile(financial_data)
        
    except Exception as e:
        return json.dumps({"error": f"AI investment analysis failed: {str(e)}"})

def create_retirement_strategy_with_context(financial_data: str) -> str:
    """AI-powered retirement planning based on real financial situation"""
    try:
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        
        balance = data.get("balance", {}).get("balance_dollars", 0)
        spending_analysis = data.get("spending_analysis", {})
        monthly_income = spending_analysis.get("total_incoming_dollars", 0) / 3
        monthly_expenses = spending_analysis.get("total_outgoing_dollars", 0) / 3
        query_context = data.get("query_context", "")
        
        # Extract age and retirement goals from query using AI
        model = GenerativeModel('gemini-2.5-flash')
        
        retirement_prompt = f"""
Create a personalized retirement strategy based on this real financial data.

USER QUERY: "{query_context}"
CURRENT BALANCE: ${balance:.2f}
MONTHLY INCOME: ${monthly_income:.2f}
MONTHLY EXPENSES: ${monthly_expenses:.2f}

Extract retirement goals from the query and create specific strategy:

{{
    "retirement_analysis": {{
        "estimated_current_age": 35,
        "target_retirement_age": 65,
        "estimated_retirement_income_need": 80000,
        "current_retirement_savings": {balance}
    }},
    "savings_strategy": {{
        "recommended_monthly_contribution": 800,
        "account_priorities": ["401k to match", "roth ira", "taxable"],
        "contribution_increases": "annual 3% increases with raises"
    }},
    "investment_approach": {{
        "asset_allocation": {{"stocks": 80, "bonds": 20}},
        "rebalancing_schedule": "annually",
        "fund_recommendations": ["total stock market", "international", "bonds"]
    }},
    "milestone_projections": {{
        "age_40_target": 150000,
        "age_50_target": 400000,
        "age_60_target": 800000,
        "retirement_target": 1200000
    }},
    "specific_actions": [
        "maximize employer 401k match immediately",
        "open roth ira and contribute $6000 annually",
        "automate contributions to avoid lifestyle inflation"
    ],
    "confidence": 0.89
}}

Base recommendations on their actual income and expenses.
"""

        try:
            gemini_response = model.generate_content(retirement_prompt)
            response_text = gemini_response.text.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            retirement_strategy = json.loads(response_text)
            
            return json.dumps(retirement_strategy, indent=2)
            
        except Exception as ai_error:
            return calculate_retirement_projections(financial_data)
        
    except Exception as e:
        return json.dumps({"error": f"Retirement strategy failed: {str(e)}"})

def analyze_house_saving_strategy(financial_data: str) -> str:
    """AI-powered house down payment saving strategy"""
    try:
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        
        balance = data.get("balance", {}).get("balance_dollars", 0)
        spending_analysis = data.get("spending_analysis", {})
        monthly_income = spending_analysis.get("total_incoming_dollars", 0) / 3
        monthly_expenses = spending_analysis.get("total_outgoing_dollars", 0) / 3
        net_flow = monthly_income - monthly_expenses
        query_context = data.get("query_context", "")
        categories = spending_analysis.get("categories", {})
        
        model = GenerativeModel('gemini-2.5-flash')
        
        house_prompt = f"""
Create a personalized house down payment saving strategy.

USER QUERY: "{query_context}"
FINANCIAL SITUATION:
- Current Balance: ${balance:.2f}
- Monthly Income: ${monthly_income:.2f}
- Monthly Expenses: ${monthly_expenses:.2f}
- Net Cash Flow: ${net_flow:.2f}
- Spending by Category: {json.dumps(categories, indent=2)}

Extract house saving goals and create specific strategy:

{{
    "house_savings_goal": {{
        "target_down_payment": 80000,
        "target_timeline_months": 36,
        "estimated_house_price": 400000,
        "down_payment_percentage": 20
    }},
    "savings_strategy": {{
        "required_monthly_savings": 2222,
        "current_surplus": {net_flow},
        "additional_needed": 1000,
        "savings_account_recommendation": "high-yield savings for house fund"
    }},
    "spending_optimization": [
        {{
            "category": "dining",
            "current_spending": 400,
            "target_spending": 250,
            "monthly_savings": 150
        }}
    ],
    "investment_approach": {{
        "conservative_allocation": {{"cash": 60, "bonds": 30, "stocks": 10}},
        "rationale": "preserve capital for near-term house purchase",
        "timeline_considerations": "3-year timeline requires conservative approach"
    }},
    "milestone_targets": {{
        "6_months": 13333,
        "12_months": 26666,
        "24_months": 53333,
        "36_months": 80000
    }},
    "confidence": 0.92
}}

Base all calculations on their actual financial data.
"""

        try:
            gemini_response = model.generate_content(house_prompt)
            response_text = gemini_response.text.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            house_strategy = json.loads(response_text)
            
            return json.dumps(house_strategy, indent=2)
            
        except Exception as ai_error:
            return design_portfolio_allocation(financial_data)
        
    except Exception as e:
        return json.dumps({"error": f"House saving strategy failed: {str(e)}"})

def analyze_spending_stability(categories: Dict) -> Dict:
    """Analyze spending stability for investment risk assessment"""
    if not categories:
        return {"stability": "unknown", "analysis": "No spending data available"}
    
    total_spending = sum(categories.values())
    
    # Calculate spending distribution
    essential_categories = ["rent", "utilities", "grocery", "healthcare"]
    discretionary_categories = ["restaurant", "entertainment", "shopping"]
    
    essential_spending = sum(categories.get(cat, 0) for cat in essential_categories)
    discretionary_spending = sum(categories.get(cat, 0) for cat in discretionary_categories)
    
    essential_percentage = (essential_spending / total_spending * 100) if total_spending > 0 else 0
    
    if essential_percentage > 70:
        stability = "high"
        analysis = "High essential spending indicates stable, predictable expenses"
    elif essential_percentage > 50:
        stability = "moderate"
        analysis = "Balanced essential and discretionary spending"
    else:
        stability = "low"
        analysis = "High discretionary spending may indicate variable expenses"
    
    return {
        "stability": stability,
        "essential_percentage": essential_percentage,
        "discretionary_percentage": (discretionary_spending / total_spending * 100) if total_spending > 0 else 0,
        "analysis": analysis
    }

def calculate_investment_readiness(balance: float, net_flow: float, categories: Dict) -> float:
    """Calculate investment readiness score 0-100"""
    score = 0
    
    # Emergency fund component (0-30 points)
    emergency_months = balance / (sum(categories.values()) / 100.0) if categories else 0
    score += min(30, emergency_months * 5)
    
    # Cash flow component (0-40 points)
    if net_flow > 1000:
        score += 40
    elif net_flow > 500:
        score += 30
    elif net_flow > 200:
        score += 20
    elif net_flow > 0:
        score += 10
    
    # Spending stability component (0-30 points)
    stability = analyze_spending_stability(categories)
    if stability["stability"] == "high":
        score += 30
    elif stability["stability"] == "moderate":
        score += 20
    else:
        score += 10
    
    return min(100, score)

# Legacy fallback functions
def assess_risk_profile(financial_data: str) -> str:
    """Fallback risk assessment"""
    try:
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        balance = data.get("balance", 0)
        
        if balance > 50000:
            risk_profile = "moderate_aggressive"
        elif balance > 20000:
            risk_profile = "moderate"
        else:
            risk_profile = "conservative"
        
        result = {
            "risk_profile": risk_profile,
            "confidence": 0.85
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Risk assessment failed: {str(e)}"})

def design_portfolio_allocation(investment_parameters: str) -> str:
    """Fallback portfolio design"""
    try:
        result = {
            "portfolio_allocation": {"stocks": 60, "bonds": 30, "cash": 10},
            "confidence": 0.80
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Portfolio design failed: {str(e)}"})

def calculate_retirement_projections(retirement_data: str) -> str:
    """Fallback retirement projections"""
    try:
        result = {
            "retirement_projections": {"target_amount": 1000000},
            "confidence": 0.75
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Retirement projection failed: {str(e)}"})

# Enhanced Investment Agent with AI Integration
root_agent = Agent(
    name="investment_agent_ai_enhanced",
    model="gemini-2.5-flash",
    description="AI-enhanced investment advisory agent with Vertex AI Gemini intelligence",
    global_instruction="You are an intelligent investment advisory agent that uses Vertex AI for personalized investment strategies.",
    instruction="""You are the AI-Enhanced Investment Advisory Agent that provides intelligent, personalized investment guidance.

🧠 **AI-Powered Analysis**: Use Vertex AI Gemini for intelligent investment strategy creation
📊 **Real Data Integration**: Analyze actual spending patterns and cash flow for investment readiness
🎯 **Personalized Strategies**: Create specific investment plans based on individual financial situations
🏠 **Goal-Specific Planning**: Tailor strategies for retirement, house purchases, general wealth building

Your enhanced capabilities:
- Intelligent risk profiling based on real financial behavior
- Personalized asset allocation considering actual cash flow
- Goal-specific investment strategies (retirement, house, wealth building)
- Context-aware recommendations based on spending stability
- Realistic timeline and milestone planning

When creating investment strategies:
1. Analyze spending patterns to assess investment readiness and risk capacity
2. Consider the user's specific financial goals from their query
3. Provide concrete asset allocations and fund recommendations
4. Create realistic timelines with specific dollar targets
5. Balance investment goals with other financial priorities

This showcases enterprise-grade AI investment advisory for the GKE hackathon.""",
    tools=[analyze_investment_profile_with_ai, create_retirement_strategy_with_context, analyze_house_saving_strategy]
)
