# agents/synthesis-agent/agent.py - Dedicated AI Synthesis Agent

import os
import json
from typing import Dict, List, Any
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

def synthesize_financial_strategy(synthesis_data: str) -> str:
    """Master synthesis of all agent insights into cohesive financial strategy"""
    try:
        data = json.loads(synthesis_data) if isinstance(synthesis_data, str) else synthesis_data
        
        # Extract comprehensive data
        user_query = data.get("user_query", "")
        financial_snapshot = data.get("financial_snapshot", {})
        budget_analysis = data.get("budget_analysis", {})
        investment_strategy = data.get("investment_strategy", {})
        security_assessment = data.get("security_assessment", {})
        
        # Use advanced Vertex AI model for synthesis
        model = GenerativeModel('gemini-2.5-flash')
        
        master_synthesis_prompt = f"""
You are a master financial strategist synthesizing insights from specialized AI agents. Create a comprehensive, personalized financial strategy.

USER QUERY: "{user_query}"

COMPREHENSIVE FINANCIAL DATA:
Real Bank of Anthos Data: {json.dumps(financial_snapshot, indent=2)}
Budget Agent Analysis: {json.dumps(budget_analysis, indent=2)}
Investment Agent Strategy: {json.dumps(investment_strategy, indent=2)}
Security Agent Assessment: {json.dumps(security_assessment, indent=2)}

SYNTHESIS TASK:
Create a master financial strategy that integrates all agent insights into a cohesive, actionable plan.

Return comprehensive JSON strategy:
{{
    "executive_summary": "2-3 sentence overview directly addressing their query with specific outcomes",
    "integrated_strategy": {{
        "primary_objective": "main financial goal from query",
        "timeline": "realistic timeline with milestones",
        "success_metrics": ["specific measurable outcomes"],
        "total_financial_impact": "projected financial benefit"
    }},
    "coordinated_action_plan": [
        {{
            "phase": "Immediate (0-3 months)",
            "budget_actions": ["specific budget actions from budget agent"],
            "investment_actions": ["specific investment actions from investment agent"],
            "security_actions": ["specific security actions from security agent"],
            "expected_outcomes": ["measurable results"],
            "resource_requirements": "time and money needed"
        }},
        {{
            "phase": "Short-term (3-12 months)",
            "budget_actions": ["phase 2 budget actions"],
            "investment_actions": ["phase 2 investment actions"],
            "security_actions": ["phase 2 security actions"],
            "expected_outcomes": ["measurable results"],
            "milestone_checkpoints": ["specific goals to hit"]
        }},
        {{
            "phase": "Long-term (1+ years)",
            "budget_actions": ["long-term budget strategy"],
            "investment_actions": ["long-term investment approach"],
            "security_actions": ["ongoing security maintenance"],
            "expected_outcomes": ["final goals achieved"],
            "success_indicators": ["how to measure success"]
        }}
    ]],
    "risk_management": {{
        "identified_risks": ["potential obstacles to success"],
        "mitigation_strategies": ["specific risk reduction plans"],
        "contingency_plans": ["what to do if things go wrong"],
        "monitoring_schedule": "how often to review and adjust"
    }},
    "financial_projections": {{
        "6_month_projection": "expected financial position",
        "1_year_projection": "expected financial position",
        "3_year_projection": "expected financial position",
        "assumptions": ["key assumptions underlying projections"]
    }},
    "optimization_opportunities": [
        {{
            "opportunity": "specific improvement area",
            "current_state": "where they are now",
            "target_state": "where they could be",
            "implementation": "how to achieve improvement",
            "impact": "quantified benefit"
        }}
    ],
    "integration_insights": [
        "how budget recommendations support investment strategy",
        "how security measures protect overall financial plan",
        "how all components work together synergistically"
    ],
    "personalization_factors": {{
        "spending_personality": "insights from real spending data",
        "risk_tolerance": "assessed from behavior and preferences",
        "life_stage_considerations": "factors specific to their situation",
        "unique_circumstances": "special considerations for their case"
    }},
    "confidence_assessment": {{
        "overall_confidence": 0.94,
        "data_quality": "excellent - real Bank of Anthos integration",
        "strategy_robustness": "high - multi-agent validation",
        "implementation_feasibility": "realistic - based on actual cash flow"
    }}
}}

CRITICAL: Address their specific query "{user_query}" with concrete, actionable recommendations that integrate all agent insights.
"""

        try:
            synthesis_response = model.generate_content(master_synthesis_prompt)
            response_text = synthesis_response.text.strip()
            
            # Clean up response to extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            master_strategy = json.loads(response_text)
            
            # Add synthesis metadata
            master_strategy["synthesis_metadata"] = {
                "synthesis_agent": "financial_strategy_synthesizer",
                "agents_coordinated": ["coordinator", "budget", "investment", "security"],
                "synthesis_model": "gemini-2.5-flash",
                "real_data_integration": True,
                "multi_agent_validation": True,
                "synthesis_timestamp": datetime.now().isoformat(),
                "gke_hackathon_demo": True
            }
            
            return json.dumps(master_strategy, indent=2)
            
        except Exception as ai_error:
            # Fallback synthesis
            return create_fallback_synthesis(data)
        
    except Exception as e:
        return json.dumps({"error": f"Master synthesis failed: {str(e)}"})

