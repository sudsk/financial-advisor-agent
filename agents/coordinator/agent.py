# agents/investment-agent/agent.py - Full ADK Investment Agent with Sub-Agents
import os
import json
from typing import Dict, Any, List
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

# ADK Tools for Investment Analysis

def assess_risk_profile(financial_data: str) -> str:
    """Comprehensive risk tolerance and capacity assessment"""
    try:
        logger.info("📊 RISK ASSESSOR: Evaluating investment risk profile")
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        
        # Extract relevant financial data
        age = data.get("age", 35)  # Default age if not provided
        balance = data.get("balance", 0)
        monthly_income = data.get("monthly_income", 0)
        monthly_expenses = data.get("monthly_expenses", 0)
        debt_amount = data.get("debt_amount", 0)
        investment_timeline = data.get("investment_timeline", 10)  # years
        
        # Calculate financial stability metrics
        emergency_fund_ratio = balance / (monthly_expenses * 6) if monthly_expenses > 0 else 0
        debt_to_income = (debt_amount / (monthly_income * 12)) if monthly_income > 0 else 0
        available_monthly = monthly_income - monthly_expenses
        
        # Risk capacity scoring (0-100)
        age_score = min(100, (65 - age) * 2)  # Younger = higher capacity
        stability_score = min(100, emergency_fund_ratio * 50)  # Emergency fund adequacy
        debt_score = max(0, 100 - (debt_to_income * 200))  # Lower debt = higher score
        income_score = min(100, (available_monthly / 1000) * 20) if available_monthly > 0 else 0
        timeline_score = min(100, investment_timeline * 8)  # Longer timeline = higher capacity
        
        risk_capacity_score = (age_score + stability_score + debt_score + income_score + timeline_score) / 5
        
        # Determine risk profile
        if risk_capacity_score >= 80:
            risk_profile = "aggressive"
            risk_level = "high"
        elif risk_capacity_score >= 60:
            risk_profile = "moderate_aggressive"
            risk_level = "moderate-high"
        elif risk_capacity_score >= 40:
            risk_profile = "moderate"
            risk_level = "moderate"
        elif risk_capacity_score >= 20:
            risk_profile = "conservative_moderate"
            risk_level = "moderate-low"
        else:
            risk_profile = "conservative"
            risk_level = "low"
        
        # Generate risk-specific recommendations
        risk_recommendations = {
            "aggressive": [
                "Can handle high volatility for higher returns",
                "Focus on growth stocks and emerging markets",
                "Consider higher allocation to equities (80-90%)"
            ],
            "moderate_aggressive": [
                "Balance growth with some stability",
                "Mix of growth and value investments",
                "Equity allocation around 70-80%"
            ],
            "moderate": [
                "Balanced approach between growth and stability",
                "Diversified portfolio across asset classes",
                "Equity allocation around 60-70%"
            ],
            "conservative_moderate": [
                "Prioritize capital preservation with modest growth",
                "Higher allocation to bonds and stable assets",
                "Equity allocation around 40-50%"
            ],
            "conservative": [
                "Focus on capital preservation",
                "High allocation to bonds and cash equivalents",
                "Equity allocation around 20-30%"
            ]
        }
        
        result = {
            "risk_capacity_score": risk_capacity_score,
            "risk_profile": risk_profile,
            "risk_level": risk_level,
            "profile_factors": {
                "age_factor": age_score,
                "financial_stability": stability_score,
                "debt_burden": debt_score,
                "income_flexibility": income_score,
                "time_horizon": timeline_score
            },
            "recommendations": risk_recommendations.get(risk_profile, []),
            "key_considerations": [
                f"Investment timeline: {investment_timeline} years",
                f"Emergency fund status: {'Adequate' if emergency_fund_ratio >= 1 else 'Needs improvement'}",
                f"Debt-to-income ratio: {debt_to_income:.1%}",
                f"Available monthly for investing: ${available_monthly:.2f}"
            ],
            "confidence": 0.91
        }
        
        logger.info(f"✅ RISK ASSESSOR: Profile determined - {risk_profile} ({risk_capacity_score:.0f}/100)")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"❌ RISK ASSESSOR: Assessment failed: {str(e)}")
        return json.dumps({"error": f"Risk assessment failed: {str(e)}"})

