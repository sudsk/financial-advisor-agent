# agents/budget-agent/agent.py - Full ADK Implementation with Sub-Agents
import os
import json
from typing import Dict, Any
from datetime import datetime
import logging

# Google ADK imports
from google.adk.agents import Agent
import google.auth
import vertexai
from vertexai.generative_models import GenerativeModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Google Cloud
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

PROJECT_ID = os.getenv('PROJECT_ID', project_id)
REGION = os.getenv('REGION', 'us-central1')
vertexai.init(project=PROJECT_ID, location=REGION)

# ADK Tools for Specialized Analysis
def analyze_spending_categories(spending_data: str) -> str:
    """Deep analysis of spending patterns by category"""
    try:
        logger.info("🔍 SPENDING ANALYZER: Processing category analysis")
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
                "monthly_average": amount / 3 if amount > 0 else 0  # Assuming 3-month data
            }
        
        analysis_result = {
            "category_breakdown": category_insights,
            "total_spending": total_spending,
            "high_spend_categories": high_spend_categories,
            "optimization_targets": optimization_targets,
            "spending_distribution": "balanced" if len(high_spend_categories) <= 1 else "concentrated",
            "analysis_confidence": 0.92
        }
        
        logger.info(f"✅ SPENDING ANALYZER: Found {len(optimization_targets)} optimization opportunities")
        return json.dumps(analysis_result, indent=2)
        
    except Exception as e:
        logger.error(f"❌ SPENDING ANALYZER: Analysis failed: {str(e)}")
        return json.dumps({"error": f"Spending analysis failed: {str(e)}"})

def calculate_savings_opportunities(financial_data: str) -> str:
    """Calculate specific savings opportunities and strategies"""
    try:
        logger.info("💰 SAVINGS STRATEGIST: Calculating savings opportunities")
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
            
            elif category.lower() == "groceries" and amount > 600:
                potential = min(amount * 0.15, 150)  # Max $150 savings on groceries
                total_potential_savings += potential
                savings_strategies.append({
                    "category": "Groceries",
                    "strategy": "Smart grocery shopping",
                    "current_spending": amount,
                    "potential_savings": potential,
                    "implementation": ["Buy generic brands", "Use coupons and sales", "Buy in bulk for non-perishables"],
                    "difficulty": "easy",
                    "timeline": "immediate"
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
        
        logger.info(f"✅ SAVINGS STRATEGIST: Identified ${total_potential_savings:.2f}/month savings potential")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"❌ SAVINGS STRATEGIST: Calculation failed: {str(e)}")
        return json.dumps({"error": f"Savings calculation failed: {str(e)}"})

def assess_emergency_fund(financial_data: str) -> str:
    """Comprehensive emergency fund analysis and recommendations"""
    try:
        logger.info("🛡️ EMERGENCY FUND ADVISOR: Assessing emergency fund adequacy")
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        
        balance = data.get("balance", 0)
        monthly_expenses = data.get("monthly_expenses", data.get("monthly_spending", 0))
        income_stability = data.get("income_stability", "stable")  # stable, variable, uncertain
        
        # Calculate emergency fund metrics
        if monthly_expenses > 0:
            months_covered = balance / monthly_expenses
            
            # Determine recommendation based on income stability
            if income_stability == "uncertain":
                target_months = 12  # 12 months for uncertain income
                adequacy_threshold = 9
            elif income_stability == "variable":
                target_months = 9   # 9 months for variable income
                adequacy_threshold = 6
            else:
                target_months = 6   # 6 months for stable income
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
            target_amount = 5000  # Default minimum emergency fund
            shortfall = target_amount - balance
            status = "critical"
            priority = "high"
            target_months = 6
        
        # Create building strategy if needed
        building_strategy = []
        if shortfall > 0:
            monthly_contribution = min(shortfall / 12, monthly_expenses * 0.1)  # 10% of expenses max
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
        
        logger.info(f"✅ EMERGENCY FUND ADVISOR: {status} status - {months_covered:.1f} months covered")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"❌ EMERGENCY FUND ADVISOR: Assessment failed: {str(e)}")
        return json.dumps({"error": f"Emergency fund assessment failed: {str(e)}"})