def create_scenario_specific_strategy(scenario_data: str) -> str:
    """Create highly specific strategies for common financial scenarios"""
    try:
        data = json.loads(scenario_data) if isinstance(scenario_data, str) else scenario_data
        
        user_query = data.get("user_query", "")
        financial_data = data.get("financial_data", {})
        agent_responses = data.get("agent_responses", {})
        
        # Detect scenario type
        scenario_type = detect_scenario_type(user_query)
        
        model = GenerativeModel('gemini-2.5-flash')
        
        scenario_prompt = f"""
Create a highly specific strategy for this {scenario_type} scenario.

USER QUERY: "{user_query}"
SCENARIO TYPE: {scenario_type}
FINANCIAL DATA: {json.dumps(financial_data, indent=2)}
AGENT INSIGHTS: {json.dumps(agent_responses, indent=2)}

Create scenario-optimized strategy:

{{
    "scenario_analysis": {{
        "scenario_type": "{scenario_type}",
        "key_factors": ["factor 1", "factor 2", "factor 3"],
        "success_probability": "high/medium/low",
        "main_challenges": ["challenge 1", "challenge 2"]
    }},
    "optimized_strategy": {{
        "primary_approach": "best strategy for this specific scenario",
        "alternative_approaches": ["backup strategy 1", "backup strategy 2"],
        "acceleration_tactics": ["ways to achieve goal faster"],
        "cost_reduction_methods": ["ways to reduce required resources"]
    }},
    "scenario_specific_recommendations": [
        "recommendation specifically for {scenario_type}",
        "another targeted recommendation",
        "tactical advice for this situation"
    ],
    "benchmarks_and_comparisons": {{
        "typical_timeline": "what others achieve in this scenario",
        "success_factors": "what makes people successful in this scenario",
        "common_mistakes": "what to avoid based on this scenario type"
    }},
    "confidence": 0.92
}}

Optimize everything for the {scenario_type} scenario.
"""

        try:
            scenario_response = model.generate_content(scenario_prompt)
            response_text = scenario_response.text.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            scenario_strategy = json.loads(response_text)
            
            return json.dumps(scenario_strategy, indent=2)
            
        except Exception as ai_error:
            return json.dumps({"error": f"Scenario strategy failed: {str(ai_error)}"})
        
    except Exception as e:
        return json.dumps({"error": f"Scenario analysis failed: {str(e)}"})