def design_portfolio_allocation(investment_parameters: str) -> str:
    """Design optimal portfolio allocation based on risk profile and goals"""
    try:
        logger.info("🎯 PORTFOLIO ARCHITECT: Designing asset allocation")
        data = json.loads(investment_parameters) if isinstance(investment_parameters, str) else investment_parameters
        
        risk_profile = data.get("risk_profile", "moderate")
        investment_amount = data.get("investment_amount", 0)
        timeline_years = data.get("timeline_years", 10)
        goals = data.get("goals", ["growth"])
        
        # Base allocations by risk profile
        allocation_templates = {
            "aggressive": {
                "stocks": 85, "bonds": 10, "alternatives": 3, "cash": 2,
                "expected_return": 0.09, "volatility": "high"
            },
            "moderate_aggressive": {
                "stocks": 75, "bonds": 20, "alternatives": 3, "cash": 2,
                "expected_return": 0.08, "volatility": "moderate-high"
            },
            "moderate": {
                "stocks": 65, "bonds": 30, "alternatives": 3, "cash": 2,
                "expected_return": 0.07, "volatility": "moderate"
            },
            "conservative_moderate": {
                "stocks": 45, "bonds": 50, "alternatives": 2, "cash": 3,
                "expected_return": 0.06, "volatility": "moderate-low"
            },
            "conservative": {
                "stocks": 25, "bonds": 65, "alternatives": 0, "cash": 10,
                "expected_return": 0.05, "volatility": "low"
            }
        }
        
        base_allocation = allocation_templates.get(risk_profile, allocation_templates["moderate"])
        
        # Adjust allocation based on timeline
        if timeline_years < 3:  # Short term - more conservative
            base_allocation["stocks"] = max(20, base_allocation["stocks"] - 20)
            base_allocation["bonds"] += 15
            base_allocation["cash"] += 5
        elif timeline_years > 15:  # Long term - can be more aggressive
            if risk_profile not in ["conservative", "conservative_moderate"]:
                base_allocation["stocks"] = min(90, base_allocation["stocks"] + 10)
                base_allocation["bonds"] = max(5, base_allocation["bonds"] - 10)
        
        # Detailed sub-allocations within stocks
        stock_allocation = {
            "us_large_cap": base_allocation["stocks"] * 0.40,
            "us_mid_cap": base_allocation["stocks"] * 0.15,
            "us_small_cap": base_allocation["stocks"] * 0.10,
            "international_developed": base_allocation["stocks"] * 0.25,
            "emerging_markets": base_allocation["stocks"] * 0.10
        }
        
        # Bond sub-allocations
        bond_allocation = {
            "us_government": base_allocation["bonds"] * 0.40,
            "us_corporate": base_allocation["bonds"] * 0.35,
            "international_bonds": base_allocation["bonds"] * 0.15,
            "tips": base_allocation["bonds"] * 0.10
        }
        
        # Calculate dollar amounts
        dollar_allocation = {}
        for asset, percentage in base_allocation.items():
            dollar_allocation[asset] = (percentage / 100) * investment_amount
        
        # Specific investment recommendations
        investment_recommendations = []
        if investment_amount >= 10000:
            investment_recommendations = [
                "Use low-cost index funds for core holdings",
                "Consider ETFs for tax efficiency",
                "Rebalance quarterly or when allocation drifts >5%",
                "Dollar-cost average if investing lump sum over 6-12 months"
            ]
        elif investment_amount >= 3000:
            investment_recommendations = [
                "Start with target-date funds for simplicity",
                "Use broad market index funds",
                "Focus on minimizing expense ratios",
                "Set up automatic investing"
            ]
        else:
            investment_recommendations = [
                "Consider robo-advisors for low minimums",
                "Start with broad market ETFs",
                "Focus on consistent monthly contributions",
                "Prioritize tax-advantaged accounts (401k, IRA)"
            ]
        
# agents/investment-agent/agent.py - Full ADK Investment Agent with Sub-Agents
import os
import json
from typing import Dict, Any, List
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

