# agents/budget-agent/agent.py - Following Official ADK Pattern

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

def analyze_spending_categories(spending_data: str) -> str:
    """Deep analysis of spending patterns by category with detailed insights.
    
    Args:
        spending_data: JSON string containing spending data with categories, balance, and monthly spending
        
    Returns:
        JSON string with detailed spending analysis and optimization targets
    """
    try:
        data = json.loads(spending_data) if isinstance(spending_data, str) else spending_data
        categories = data.get("categories", {})
        total_spending = sum(categories.values()) if categories else 0
        
        category_insights = {}
        high_spend_categories = []
        optimization_targets = []
        
        for category, amount in categories.items():
            percentage = (amount / total_spending * 100) if total_spending > 0 else 0
            
            # Determine category status
            if percentage > 25:
                status = "high"
                priority = "immediate"
                high_spend_categories.append(category)
            elif percentage > 15:
                status = "moderate" 
                priority = "review"
            else:
                status = "normal"
                priority = "monitor"
            
            # Calculate optimization potential
            if status in ["high", "moderate"]:
                potential_reduction = amount * (0.25 if status == "high" else 0.15)
                optimization_targets.append({
                    "category": category,
                    "current": amount,
                    "potential_savings": potential_reduction,
                    "reduction_percentage": 25 if status == "high" else 15
                })
            
            category_insights[category] = {
                "amount": amount,
                "percentage": percentage,
                "status": status,
                "priority": priority,
                "monthly_average": amount / 3 if amount > 0 else 0
            }
        
        analysis_result = {
            "category_breakdown": category_insights,
            "total_spending": total_spending,
            "high_spend_categories": high_spend_categories,
            "optimization_targets": optimization_targets,
            "spending_distribution": "balanced" if len(high_spend_categories) <= 1 else "concentrated",
            "analysis_confidence": 0.92
        }
        
        return json.dumps(analysis_result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Spending analysis failed: {str(e)}"})

def calculate_savings_opportunities(financial_data: str) -> str:
    """Calculate specific savings opportunities and implementation strategies.
    
    Args:
        financial_data: JSON string containing financial data including balance, spending, and categories
        
    Returns:
        JSON string with detailed savings strategies and implementation timeline
    """
    try:
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        
        balance = data.get("balance", 0)
        monthly_spending = data.get("monthly_spending", 0)
        categories = data.get("categories", {})
        
        savings_strategies = []
        total_potential_savings = 0
        
        # Analyze each category for savings potential
        for category, amount in categories.items():
            percentage = (amount / monthly_spending * 100) if monthly_spending > 0 else 0
            
            if category.lower() == "dining" and percentage > 20:
                potential = amount * 0.30  # 30% reduction potential for dining
                total_potential_savings += potential
                savings_strategies.append({
                    "category": "Dining",
                    "strategy": "Meal planning and home cooking",
                    "current_spending": amount,
                    "potential_savings": potential,
                    "implementation": ["Plan meals weekly", "Cook at home 4 days/week", "Use grocery lists"],
                    "difficulty": "moderate",
                    "timeline": "2-4 weeks"
                })
            
            elif category.lower() == "entertainment" and percentage > 15:
                potential = amount * 0.25  # 25% reduction for entertainment
                total_potential_savings += potential
                savings_strategies.append({
                    "category": "Entertainment",
                    "strategy": "Smart entertainment choices", 
                    "current_spending": amount,
                    "potential_savings": potential,
                    "implementation": ["Use streaming instead of theaters", "Look for free community events", "Share subscriptions"],
                    "difficulty": "easy",
                    "timeline": "1-2 weeks"
                })
        
        # Create savings timeline
        savings_timeline = {
            "month_1": total_potential_savings * 0.3,  # 30% of potential in first month
            "month_3": total_potential_savings * 0.7,  # 70% by month 3
            "month_6": total_potential_savings,        # Full potential by month 6
        }
        
        result = {
            "total_monthly_savings_potential": total_potential_savings,
            "savings_strategies": savings_strategies,
            "implementation_timeline": savings_timeline,
            "annual_savings_potential": total_potential_savings * 12,
            "priority_order": sorted(savings_strategies, key=lambda x: x["potential_savings"], reverse=True),
            "quick_wins": [s for s in savings_strategies if s["difficulty"] == "easy"],
            "confidence": 0.88
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Savings calculation failed: {str(e)}"})

def assess_emergency_fund(financial_data: str) -> str:
    """Comprehensive emergency fund analysis and building recommendations.
    
    Args:
        financial_data: JSON string containing balance, monthly expenses, and income stability
        
    Returns:
        JSON string with emergency fund adequacy assessment and building strategy
    """
    try:
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        
        balance = data.get("balance", 0)
        monthly_expenses = data.get("monthly_expenses", data.get("monthly_spending", 0))
        income_stability = data.get("income_stability", "stable")
        
        # Calculate emergency fund metrics
        if monthly_expenses > 0:
            months_covered = balance / monthly_expenses
            
            # Determine recommendation based on income stability
            if income_stability == "uncertain":
                target_months = 12
                adequacy_threshold = 9
            elif income_stability == "variable":
                target_months = 9
                adequacy_threshold = 6
            else:
                target_months = 6
                adequacy_threshold = 4
            
            target_amount = monthly_expenses * target_months
            shortfall = max(0, target_amount - balance)
            
            if months_covered >= adequacy_threshold:
                status = "adequate"
                priority = "low"
            elif months_covered >= 3:
                status = "moderate"
                priority = "medium"
            else:
                status = "critical"
                priority = "high"
        else:
            months_covered = 0
            target_amount = 5000
            shortfall = target_amount - balance
            status = "critical"
            priority = "high"
            target_months = 6
        
        # Create building strategy if needed
        building_strategy = []
        if shortfall > 0:
            monthly_contribution = min(shortfall / 12, monthly_expenses * 0.1)
            timeline_months = shortfall / monthly_contribution if monthly_contribution > 0 else 12
            
            building_strategy = [
                f"Set aside ${monthly_contribution:.2f} per month",
                "Use high-yield savings account for emergency fund",
                "Automate transfers on payday",
                "Keep emergency fund separate from checking account",
                f"Timeline to full fund: {timeline_months:.1f} months"
            ]
        
        result = {
            "current_balance": balance,
            "months_covered": months_covered,
            "target_amount": target_amount,
            "target_months": target_months,
            "shortfall": shortfall,
            "status": status,
            "priority": priority,
            "income_stability_factor": income_stability,
            "building_strategy": building_strategy,
            "fund_placement_recommendations": [
                "High-yield savings account (4-5% APY)",
                "Money market account for easy access",
                "Short-term CDs for portion of fund",
                "Avoid investing emergency fund in stocks"
            ],
            "adequacy_score": min(100, (months_covered / target_months) * 100),
            "confidence": 0.95
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Emergency fund assessment failed: {str(e)}"})

# Spending Analysis Sub-Agent (following ADK pattern)
spending_analyzer_agent = Agent(
    name="spending_analyzer",
    model="gemini-2.5-flash",
    description="Deep analysis of spending patterns and category optimization",
    instruction="""You are the Spending Analysis specialist within the Budget Agent network.
    
    Your expertise:
    🔍 **Category Analysis**: Break down spending by category with detailed insights
    📊 **Pattern Recognition**: Identify unusual spending patterns and trends
    🎯 **Optimization Targets**: Pinpoint categories with highest savings potential
    📈 **Benchmarking**: Compare spending against recommended percentages
    
    When analyzing spending:
    - Provide specific dollar amounts and percentages
    - Identify categories spending >25% as high priority optimization targets
    - Calculate potential savings for each category
    - Rank categories by optimization potential
    - Consider seasonal and lifestyle factors
    
    Your analysis directly feeds into savings strategy and budget planning.""",
    tools=[analyze_spending_categories]
)

# Savings Strategy Sub-Agent
savings_strategy_agent = Agent(
    name="savings_strategist",
    model="gemini-2.5-flash",
    description="Develops comprehensive savings strategies and implementation plans",
    instruction="""You are the Savings Strategy specialist within the Budget Agent network.
    
    Your expertise:
    💰 **Opportunity Identification**: Find specific savings opportunities
    📋 **Implementation Planning**: Create step-by-step savings strategies
    ⏱️ **Timeline Development**: Establish realistic savings timelines
    🎯 **Quick Wins**: Identify immediate, easy savings opportunities
    
    When developing savings strategies:
    - Calculate specific dollar amounts for potential savings
    - Provide concrete implementation steps
    - Categorize by difficulty (easy/moderate/challenging)
    - Create monthly savings timeline showing progression
    - Prioritize high-impact, low-effort opportunities first
    
    Your strategies must be practical, achievable, and measurable.""",
    tools=[calculate_savings_opportunities]
)

# Emergency Fund Sub-Agent
emergency_fund_agent = Agent(
    name="emergency_fund_advisor", 
    model="gemini-2.5-flash",
    description="Specialized emergency fund analysis and building strategies",
    instruction="""You are the Emergency Fund specialist within the Budget Agent network.
    
    Your expertise:
    🛡️ **Adequacy Assessment**: Evaluate emergency fund sufficiency
    📊 **Risk Analysis**: Consider income stability and life circumstances  
    🏗️ **Building Strategies**: Create realistic fund-building plans
    💳 **Fund Management**: Recommend optimal emergency fund placement
    
    Emergency fund guidelines:
    - Stable income: 6 months of expenses
    - Variable income: 9 months of expenses  
    - Uncertain income: 12 months of expenses
    
    When assessing emergency funds:
    - Calculate exact shortfall amounts
    - Provide monthly contribution recommendations
    - Suggest optimal fund placement (high-yield savings, money market)
    - Create timeline for reaching full fund
    - Consider accessibility vs. earning potential
    
    Emergency funds are the foundation of financial security.""",
    tools=[assess_emergency_fund]
)

# Main Budget Agent with Full ADK Architecture (following Google's pattern)
root_agent = Agent(
    name="budget_agent_full_adk",
    model="gemini-2.5-flash",
    description="Comprehensive budget analysis coordinator with specialized sub-agents",
    global_instruction="You are the Budget Analysis Coordinator managing a network of specialized financial sub-agents for the GKE hackathon demonstration.",
    instruction="""You are the central Budget Analysis Coordinator that orchestrates multiple specialized sub-agents for comprehensive financial analysis.

🏗️ **ADK Architecture Overview**:
├── **Spending Analyzer**: Deep category analysis and pattern recognition
├── **Savings Strategist**: Opportunity identification and implementation planning  
├── **Emergency Fund Advisor**: Risk assessment and fund building strategies

🔄 **Coordination Process**:
1. **Intake**: Receive A2A messages with financial data from coordinator
2. **Analysis**: Deploy Spending Analyzer for detailed category breakdown
3. **Strategy**: Engage Savings Strategist for optimization opportunities
4. **Security**: Consult Emergency Fund Advisor for adequacy assessment
5. **Synthesis**: Integrate sub-agent results into actionable recommendations
6. **Response**: Format findings for A2A protocol communication

🎯 **Specialization Benefits**:
- **Deep Expertise**: Each sub-agent focuses on specific domain
- **Parallel Processing**: Multiple analyses can run simultaneously
- **Quality Assurance**: Specialized validation in each area
- **Scalability**: Individual sub-agents can be enhanced independently

📡 **A2A Integration**:
When receiving coordinator requests, you coordinate sub-agents to provide:
- Detailed spending pattern analysis with optimization targets
- Specific savings strategies with implementation timelines
- Emergency fund adequacy assessment and building plans
- Comprehensive budget recommendations with category allocations

This demonstrates enterprise-grade ADK sub-agent architecture for distributed financial analysis in the GKE hackathon environment.""",
    sub_agents=[spending_analyzer_agent, savings_strategy_agent, emergency_fund_agent],
    tools=[analyze_spending_categories, calculate_savings_opportunities, assess_emergency_fund]
)