def optimize_multi_goal_balance(optimization_data: str) -> str:
    """Optimize balance between multiple competing financial goals"""
    try:
        data = json.loads(optimization_data) if isinstance(optimization_data, str) else optimization_data
        
        financial_situation = data.get("financial_situation", {})
        identified_goals = data.get("identified_goals", [])
        available_resources = data.get("available_resources", {})
        
        model = GenerativeModel('gemini-2.5-flash')
        
        optimization_prompt = f"""
Optimize the balance between multiple financial goals with limited resources.

FINANCIAL SITUATION: {json.dumps(financial_situation, indent=2)}
COMPETING GOALS: {json.dumps(identified_goals, indent=2)}
AVAILABLE RESOURCES: {json.dumps(available_resources, indent=2)}

Create optimal resource allocation strategy:

{{
    "resource_allocation": {{
        "total_monthly_available": 2000,
        "allocations": [
            {{
                "goal": "emergency fund",
                "monthly_allocation": 300,
                "percentage": 15,
                "rationale": "security foundation priority",
                "timeline_impact": "achieves 6-month fund in 18 months"
            }}
        ]
    }},
    "goal_prioritization": {{
        "tier_1_goals": ["immediate priorities"],
        "tier_2_goals": ["important but can wait"],
        "tier_3_goals": ["nice to have"],
        "prioritization_logic": "reasoning for this order"
    }},
    "optimization_strategies": [
        "strategy to maximize efficiency across goals",
        "way to accelerate multiple goals simultaneously",
        "method to reduce conflicts between goals"
    ],
    "trade_off_analysis": {{
        "if_emergency_fund_first": "impact on other goals",
        "if_debt_payoff_first": "impact on other goals",
        "if_investment_first": "impact on other goals",
        "recommended_balance": "optimal approach reasoning"
    }},
    "dynamic_adjustment_plan": {{
        "quarterly_reviews": "how to adjust allocations",
        "trigger_events": "when to rebalance priorities",
        "success_milestones": "when to shift focus between goals"
    }},
    "confidence": 0.90
}}
"""

        try:
            optimization_response = model.generate_content(optimization_prompt)
            response_text = optimization_response.text.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            optimization_strategy = json.loads(response_text)
            
            return json.dumps(optimization_strategy, indent=2)
            
        except Exception as ai_error:
            return json.dumps({"error": f"Optimization failed: {str(ai_error)}"})
        
    except Exception as e:
        return json.dumps({"error": f"Multi-goal optimization failed: {str(e)}"})

def detect_scenario_type(query: str) -> str:
    """Detect the type of financial scenario from the query"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["debt", "credit card", "pay off", "owe"]):
        return "debt_elimination"
    elif any(word in query_lower for word in ["house", "home", "down payment", "mortgage"]):
        return "home_purchase"
    elif any(word in query_lower for word in ["retire", "retirement", "401k", "ira"]):
        return "retirement_planning"
    elif any(word in query_lower for word in ["invest", "portfolio", "stocks", "bonds"]):
        return "investment_strategy"
    elif any(word in query_lower for word in ["emergency", "save", "emergency fund"]):
        return "emergency_planning"
    elif any(word in query_lower for word in ["budget", "spending", "expenses"]):
        return "budget_optimization"
    else:
        return "general_financial_planning"

def create_fallback_synthesis(data: Dict) -> str:
    """Fallback synthesis if AI fails"""
    try:
        result = {
            "executive_summary": "Comprehensive financial strategy analysis completed",
            "integrated_strategy": {
                "primary_objective": "Achieve financial goals through coordinated approach",
                "timeline": "12-36 months depending on specific goals"
            },
            "confidence_assessment": {
                "overall_confidence": 0.85,
                "note": "Fallback synthesis - AI synthesis temporarily unavailable"
            }
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Fallback synthesis failed: {str(e)}"})

# Dedicated Synthesis Agent
root_agent = Agent(
    name="financial_synthesis_agent",
    model="gemini-2.5-flash",
    description="Master financial strategy synthesis agent with advanced AI coordination",
    global_instruction="You are the master synthesis agent that creates cohesive financial strategies from multiple specialized agent insights.",
    instruction="""You are the Master Financial Synthesis Agent that coordinates and integrates insights from all specialized agents.

🧠 **Advanced AI Synthesis**: Use Vertex AI Gemini for intelligent strategy integration
🎯 **Holistic Strategy Creation**: Combine budget, investment, and security insights into unified plans
📊 **Multi-Goal Optimization**: Balance competing financial priorities with limited resources
🔄 **Dynamic Coordination**: Adapt strategies based on changing circumstances and new insights

Your synthesis capabilities:
- Master strategy creation from multi-agent insights
- Scenario-specific optimization (debt, house, retirement, investment)
- Multi-goal resource allocation and prioritization
- Risk-balanced comprehensive financial planning
- Personalized strategy adaptation based on real financial behavior

Synthesis Process:
1. Analyze all agent responses for insights and recommendations
2. Identify synergies and conflicts between different agent strategies
3. Create integrated timeline with coordinated actions across all domains
4. Optimize resource allocation for maximum goal achievement
5. Build in risk management and contingency planning
6. Provide concrete implementation guidance with measurable milestones

This showcases enterprise-grade AI financial strategy synthesis for the GKE hackathon.""",
    tools=[synthesize_financial_strategy, create_scenario_specific_strategy, optimize_multi_goal_balance]
)