# ADK Tools for Investment Analysis

def assess_risk_profile(financial_data: str) -> str:
    """Comprehensive risk tolerance and capacity assessment"""
    try:
        logger.info("📊 RISK ASSESSOR: Evaluating investment risk profile")
        data = json.loads(financial_data) if isinstance(financial_data, str) else financial_data
        
        # Extract relevant financial data
        age = data.get("age", 35)  # Default age if not provided
        balance = data.get("balance", 0)
        monthly_income = data.get("monthly_income", 0)
        monthly_expenses = data.get("monthly_expenses", 0)
        debt_amount = data.get("debt_amount", 0)
        investment_timeline = data.get("investment_timeline", 10)  # years
        
        # Calculate financial stability metrics
        emergency_fund_ratio = balance / (monthly_expenses * 6) if monthly_expenses > 0 else 0
        debt_to_income = (debt_amount / (monthly_income * 12)) if monthly_income > 0 else 0
        available_monthly = monthly_income - monthly_expenses
        
        # Risk capacity scoring (0-100)
        age_score = min(100, (65 - age) * 2)  # Younger = higher capacity
        stability_score = min(100, emergency_fund_ratio * 50)  # Emergency fund adequacy
        debt_score = max(0, 100 - (debt_to_income * 200))  # Lower debt = higher score
        income_score = min(100, (available_monthly / 1000) * 20) if available_monthly > 0 else 0
        timeline_score = min(100, investment_timeline * 8)  # Longer timeline = higher capacity
        
        risk_capacity_score = (age_score + stability_score + debt_score + income_score + timeline_score) / 5
        
        # Determine risk profile
        if risk_capacity_score >= 80:
            risk_profile = "aggressive"
            risk_level = "high"
        elif risk_capacity_score >= 60:
            risk_profile = "moderate_aggressive"
            risk_level = "moderate-high"
        elif risk_capacity_score >= 40:
            risk_profile = "moderate"
            risk_level = "moderate"
        elif risk_capacity_score >= 20:
            risk_profile = "conservative_moderate"
            risk_level = "moderate-low"
        else:
            risk_profile = "conservative"
            risk_level = "low"
        
        # Generate risk-specific recommendations
        risk_recommendations = {
            "aggressive": [
                "Can handle high volatility for higher returns",
                "Focus on growth stocks and emerging markets",
                "Consider higher allocation to equities (80-90%)"
            ],
            "moderate_aggressive": [
                "Balance growth with some stability",
                "Mix of growth and value investments",
                "Equity allocation around 70-80%"
            ],
            "moderate": [
                "Balanced approach between growth and stability",
                "Diversified portfolio across asset classes",
                "Equity allocation around 60-70%"
            ],
            "conservative_moderate": [
                "Prioritize capital preservation with modest growth",
                "Higher allocation to bonds and stable assets",
                "Equity allocation around 40-50%"
            ],
            "conservative": [
                "Focus on capital preservation",
                "High allocation to bonds and cash equivalents",
                "Equity allocation around 20-30%"
            ]
        }
        
        result = {
            "risk_capacity_score": risk_capacity_score,
            "risk_profile": risk_profile,
            "risk_level": risk_level,
            "profile_factors": {
                "age_factor": age_score,
                "financial_stability": stability_score,
                "debt_burden": debt_score,
                "income_flexibility": income_score,
                "time_horizon": timeline_score
            },
            "recommendations": risk_recommendations.get(risk_profile, []),
            "key_considerations": [
                f"Investment timeline: {investment_timeline} years",
                f"Emergency fund status: {'Adequate' if emergency_fund_ratio >= 1 else 'Needs improvement'}",
                f"Debt-to-income ratio: {debt_to_income:.1%}",
                f"Available monthly for investing: ${available_monthly:.2f}"
            ],
            "confidence": 0.91
        }
        
        logger.info(f"✅ RISK ASSESSOR: Profile determined - {risk_profile} ({risk_capacity_score:.0f}/100)")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"❌ RISK ASSESSOR: Assessment failed: {str(e)}")
        return json.dumps({"error": f"Risk assessment failed: {str(e)}"})

