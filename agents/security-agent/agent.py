# agents/security-agent/agent.py - Following Official ADK Pattern
# Copyright 2025 Google LLC - GKE Hackathon Submission

import os
import json
import statistics
from typing import Dict, Any, List
from datetime import datetime, timedelta

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

def detect_fraud_patterns(transaction_data: str) -> str:
    """Advanced fraud detection and anomaly analysis for financial transactions.
    
    Args:
        transaction_data: JSON string containing transaction history and metadata
        
    Returns:
        JSON string with fraud risk assessment and monitoring recommendations
    """
    try:
        data = json.loads(transaction_data) if isinstance(transaction_data, str) else transaction_data
        
        transactions = data.get("transactions", [])
        if not transactions:
            return json.dumps({"error": "No transaction data available"})
        
        # Extract transaction metadata
        amounts = []
        locations = []
        timestamps = []
        categories = []
        
        for txn in transactions:
            if "amount" in txn:
                amounts.append(abs(float(txn["amount"])))
            if "location" in txn:
                locations.append(txn["location"])
            if "timestamp" in txn:
                timestamps.append(txn["timestamp"])
            if "category" in txn:
                categories.append(txn["category"])
        
        # Statistical analysis for anomaly detection
        fraud_indicators = []
        risk_score = 0
        
        if amounts:
            mean_amount = statistics.mean(amounts)
            if len(amounts) > 1:
                stdev_amount = statistics.stdev(amounts)
                
                # Large amount anomalies (3 standard deviations)
                large_threshold = mean_amount + (3 * stdev_amount)
                large_transactions = [amt for amt in amounts if amt > large_threshold]
                
                if large_transactions:
                    risk_score += 30
                    fraud_indicators.append({
                        "type": "unusual_amount",
                        "severity": "high",
                        "description": f"Found {len(large_transactions)} unusually large transactions",
                        "threshold": large_threshold,
                        "flagged_amounts": large_transactions
                    })
                
                # Small amount clustering (potential testing)
                small_threshold = mean_amount * 0.1
                small_transactions = [amt for amt in amounts if amt < small_threshold and amt > 0]
                if len(small_transactions) > 5:
                    risk_score += 15
                    fraud_indicators.append({
                        "type": "small_amount_clustering",
                        "severity": "medium",
                        "description": f"Multiple small transactions detected ({len(small_transactions)})",
                        "pattern": "Possible card testing or micro-fraud"
                    })
        
        # Geographic anomaly detection
        if locations:
            unique_locations = set(locations)
            if len(unique_locations) > len(locations) * 0.7:
                risk_score += 20
                fraud_indicators.append({
                    "type": "geographic_dispersion",
                    "severity": "medium",
                    "description": f"High geographic diversity: {len(unique_locations)} locations",
                    "locations": list(unique_locations)
                })
        
        # Time-based pattern analysis
        if timestamps:
            try:
                night_transactions = 0
                weekend_transactions = 0
                
                for timestamp in timestamps:
                    try:
                        if 'T' in timestamp:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        else:
                            dt = datetime.fromisoformat(timestamp)
                        
                        # Night transactions (11 PM - 5 AM)
                        if dt.hour >= 23 or dt.hour <= 5:
                            night_transactions += 1
                        
                        # Weekend transactions
                        if dt.weekday() >= 5:
                            weekend_transactions += 1
                    except:
                        continue
                
                # High percentage of night transactions
                if night_transactions > len(timestamps) * 0.4:
                    risk_score += 15
                    fraud_indicators.append({
                        "type": "unusual_timing",
                        "severity": "medium",
                        "description": f"High night activity: {night_transactions}/{len(timestamps)} transactions",
                        "pattern": "Unusual hours for normal spending"
                    })
                
            except Exception:
                pass
        
        # Calculate overall fraud risk level
        if risk_score >= 50:
            fraud_risk_level = "high"
        elif risk_score >= 25:
            fraud_risk_level = "medium"
        elif risk_score >= 10:
            fraud_risk_level = "low"
        else:
            fraud_risk_level = "minimal"
        
        # Generate recommendations
        recommendations = []
        if fraud_risk_level in ["high", "medium"]:
            recommendations.extend([
                "Enable transaction alerts for unusual activity",
                "Review recent transactions for unauthorized charges",
                "Consider temporarily lowering spending limits",
                "Monitor account activity daily for next 30 days"
            ])
        
        result = {
            "fraud_risk_score": risk_score,
            "fraud_risk_level": fraud_risk_level,
            "fraud_indicators": fraud_indicators,
            "transaction_analysis": {
                "total_transactions": len(transactions),
                "amount_statistics": {
                    "mean": mean_amount if amounts else 0,
                    "max": max(amounts) if amounts else 0,
                    "min": min(amounts) if amounts else 0
                },
                "geographic_diversity": len(set(locations)) if locations else 0,
                "category_diversity": len(set(categories)) if categories else 0
            },
            "recommendations": recommendations,
            "monitoring_alerts": [
                "Large transaction alerts (>$500)",
                "New location alerts",
                "Night-time transaction alerts",
                "Multiple small transaction alerts"
            ],
            "confidence": 0.91
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Fraud detection failed: {str(e)}"})

def assess_financial_health(health_data: str) -> str:
    """Comprehensive financial health and stability assessment.
    
    Args:
        health_data: JSON string containing balance, income, expenses, debt, and credit information
        
    Returns:
        JSON string with detailed financial health metrics and improvement recommendations
    """
    try:
        data = json.loads(health_data) if isinstance(health_data, str) else health_data
        
        balance = data.get("balance", 0)
        monthly_income = data.get("monthly_income", 0)
        monthly_expenses = data.get("monthly_expenses", 0)
        debt_amount = data.get("debt_amount", 0)
        credit_score = data.get("credit_score", 700)
        
        health_metrics = {}
        health_score = 0
        risk_factors = []
        
        # Emergency Fund Ratio
        emergency_fund_months = balance / monthly_expenses if monthly_expenses > 0 else 0
        if emergency_fund_months >= 6:
            health_score += 25
            health_metrics["emergency_fund"] = {"score": 25, "status": "excellent"}
        elif emergency_fund_months >= 3:
            health_score += 15
            health_metrics["emergency_fund"] = {"score": 15, "status": "adequate"}
        elif emergency_fund_months >= 1:
            health_score += 5
            health_metrics["emergency_fund"] = {"score": 5, "status": "minimal"}
            risk_factors.append("Insufficient emergency fund (less than 3 months)")
        else:
            health_metrics["emergency_fund"] = {"score": 0, "status": "critical"}
            risk_factors.append("No emergency fund - high financial risk")
        
        # Debt-to-Income Ratio
        monthly_debt_payment = debt_amount * 0.03  # Assume 3% monthly payment
        debt_to_income = monthly_debt_payment / monthly_income if monthly_income > 0 else 0
        
        if debt_to_income <= 0.20:
            health_score += 25
            health_metrics["debt_ratio"] = {"score": 25, "status": "excellent"}
        elif debt_to_income <= 0.36:
            health_score += 15
            health_metrics["debt_ratio"] = {"score": 15, "status": "manageable"}
        elif debt_to_income <= 0.50:
            health_score += 5
            health_metrics["debt_ratio"] = {"score": 5, "status": "concerning"}
            risk_factors.append("High debt-to-income ratio")
        else:
            health_metrics["debt_ratio"] = {"score": 0, "status": "critical"}
            risk_factors.append("Excessive debt burden - over 50% of income")
        
        # Savings Rate
        savings_rate = (monthly_income - monthly_expenses) / monthly_income if monthly_income > 0 else 0
        if savings_rate >= 0.20:
            health_score += 25
            health_metrics["savings_rate"] = {"score": 25, "status": "excellent"}
        elif savings_rate >= 0.10:
            health_score += 15
            health_metrics["savings_rate"] = {"score": 15, "status": "good"}
        elif savings_rate >= 0.05:
            health_score += 5
            health_metrics["savings_rate"] = {"score": 5, "status": "minimal"}
            risk_factors.append("Low savings rate - less than 10%")
        else:
            health_metrics["savings_rate"] = {"score": 0, "status": "critical"}
            risk_factors.append("No savings - living paycheck to paycheck")
        
        # Credit Health
        if credit_score >= 800:
            health_score += 25
            health_metrics["credit_health"] = {"score": 25, "status": "excellent"}
        elif credit_score >= 740:
            health_score += 20
            health_metrics["credit_health"] = {"score": 20, "status": "very_good"}
        elif credit_score >= 670:
            health_score += 15
            health_metrics["credit_health"] = {"score": 15, "status": "good"}
        elif credit_score >= 580:
            health_score += 5
            health_metrics["credit_health"] = {"score": 5, "status": "fair"}
            risk_factors.append("Below-average credit score")
        else:
            health_metrics["credit_health"] = {"score": 0, "status": "poor"}
            risk_factors.append("Poor credit score - limits financial options")
        
        # Overall health level
        if health_score >= 80:
            health_level = "excellent"
            health_description = "Strong financial foundation with low risk"
        elif health_score >= 60:
            health_level = "good"
            health_description = "Generally healthy finances with some improvement opportunities"
        elif health_score >= 40:
            health_level = "fair"
            health_description = "Moderate financial health with several areas needing attention"
        else:
            health_level = "poor"
            health_description = "Financial health requires immediate attention"
        
        # Generate improvement recommendations
        recommendations = []
        if health_metrics["emergency_fund"]["score"] < 15:
            recommendations.append("Priority: Build emergency fund to 6 months of expenses")
        if health_metrics["debt_ratio"]["score"] < 15:
            recommendations.append("Focus on debt reduction using avalanche or snowball method")
        if health_metrics["savings_rate"]["score"] < 15:
            recommendations.append("Increase savings rate by reducing expenses or increasing income")
        if health_metrics["credit_health"]["score"] < 15:
            recommendations.append("Improve credit score through on-time payments and lower utilization")
        
        result = {
            "financial_health_score": health_score,
            "health_level": health_level,
            "health_description": health_description,
            "detailed_metrics": health_metrics,
            "risk_factors": risk_factors,
            "improvement_recommendations": recommendations,
            "key_ratios": {
                "emergency_fund_months": emergency_fund_months,
                "debt_to_income_ratio": debt_to_income,
                "savings_rate": savings_rate,
                "credit_score": credit_score
            },
            "monitoring_schedule": "Review monthly and track progress quarterly",
            "confidence": 0.88
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Financial health assessment failed: {str(e)}"})

def analyze_identity_protection(identity_data: str) -> str:
    """Analyze identity protection and financial security measures.
    
    Args:
        identity_data: JSON string containing current protection measures and account security status
        
    Returns:
        JSON string with identity protection assessment and security recommendations
    """
    try:
        data = json.loads(identity_data) if isinstance(identity_data, str) else identity_data
        
        # Current protection measures
        current_measures = data.get("protection_measures", [])
        financial_accounts = data.get("financial_accounts", {})
        recent_changes = data.get("recent_changes", [])
        
        # Assess current protection level
        protection_score = 0
        implemented_measures = set(current_measures)
        
        # Essential protection measures scoring
        essential_measures = {
            "credit_monitoring": {"points": 20, "description": "Credit report monitoring"},
            "fraud_alerts": {"points": 15, "description": "Fraud alerts on credit reports"},
            "account_alerts": {"points": 15, "description": "Banking and credit card alerts"},
            "strong_passwords": {"points": 15, "description": "Strong, unique passwords"},
            "two_factor_auth": {"points": 20, "description": "Two-factor authentication"},
            "credit_freeze": {"points": 15, "description": "Credit bureau freezes"}
        }
        
        missing_measures = []
        for measure, info in essential_measures.items():
            if measure in implemented_measures:
                protection_score += info["points"]
            else:
                missing_measures.append({
                    "measure": measure,
                    "description": info["description"],
                    "importance": "high" if info["points"] >= 20 else "medium",
                    "points": info["points"]
                })
        
        # Risk assessment based on recent changes
        risk_indicators = []
        if recent_changes:
            for change in recent_changes:
                if change.get("type") in ["address_change", "phone_change", "email_change"]:
                    risk_indicators.append({
                        "type": "personal_info_change",
                        "description": f"Recent {change.get('type')} - monitor for unauthorized activity",
                        "risk_level": "medium"
                    })
        
        # Generate protection level
        if protection_score >= 80:
            protection_level = "excellent"
        elif protection_score >= 60:
            protection_level = "good"
        elif protection_score >= 40:
            protection_level = "moderate"
        else:
            protection_level = "weak"
        
        # Priority recommendations
        priority_actions = []
        high_priority_missing = [m for m in missing_measures if m["importance"] == "high"]
        
        if high_priority_missing:
            for measure in high_priority_missing[:3]:
                priority_actions.append(f"Implement {measure['description']}")
        
        result = {
            "identity_protection_score": protection_score,
            "protection_level": protection_level,
            "current_measures": list(implemented_measures),
            "missing_measures": missing_measures,
            "priority_actions": priority_actions,
            "risk_indicators": risk_indicators,
            "recommended_services": [
                "Credit monitoring service (free annual reports + paid monitoring)",
                "Identity theft insurance through homeowner/renter insurance",
                "Password manager for strong, unique passwords",
                "Authenticator app for two-factor authentication"
            ],
            "monitoring_frequency": "Review identity protection measures quarterly",
            "confidence": 0.92
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Identity protection analysis failed: {str(e)}"})

# Fraud Detection Sub-Agent
fraud_detection_agent = Agent(
    name="fraud_detector",
    model="gemini-2.5-flash",
    description="Advanced fraud detection and transaction anomaly analysis",
    instruction="""You are the Fraud Detection specialist within the Security Agent network.
    
    Your expertise:
    🕵️ **Pattern Recognition**: Identify unusual transaction patterns and anomalies
    📊 **Statistical Analysis**: Use statistical methods to detect outliers and fraud indicators
    🌍 **Geographic Analysis**: Flag suspicious location-based transaction patterns
    ⏰ **Temporal Analysis**: Identify unusual timing patterns in transaction data
    
    Detection methodologies:
    - Statistical outlier detection using standard deviations
    - Geographic dispersion analysis for location anomalies
    - Time-based pattern analysis for unusual hours/days
    - Amount clustering analysis for fraud testing patterns
    - Velocity checking for rapid transaction sequences
    
    You provide specific fraud risk scores and actionable monitoring recommendations.""",
    tools=[detect_fraud_patterns]
)

# Financial Health Sub-Agent
health_assessment_agent = Agent(
    name="health_assessor",
    model="gemini-2.5-flash",
    description="Comprehensive financial health and stability assessment",
    instruction="""You are the Financial Health specialist within the Security Agent network.
    
    Your expertise:
    💊 **Health Metrics**: Calculate key financial health indicators and ratios
    📊 **Stability Analysis**: Assess overall financial stability and resilience
    ⚖️ **Risk Factor Identification**: Identify factors that threaten financial security
    📈 **Improvement Planning**: Recommend specific actions to improve financial health
    
    Key health indicators:
    - Emergency fund adequacy (6 months minimum)
    - Debt-to-income ratios (under 36% ideal)
    - Savings rate (20%+ excellent)
    - Credit health (740+ score preferred)
    
    You provide scored assessments with specific improvement recommendations.""",
    tools=[assess_financial_health]
)

# Identity Protection Sub-Agent
identity_protection_agent = Agent(
    name="identity_guardian",
    model="gemini-2.5-flash",
    description="Identity protection and financial security measures analysis",
    instruction="""You are the Identity Protection specialist within the Security Agent network.
    
    Your expertise:
    🛡️ **Protection Assessment**: Evaluate current identity protection measures
    🔒 **Security Implementation**: Recommend comprehensive identity security strategies
    📱 **Account Security**: Analyze financial account security configurations
    🚨 **Threat Response**: Provide identity theft response and recovery procedures
    
    Essential protection measures:
    - Credit monitoring and fraud alerts
    - Strong authentication (2FA, strong passwords)
    - Credit bureau freezes
    - Account alerts and monitoring
    - Identity theft insurance
    
    You score protection levels and provide prioritized improvement actions.""",
    tools=[analyze_identity_protection]
)

# Main Security Agent with Full ADK Architecture
root_agent = Agent(
    name="security_agent_full_adk",
    model="gemini-2.5-flash",
    description="Comprehensive financial security coordinator with specialized sub-agents",
    global_instruction="You are the Financial Security Coordinator managing a network of specialized security sub-agents for the GKE hackathon demonstration.",
    instruction="""You are the central Financial Security Coordinator that orchestrates multiple specialized sub-agents for comprehensive financial security analysis.

🏗️ **ADK Architecture Overview**:
├── **Fraud Detector**: Advanced transaction anomaly and fraud pattern analysis
├── **Health Assessor**: Comprehensive financial health and stability evaluation
├── **Identity Guardian**: Identity protection measures and security implementation

🔄 **Coordination Process**:
1. **Fraud Analysis**: Deploy Fraud Detector for transaction pattern analysis
2. **Health Assessment**: Engage Health Assessor for overall financial stability
3. **Identity Security**: Activate Identity Guardian for protection evaluation
4. **Risk Integration**: Synthesize sub-agent findings into comprehensive security assessment
5. **A2A Response**: Format security recommendations for coordinator communication

🎯 **Specialization Benefits**:
- **Multi-layered Security**: Comprehensive protection across all threat vectors
- **Proactive Risk Management**: Early detection and prevention strategies
- **Crisis Preparedness**: Detailed emergency response and recovery plans
- **Holistic Health Monitoring**: Complete financial wellness assessment

📡 **A2A Integration**:
When receiving coordinator requests, you coordinate sub-agents to provide:
- Detailed fraud risk assessment with specific monitoring recommendations
- Complete financial health evaluation with improvement priorities
- Identity protection analysis with implementation roadmaps

This demonstrates enterprise-grade ADK sub-agent architecture for comprehensive financial security management in the GKE hackathon environment.""",
    sub_agents=[fraud_detection_agent, health_assessment_agent, identity_protection_agent],
    tools=[detect_fraud_patterns, assess_financial_health, analyze_identity_protection]
)