def create_budget_plan(planning_data: str) -> str:
    """Create comprehensive budget plan with specific allocations"""
    try:
        logger.info("📋 BUDGET PLANNER: Creating comprehensive budget plan")
        data = json.loads(planning_data) if isinstance(planning_data, str) else planning_data
        
        monthly_income = data.get("monthly_income", 0)
        current_expenses = data.get("current_expenses", {})
        financial_goals = data.get("financial_goals", [])
        
        # Standard budget allocation recommendations (50/30/20 rule modified)
        recommended_allocations = {
            "needs": {"percentage": 50, "amount": monthly_income * 0.50},
            "wants": {"percentage": 25, "amount": monthly_income * 0.25}, 
            "savings": {"percentage": 15, "amount": monthly_income * 0.15},
            "debt_repayment": {"percentage": 10, "amount": monthly_income * 0.10}
        }
        
        # Detailed category recommendations
        detailed_budget = {
            "housing": {"recommended_max": monthly_income * 0.28, "priority": "high"},
            "transportation": {"recommended_max": monthly_income * 0.15, "priority": "high"},
            "groceries": {"recommended_max": monthly_income * 0.10, "priority": "high"},
            "utilities": {"recommended_max": monthly_income * 0.08, "priority": "high"},
            "dining_out": {"recommended_max": monthly_income * 0.05, "priority": "medium"},
            "entertainment": {"recommended_max": monthly_income * 0.05, "priority": "medium"},
            "shopping": {"recommended_max": monthly_income * 0.05, "priority": "low"},
            "emergency_fund": {"recommended_min": monthly_income * 0.10, "priority": "high"},
            "retirement": {"recommended_min": monthly_income * 0.15, "priority": "high"}
        }
        
        # Compare current vs recommended
        budget_analysis = []
        for category, current_amount in current_expenses.items():
            recommended = detailed_budget.get(category.lower(), {})
            if recommended:
                recommended_max = recommended.get("recommended_max", 0)
                if current_amount > recommended_max:
                    overspend = current_amount - recommended_max
                    budget_analysis.append({
                        "category": category,
                        "current": current_amount,
                        "recommended_max": recommended_max,
                        "overspend": overspend,
                        "action": f"Consider reducing by ${overspend:.2f}"
                    })
        
        result = {
            "monthly_income": monthly_income,
            "recommended_allocations": recommended_allocations,
            "detailed_budget_guide": detailed_budget,
            "current_vs_recommended": budget_analysis,
            "budget_health_score": min(100, max(0, 100 - len(budget_analysis) * 10)),
            "implementation_steps": [
                "Track all expenses for one month to establish baseline",
                "Set up separate accounts for different budget categories",
                "Automate savings and bill payments",
                "Review and adjust budget monthly",
                "Use budgeting app or spreadsheet to monitor progress"
            ],
            "confidence": 0.90
        }
        
        logger.info(f"✅ BUDGET PLANNER: Created budget plan with {len(budget_analysis)} optimization areas")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"❌ BUDGET PLANNER: Planning failed: {str(e)}")
        return json.dumps({"error": f"Budget planning failed: {str(e)}"})

# ADK Sub-Agents for Specialized Budget Tasks

# Spending Analysis Sub-Agent
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

# Budget Planning Sub-Agent
budget_planner_agent = Agent(
    name="budget_planner",
    model="gemini-2.5-flash", 
    description="Creates comprehensive budget plans and allocation strategies",
    instruction="""You are the Budget Planning specialist within the Budget Agent network.
    
    Your expertise:
    📋 **Budget Architecture**: Design comprehensive budget frameworks
    🎯 **Allocation Strategy**: Optimize income allocation across categories
    📊 **Performance Tracking**: Establish budget monitoring and adjustment processes
    ⚖️ **Balance Optimization**: Balance needs, wants, savings, and debt repayment
    
    Budget frameworks you use:
    - 50/30/20 rule (needs/wants/savings) as baseline
    - Modified allocations based on individual circumstances
    - Category-specific percentage guidelines
    - Goal-based budget adjustments
    
    When creating budget plans:
    - Provide specific dollar amounts for each category
    - Compare current spending vs. recommended allocations
    - Identify overspending areas with corrective actions
    - Create implementation timeline and tracking methods
    - Include regular review and adjustment schedules
    
    Your plans must be realistic, sustainable, and goal-oriented.""",
    tools=[create_budget_plan]
)

# Main Budget Agent with Full ADK Sub-Agent Architecture
root_agent = Agent(
    name="budget_agent_full_adk",
    model="gemini-2.5-flash", 
    description="Comprehensive budget analysis coordinator with specialized sub-agents",
    global_instruction="You are the Budget Analysis Coordinator managing a network of specialized financial sub-agents.",
    instruction="""You are the central Budget Analysis Coordinator that orchestrates multiple specialized sub-agents for comprehensive financial analysis.

🏗️ **ADK Architecture Overview**:
├── **Spending Analyzer**: Deep category analysis and pattern recognition
├── **Savings Strategist**: Opportunity identification and implementation planning  
├── **Emergency Fund Advisor**: Risk assessment and fund building strategies
└── **Budget Planner**: Comprehensive budget design and allocation optimization

🔄 **Coordination Process**:
1. **Intake**: Receive A2A messages with financial data from coordinator
2. **Analysis**: Deploy Spending Analyzer for detailed category breakdown
3. **Strategy**: Engage Savings Strategist for optimization opportunities
4. **Security**: Consult Emergency Fund Advisor for adequacy assessment
5. **Planning**: Activate Budget Planner for comprehensive budget design
6. **Synthesis**: Integrate sub-agent results into actionable recommendations
7. **Response**: Format findings for A2A protocol communication

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
    sub_agents=[spending_analyzer_agent, savings_strategy_agent, emergency_fund_agent, budget_planner_agent],
    tools=[]  # Main agent coordinates sub-agents, uses their specialized tools
)