def design_portfolio_allocation(investment_parameters: str) -> str:
    """Design optimal portfolio allocation based on risk profile and goals"""
    try:
        logger.info("🎯 PORTFOLIO ARCHITECT: Designing asset allocation")
        data = json.loads(investment_parameters) if isinstance(investment_parameters, str) else investment_parameters
        
        risk_profile = data.get("risk_profile", "moderate")
        investment_amount = data.get("investment_amount", 0)
        timeline_years = data.get("timeline_years", 10)
        goals = data.get("goals", ["growth"])
        
        # Base allocations by risk profile
        allocation_templates = {
            "aggressive": {
                "stocks": 85, "bonds": 10, "alternatives": 3, "cash": 2,
                "expected_return": 0.09, "volatility": "high"
            },
            "moderate_aggressive": {
                "stocks": 75, "bonds": 20, "alternatives": 3, "cash": 2,
                "expected_return": 0.08, "volatility": "moderate-high"
            },
            "moderate": {
                "stocks": 65, "bonds": 30, "alternatives": 3, "cash": 2,
                "expected_return": 0.07, "volatility": "moderate"
            },
            "conservative_moderate": {
                "stocks": 45, "bonds": 50, "alternatives": 2, "cash": 3,
                "expected_return": 0.06, "volatility": "moderate-low"
            },
            "conservative": {
                "stocks": 25, "bonds": 65, "alternatives": 0, "cash": 10,
                "expected_return": 0.05, "volatility": "low"
            }
        }
        
        base_allocation = allocation_templates.get(risk_profile, allocation_templates["moderate"]).copy()
        
        # Adjust allocation based on timeline
        if timeline_years < 3:  # Short term - more conservative
            base_allocation["stocks"] = max(20, base_allocation["stocks"] - 20)
            base_allocation["bonds"] += 15
            base_allocation["cash"] += 5
        elif timeline_years > 15:  # Long term - can be more aggressive
            if risk_profile not in ["conservative", "conservative_moderate"]:
                base_allocation["stocks"] = min(90, base_allocation["stocks"] + 10)
                base_allocation["bonds"] = max(5, base_allocation["bonds"] - 10)
        
        # Detailed sub-allocations within stocks
        stock_allocation = {
            "us_large_cap": base_allocation["stocks"] * 0.40,
            "us_mid_cap": base_allocation["stocks"] * 0.15,
            "us_small_cap": base_allocation["stocks"] * 0.10,
            "international_developed": base_allocation["stocks"] * 0.25,
            "emerging_markets": base_allocation["stocks"] * 0.10
        }
        
        # Bond sub-allocations
        bond_allocation = {
            "us_government": base_allocation["bonds"] * 0.40,
            "us_corporate": base_allocation["bonds"] * 0.35,
            "international_bonds": base_allocation["bonds"] * 0.15,
            "tips": base_allocation["bonds"] * 0.10
        }
        
        # Calculate dollar amounts
        dollar_allocation = {}
        for asset, percentage in base_allocation.items():
            dollar_allocation[asset] = (percentage / 100) * investment_amount
        
        # Specific investment recommendations
        investment_recommendations = []
        if investment_amount >= 10000:
            investment_recommendations = [
                "Use low-cost index funds for core holdings",
                "Consider ETFs for tax efficiency",
                "Rebalance quarterly or when allocation drifts >5%",
                "Dollar-cost average if investing lump sum over 6-12 months"
            ]
        elif investment_amount >= 3000:
            investment_recommendations = [
                "Start with target-date funds for simplicity",
                "Use broad market index funds",
                "Focus on minimizing expense ratios",
                "Set up automatic investing"
            ]
        else:
            investment_recommendations = [
                "Consider robo-advisors for low minimums",
                "Start with broad market ETFs",
                "Focus on consistent monthly contributions",
                "Prioritize tax-advantaged accounts (401k, IRA)"
            ]
        
        result = {
            "portfolio_allocation": base_allocation,
            "dollar_allocation": dollar_allocation,
            "stock_breakdown": stock_allocation,
            "bond_breakdown": bond_allocation,
            "expected_annual_return": base_allocation["expected_return"],
            "volatility_level": base_allocation["volatility"],
            "investment_recommendations": investment_recommendations,
            "rebalancing_schedule": "Quarterly review, rebalance when >5% drift",
            "tax_considerations": [
                "Use tax-advantaged accounts first (401k, IRA)",
                "Consider tax-loss harvesting in taxable accounts",
                "Hold tax-inefficient investments in tax-deferred accounts",
                "Consider index funds for tax efficiency"
            ],
            "confidence": 0.89
        }
        
        logger.info(f"✅ PORTFOLIO ARCHITECT: Designed {risk_profile} portfolio - {base_allocation['stocks']}% stocks")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"❌ PORTFOLIO ARCHITECT: Design failed: {str(e)}")
        return json.dumps({"error": f"Portfolio design failed: {str(e)}"})

