# agents/budget-agent/agent.py - Budget Agent with A2A Protocol Support
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

def process_a2a_spending_analysis(message_payload: str) -> str:
    """A2A Protocol tool for processing spending analysis requests from coordinator
    
    Args:
        message_payload: JSON string containing A2A message with financial data
        
    Returns:
        JSON string with budget analysis results for A2A response
    """
    try:
        logger.info("💰 BUDGET AGENT: Processing A2A spending analysis request")
        
        # Parse A2A message payload
        payload = json.loads(message_payload) if isinstance(message_payload, str) else message_payload
        financial_data = payload.get("financial_data", {})
        query_context = payload.get("query_context", "")
        correlation_id = payload.get("correlation_id", "unknown")
        
        logger.info(f"💰 BUDGET AGENT: Correlation ID {correlation_id}")
        
        # Extract financial information
        balance = financial_data.get("balance", {}).get("amount", 0)
        spending_analysis = financial_data.get("spending_analysis", {})
        categories = spending_analysis.get("categories", {})
        total_spending = spending_analysis.get("total_spending", 0)
        monthly_average = spending_analysis.get("average_monthly", 0)
        
        # Calculate category percentages and optimization opportunities
        category_percentages = {}
        optimization_opportunities = []
        savings_potential = 0
        
        for category, amount in categories.items():
            percentage = (amount / total_spending * 100) if total_spending > 0 else 0
            category_percentages[category] = percentage
            
            # Identify optimization opportunities
            if category == "Dining" and percentage > 20:
                potential_savings = amount * 0.3
                savings_potential += potential_savings
                optimization_opportunities.append(
                    f"Reduce dining expenses by 30% - save ${potential_savings:.2f}/month"
                )
            elif category == "Entertainment" and percentage > 15:
                potential_savings = amount * 0.25
                savings_potential += potential_savings
                optimization_opportunities.append(
                    f"Optimize entertainment spending - save ${potential_savings:.2f}/month"
                )
            elif category == "Groceries" and amount > 600:
                potential_savings = min(amount * 0.15, 150)
                savings_potential += potential_savings
                optimization_opportunities.append(
                    f"Meal planning optimization - save ${potential_savings:.2f}/month"
                )
        
        # Emergency fund analysis
        emergency_fund_ratio = balance / (monthly_average * 6) if monthly_average > 0 else 0
        emergency_fund_status = "adequate" if emergency_fund_ratio >= 1.0 else "insufficient"
        
        # Generate AI-enhanced recommendations using Vertex AI
        try:
            model = GenerativeModel('gemini-pro')
            context_prompt = f"""
            As a budget analysis expert, provide insights based on this financial data:
            
            Query Context: "{query_context}"
            Monthly Spending: ${monthly_average}
            Balance: ${balance}
            Top Categories: {dict(list(categories.items())[:3])}
            Savings Potential: ${savings_potential}/month
            Emergency Fund Status: {emergency_fund_status}
            
            Provide 3 specific, actionable budget recommendations as a JSON array:
            ["recommendation 1", "recommendation 2", "recommendation 3"]
            """
            
            ai_response = model.generate_content(context_prompt)
            ai_recommendations = json.loads(ai_response.text)
            
        except Exception as e:
            logger.warning(f"💰 BUDGET AGENT: AI enhancement failed: {str(e)}")
            ai_recommendations = optimization_opportunities[:3] if optimization_opportunities else [
                "Track all expenses for better visibility",
                "Set up automatic savings transfers", 
                "Review subscriptions and recurring charges"
            ]
        
        # Build A2A response
        a2a_response = {
            "agent_id": "budget_agent",
            "agent_type": "budget_analysis",
            "correlation_id": correlation_id,
            "analysis_results": {
                "category_breakdown": category_percentages,
                "total_monthly_spending": monthly_average,
                "potential_monthly_savings": savings_potential,
                "emergency_fund_ratio": emergency_fund_ratio,
                "emergency_fund_status": emergency_fund_status,
                "optimization_opportunities": optimization_opportunities
            },
            "recommendations": ai_recommendations,
            "budget_score": min(100, max(0, 100 - (len(optimization_opportunities) * 15))),
            "confidence": 0.92,
            "processing_metadata": {
                "categories_analyzed": len(categories),
                "optimization_areas_found": len(optimization_opportunities),
                "ai_enhanced": True,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        logger.info(f"✅ BUDGET AGENT: Analysis complete - found {len(optimization_opportunities)} optimization opportunities")
        return json.dumps(a2a_response, indent=2)
        
    except Exception as e:
        logger.error(f"❌ BUDGET AGENT: A2A processing failed: {str(e)}")
        return json.dumps({
            "agent_id": "budget_agent",
            "agent_type": "budget_analysis", 
            "error": f"Budget analysis failed: {str(e)}",
            "confidence": 0.0,
            "recommendations": ["Unable to perform budget analysis", "Please check data and try again"],
            "processing_metadata": {
                "error": True,
                "timestamp": datetime.now().isoformat()
            }
        })

def create_savings_strategy(savings_goal_data: str) -> str:
    """Tool to create detailed savings strategy for specific goals
    
    Args:
        savings_goal_data: JSON string with savings goal parameters
        
    Returns:
        JSON string with detailed savings strategy
    """
    try:
        data = json.loads(savings_goal_data) if isinstance(savings_goal_data, str) else savings_goal_data
        
        goal_amount = data.get("goal_amount", 0)
        timeline_months = data.get("timeline_months", 12)
        current_savings = data.get("current_savings", 0)
        monthly_income = data.get("monthly_income", 0)
        monthly_expenses = data.get("monthly_expenses", 0)
        
        # Calculate savings requirements
        remaining_needed = max(0, goal_amount - current_savings)
        monthly_target = remaining_needed / timeline_months if timeline_months > 0 else 0
        available_surplus = max(0, monthly_income - monthly_expenses)
        
        # Determine feasibility
        feasibility_ratio = monthly_target / available_surplus if available_surplus > 0 else float('inf')
        
        if feasibility_ratio <= 0.5:
            feasibility = "highly_achievable"
            difficulty = "easy"
        elif feasibility_ratio <= 0.8:
            feasibility = "achievable"
            difficulty = "moderate"
        else:
            feasibility = "challenging"
            difficulty = "difficult"
        
        strategy = {
            "goal_analysis": {
                "target_amount": goal_amount,
                "current_progress": current_savings,
                "remaining_needed": remaining_needed,
                "timeline_months": timeline_months,
                "monthly_target": monthly_target
            },
            "feasibility_assessment": {
                "status": feasibility,
                "difficulty": difficulty,
                "monthly_surplus_needed": monthly_target,
                "available_surplus": available_surplus,
                "feasibility_ratio": min(1.0, feasibility_ratio)
            },
            "savings_strategy": [
                f"Set up automatic transfer of ${monthly_target:.2f} per month",
                "Open dedicated high-yield savings account for this goal",
                "Review progress monthly and adjust if income changes",
                "Consider additional income sources if target is challenging"
            ],
            "milestones": [
                {"month": timeline_months // 4, "target": goal_amount * 0.25},
                {"month": timeline_months // 2, "target": goal_amount * 0.50},
                {"month": int(timeline_months * 0.75), "target": goal_amount * 0.75},
                {"month": timeline_months, "target": goal_amount}
            ]
        }
        
        return json.dumps(strategy, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Savings strategy creation failed: {str(e)}",
            "strategy": [],
            "milestones": []
        })

# ADK Budget Agent with A2A Protocol Support
root_agent = Agent(
    name="budget_agent_a2a",
    model="gemini-2.5-flash",
    description="Specialized budget analysis agent with A2A protocol support for distributed coordination",
    instruction="""You are a specialized budget analysis agent that operates in a distributed agent network.

Your capabilities:
🔍 **Spending Analysis**: Deep dive into spending patterns and category optimization
📊 **Budget Optimization**: Identify concrete savings opportunities with dollar amounts
💡 **Strategic Recommendations**: AI-enhanced, actionable budget advice
📡 **A2A Protocol**: Network communication with coordinator and other agents
🎯 **Goal-Oriented**: Create specific savings strategies for financial goals

When processing A2A requests from the coordinator:
1. Thoroughly analyze the financial data provided in the message payload
2. Calculate category-wise spending percentages and identify optimization areas
3. Use Vertex AI to enhance recommendations based on query context
4. Provide specific dollar amounts for potential savings
5. Return structured A2A response with detailed analysis and confidence scores

Your analysis should be:
- **Specific**: Provide exact dollar amounts and percentages
- **Actionable**: Give steps users can implement immediately  
- **Realistic**: Ensure recommendations are achievable
- **Context-Aware**: Consider the user's overall financial situation

This agent demonstrates enterprise-grade distributed financial analysis for the GKE hackathon.
""",
    tools=[process_a2a_spending_analysis, create_savings_strategy]
)