def calculate_retirement_projections(retirement_data: str) -> str:
    """Calculate retirement savings projections and requirements"""
    try:
        logger.info("🏖️ RETIREMENT PLANNER: Calculating retirement projections")
        data = json.loads(retirement_data) if isinstance(retirement_data, str) else retirement_data
        
        current_age = data.get("current_age", 35)
        retirement_age = data.get("retirement_age", 65)
        current_retirement_savings = data.get("current_savings", 0)
        monthly_contribution = data.get("monthly_contribution", 0)
        expected_return = data.get("expected_return", 0.07)
        current_income = data.get("current_income", 60000)
        replacement_ratio = data.get("replacement_ratio", 0.80)  # 80% of current income
        
        years_to_retirement = retirement_age - current_age
        years_in_retirement = 90 - retirement_age  # Assume living to 90
        
        # Calculate future value of current savings
        future_value_current = current_retirement_savings * ((1 + expected_return) ** years_to_retirement)
        
        # Calculate future value of monthly contributions (annuity)
        if expected_return > 0:
            future_value_contributions = monthly_contribution * 12 * (((1 + expected_return) ** years_to_retirement - 1) / expected_return)
        else:
            future_value_contributions = monthly_contribution * 12 * years_to_retirement
        
        total_projected_savings = future_value_current + future_value_contributions
        
        # Calculate retirement income need
        inflation_rate = 0.025  # 2.5% annual inflation
        future_income_need = current_income * ((1 + inflation_rate) ** years_to_retirement)
        annual_retirement_need = future_income_need * replacement_ratio
        
        # Calculate required retirement savings using 4% withdrawal rule
        required_retirement_savings = annual_retirement_need / 0.04
        
        # Calculate shortfall or surplus
        shortfall = max(0, required_retirement_savings - total_projected_savings)
        surplus = max(0, total_projected_savings - required_retirement_savings)
        
        # Calculate additional monthly savings needed to close shortfall
        if shortfall > 0 and years_to_retirement > 0:
            if expected_return > 0:
                additional_monthly_needed = shortfall / (12 * (((1 + expected_return) ** years_to_retirement - 1) / expected_return))
            else:
                additional_monthly_needed = shortfall / (12 * years_to_retirement)
        else:
            additional_monthly_needed = 0
        
        # Generate recommendations
        recommendations = []
        if shortfall > 0:
            recommendations.extend([
                f"Increase monthly contributions by ${additional_monthly_needed:.2f}",
                "Maximize employer 401(k) matching if available",
                "Consider catch-up contributions if over 50",
                "Review and optimize investment allocation for growth"
            ])
        else:
            recommendations.extend([
                "Current savings trajectory looks good",
                "Continue consistent contributions",
                "Consider increasing contributions with salary raises",
                "Review allocation as you approach retirement"
            ])
        
        # Milestone projections
        milestones = {}
        for years in [5, 10, 15, 20, 25]:
            if years <= years_to_retirement:
                milestone_age = current_age + years
                projected_value = (current_retirement_savings * ((1 + expected_return) ** years) + 
                                 monthly_contribution * 12 * (((1 + expected_return) ** years - 1) / expected_return if expected_return > 0 else years))
                milestones[f"age_{milestone_age}"] = projected_value
        
        result = {
            "retirement_analysis": {
                "current_age": current_age,
                "retirement_age": retirement_age,
                "years_to_retirement": years_to_retirement,
                "current_savings": current_retirement_savings,
                "monthly_contribution": monthly_contribution
            },
            "projections": {
                "total_projected_savings": total_projected_savings,
                "required_savings": required_retirement_savings,
                "annual_retirement_income_need": annual_retirement_need,
                "projected_monthly_income": total_projected_savings * 0.04 / 12
            },
            "gap_analysis": {
                "shortfall": shortfall,
                "surplus": surplus,
                "additional_monthly_needed": additional_monthly_needed,
                "on_track": shortfall == 0
            },
            "milestone_projections": milestones,
            "recommendations": recommendations,
            "assumptions": {
                "expected_return": f"{expected_return:.1%}",
                "inflation_rate": "2.5%",
                "withdrawal_rate": "4.0%",
                "replacement_ratio": f"{replacement_ratio:.0%}"
            },
            "confidence": 0.87
        }
        
        status = "on track" if shortfall == 0 else f"${shortfall:,.0f} shortfall"
        logger.info(f"✅ RETIREMENT PLANNER: Analysis complete - {status}")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"❌ RETIREMENT PLANNER: Calculation failed: {str(e)}")
        return json.dumps({"error": f"Retirement projection failed: {str(e)}"})

def optimize_tax_strategy(tax_data: str) -> str:
    """Analyze and optimize investment tax strategy"""
    try:
        logger.info("💰 TAX OPTIMIZER: Analyzing investment tax strategy")
        data = json.loads(tax_data) if isinstance(tax_data, str) else tax_data
        
        current_income = data.get("current_income", 60000)
        tax_bracket = data.get("tax_bracket", 0.22)  # 22% federal bracket
        investment_accounts = data.get("investment_accounts", {})
        available_401k = data.get("available_401k", True)
        available_ira = data.get("available_ira", True)
        available_roth_ira = data.get("available_roth_ira", True)
        
        # 2024 contribution limits
        contribution_limits = {
            "401k": 23000,
            "ira": 7000,
            "roth_ira": 7000,
            "hsa": 4300  # Individual HSA limit
        }
        
        # Tax optimization strategies
        tax_strategies = []
        potential_tax_savings = 0
        
        # 401(k) optimization
        if available_401k:
            current_401k = investment_accounts.get("401k", 0)
            max_401k_contribution = min(contribution_limits["401k"], current_income * 0.15)  # Reasonable limit
            additional_401k = max(0, max_401k_contribution - current_401k)
            
            if additional_401k > 0:
                tax_savings = additional_401k * tax_bracket
                potential_tax_savings += tax_savings
                tax_strategies.append({
                    "strategy": "Maximize 401(k) contributions",
                    "current_contribution": current_401k,
                    "recommended_contribution": max_401k_contribution,
                    "additional_needed": additional_401k,
                    "annual_tax_savings": tax_savings,
                    "priority": "high"
                })
        
        # IRA vs Roth IRA analysis
        if available_ira or available_roth_ira:
            current_ira = investment_accounts.get("ira", 0) + investment_accounts.get("roth_ira", 0)
            ira_space = contribution_limits["ira"] - current_ira
            
            if ira_space > 0:
                # Recommend traditional IRA for high tax bracket, Roth for lower
                if tax_bracket >= 0.22:
                    recommended_ira = "traditional"
                    tax_savings = ira_space * tax_bracket
                    potential_tax_savings += tax_savings
                else:
                    recommended_ira = "roth"
                    tax_savings = 0  # No immediate tax savings, but tax-free growth
                
                tax_strategies.append({
                    "strategy": f"Maximize {recommended_ira} IRA contributions",
                    "current_contribution": current_ira,
                    "recommended_contribution": contribution_limits["ira"],
                    "additional_needed": ira_space,
                    "annual_tax_savings": tax_savings,
                    "rationale": f"Current tax bracket: {tax_bracket:.0%}",
                    "priority": "medium"
                })
        
        # Tax-loss harvesting recommendations
        if investment_accounts.get("taxable", 0) > 0:
            tax_strategies.append({
                "strategy": "Implement tax-loss harvesting",
                "description": "Realize losses to offset capital gains",
                "potential_benefit": "Up to $3,000 annual loss deduction",
                "implementation": [
                    "Review portfolio for unrealized losses",
                    "Harvest losses before year-end",
                    "Avoid wash sale rules (30-day period)",
                    "Reinvest in similar but not identical securities"
                ],
                "priority": "medium"
            })
        
        # Asset location optimization
        asset_location_strategy = {
            "tax_deferred_401k_ira": [
                "Bond funds and REITs (tax-inefficient)",
                "Actively managed funds with high turnover",
                "International funds (foreign tax credits)"
            ],
            "roth_ira": [
                "Highest growth potential investments",
                "Small-cap and emerging market funds",
                "Individual growth stocks"
            ],
            "taxable_account": [
                "Tax-efficient index funds",
                "Individual stocks for long-term holding",
                "Tax-managed funds",
                "Municipal bonds (if high tax bracket)"
            ]
        }
        
        result = {
            "current_tax_situation": {
                "income": current_income,
                "estimated_tax_bracket": f"{tax_bracket:.0%}",
                "current_contributions": investment_accounts
            },
            "optimization_strategies": tax_strategies,
            "total_potential_tax_savings": potential_tax_savings,
            "asset_location_guide": asset_location_strategy,
            "contribution_limits_2024": contribution_limits,
            "key_recommendations": [
                "Prioritize tax-advantaged accounts before taxable investing",
                "Use traditional accounts when in high tax brackets",
                "Consider Roth conversions in low-income years",
                "Implement tax-loss harvesting in taxable accounts"
            ],
            "confidence": 0.85
        }
        
        logger.info(f"✅ TAX OPTIMIZER: Identified ${potential_tax_savings:,.0f} in potential tax savings")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"❌ TAX OPTIMIZER: Optimization failed: {str(e)}")
        return json.dumps({"error": f"Tax optimization failed: {str(e)}"})

# ADK Sub-Agents for Investment Specialization

# Risk Assessment Sub-Agent
risk_assessment_agent = Agent(
    name="risk_assessor",
    model="gemini-2.5-flash",
    description="Comprehensive investment risk tolerance and capacity assessment",
    instruction="""You are the Risk Assessment specialist within the Investment Agent network.
    
    Your expertise:
    📊 **Risk Capacity Analysis**: Objective assessment of financial ability to take risk
    🎯 **Risk Tolerance Evaluation**: Subjective comfort level with investment volatility
    ⚖️ **Profile Matching**: Match investors to appropriate risk-based portfolios
    📈 **Timeline Integration**: Adjust risk recommendations based on investment timeline
    
    Key factors you analyze:
    - Age and time horizon (longer = higher capacity)
    - Financial stability (emergency fund, debt levels)
    - Income consistency and growth potential
    - Investment timeline and goals
    - Overall financial health
    
    Your risk profiles range from conservative to aggressive, with specific allocation recommendations for each level.""",
    tools=[assess_risk_profile]
)

# Portfolio Architecture Sub-Agent
portfolio_architect_agent = Agent(
    name="portfolio_architect",
    model="gemini-2.5-flash",
    description="Designs optimal asset allocation and portfolio construction",
    instruction="""You are the Portfolio Architecture specialist within the Investment Agent network.
    
    Your expertise:
    🎯 **Asset Allocation**: Design optimal mix of stocks, bonds, alternatives
    🏗️ **Portfolio Construction**: Build diversified portfolios across asset classes
    🔄 **Rebalancing Strategy**: Establish maintenance and adjustment protocols
    💼 **Investment Selection**: Recommend specific funds and investment vehicles
    
    Design principles:
    - Diversification across asset classes, sectors, and geographies
    - Cost-efficiency through low-expense index funds and ETFs
    - Tax-efficiency considerations for different account types
    - Simplicity and maintainability for long-term success
    
    You create detailed allocation breakdowns with specific percentages and dollar amounts.""",
    tools=[design_portfolio_allocation]
)

# Retirement Planning Sub-Agent
retirement_planner_agent = Agent(
    name="retirement_planner",
    model="gemini-2.5-flash",
    description="Specialized retirement savings analysis and projection modeling",
    instruction="""You are the Retirement Planning specialist within the Investment Agent network.
    
    Your expertise:
    🏖️ **Retirement Projections**: Model future savings growth and income needs
    📊 **Gap Analysis**: Identify shortfalls and surplus in retirement planning
    💰 **Contribution Optimization**: Calculate optimal savings rates and strategies
    📅 **Milestone Tracking**: Create checkpoints for retirement readiness
    
    Key calculations:
    - Future value projections using compound growth
    - Retirement income replacement ratios (typically 70-90%)
    - Withdrawal rate sustainability (4% rule and variations)
    - Inflation adjustments for future purchasing power
    
    You provide specific dollar amounts for contributions needed and timeline projections.""",
    tools=[calculate_retirement_projections]
)

# Tax Optimization Sub-Agent
tax_optimizer_agent = Agent(
    name="tax_optimizer",
    model="gemini-2.5-flash",
    description="Investment tax strategy optimization and planning",
    instruction="""You are the Tax Optimization specialist within the Investment Agent network.
    
    Your expertise:
    💰 **Tax-Advantaged Accounts**: Maximize 401(k), IRA, and other tax-deferred vehicles
    🏛️ **Asset Location**: Optimize which investments go in which account types
    📉 **Tax-Loss Harvesting**: Implement strategies to minimize taxable gains
    🔄 **Roth Conversions**: Analyze opportunities for tax-free growth strategies
    
    Key strategies:
    - Prioritize tax-deferred contributions for high earners
    - Use Roth accounts for young investors and low-income years
    - Place tax-inefficient investments in tax-deferred accounts
    - Harvest losses to offset gains in taxable accounts
    
    You calculate specific tax savings and provide implementation timelines.""",
    tools=[optimize_tax_strategy]
)

# Main Investment Agent with Full ADK Sub-Agent Architecture
root_agent = Agent(
    name="investment_agent_full_adk",
    model="gemini-2.5-flash",
    description="Comprehensive investment advisory coordinator with specialized sub-agents",
    global_instruction="You are the Investment Advisory Coordinator managing a network of specialized investment sub-agents.",
    instruction="""You are the central Investment Advisory Coordinator that orchestrates multiple specialized sub-agents for comprehensive investment analysis.

🏗️ **ADK Architecture Overview**:
├── **Risk Assessor**: Comprehensive risk tolerance and capacity analysis
├── **Portfolio Architect**: Asset allocation design and portfolio construction
├── **Retirement Planner**: Long-term savings projections and gap analysis
└── **Tax Optimizer**: Investment tax strategy and account optimization

🔄 **Coordination Process**:
1. **Risk Assessment**: Deploy Risk Assessor for profile determination
2. **Portfolio Design**: Engage Portfolio Architect for allocation strategy
3. **Retirement Analysis**: Activate Retirement Planner for long-term projections
4. **Tax Optimization**: Consult Tax Optimizer for account and strategy optimization
5. **Integration**: Synthesize sub-agent recommendations into cohesive strategy
6. **A2A Response**: Format comprehensive investment plan for coordinator

🎯 **Specialization Benefits**:
- **Risk-Aligned Portfolios**: Precise risk matching through dedicated assessment
- **Optimized Allocations**: Professional portfolio construction methodology
- **Retirement Readiness**: Detailed projections and milestone tracking
- **Tax Efficiency**: Maximized after-tax returns through strategic planning

📡 **A2A Integration**:
When receiving coordinator requests, you coordinate sub-agents to provide:
- Comprehensive risk profile with specific allocation recommendations
- Detailed portfolio design with dollar amounts and rebalancing schedule
- Retirement projections with gap analysis and contribution recommendations
- Tax optimization strategies with specific savings calculations

This demonstrates enterprise-grade ADK sub-agent architecture for sophisticated investment advisory services in the GKE hackathon environment.""",
    sub_agents=[risk_assessment_agent, portfolio_architect_agent, retirement_planner_agent, tax_optimizer_agent],
    tools=[]  # Main agent coordinates sub-agents through their specialized tools
)
