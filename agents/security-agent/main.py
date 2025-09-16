# agents/security-agent/main.py
from flask import Flask, request, jsonify
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import os
import vertexai
from vertexai.generative_models import GenerativeModel
import statistics
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class SecurityAgent:
    def __init__(self, project_id: str, region: str):
        self.project_id = project_id
        self.region = region
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=region)
        self.model = GenerativeModel('gemini-pro')
        logger.info(f"Security Agent initialized with project {project_id} in region {region}")
    
    def analyze_transaction_patterns(self, transactions: List[Dict]) -> Dict:
        """Analyze transaction patterns for security risks"""
        
        if not transactions:
            return {"risk_score": 0, "patterns": [], "anomalies": []}
        
        # Analyze spending patterns
        amounts = [abs(t.get("amount", 0)) for t in transactions if t.get("amount", 0) < 0]
        locations = [t.get("location", "unknown") for t in transactions]
        times = [t.get("timestamp", "") for t in transactions]
        
        anomalies = []
        risk_factors = []
        
        if amounts:
            # Check for unusual amounts
            avg_amount = statistics.mean(amounts)
            std_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            for transaction in transactions:
                amount = abs(transaction.get("amount", 0))
                if amount > avg_amount + (2 * std_amount) and amount > 1000:
                    anomalies.append(f"Large transaction: ${amount}")
        
        # Check for geographical anomalies
        unique_locations = set(locations)
        if len(unique_locations) > 5:  # Many different locations
            risk_factors.append("High geographical diversity in transactions")
        
        # Check for time-based patterns
        try:
            night_transactions = sum(1 for t in transactions 
                                   if "timestamp" in t and 
                                   datetime.fromisoformat(t["timestamp"].replace('Z', '+00:00')).hour < 6)
            
            if night_transactions > len(transactions) * 0.3:
                risk_factors.append("High number of late-night transactions")
        except Exception as e:
            logger.warning(f"Error analyzing transaction times: {str(e)}")
        
        # Calculate overall risk score
        risk_score = min(1.0, (len(anomalies) * 0.3 + len(risk_factors) * 0.2))
        
        return {
            "risk_score": risk_score,
            "anomalies": anomalies,
            "risk_factors": risk_factors,
            "transaction_count": len(transactions),
            "avg_transaction_amount": avg_amount if amounts else 0
        }
    
    def assess_financial_health_risks(self, user_data: Dict) -> Dict:
        """Assess overall financial health and security risks"""
        
        balance = user_data.get("balance", {}).get("amount", 0)
        spending_analysis = user_data.get("spending_analysis", {})
        monthly_spending = spending_analysis.get("average_monthly", 0)
        
        risks = []
        recommendations = []
        
        # Emergency fund analysis
        emergency_fund_ratio = balance / (monthly_spending * 6) if monthly_spending > 0 else 0
        if emergency_fund_ratio < 0.5:
            risks.append("Insufficient emergency fund (less than 3 months expenses)")
            recommendations.append("Build emergency fund to 6 months of expenses")
        
        # Debt-to-income analysis (simplified)
        categories = spending_analysis.get("categories", {})
        debt_payments = categories.get("Debt Payments", 0) + categories.get("Credit Cards", 0)
        if debt_payments > monthly_spending * 0.3:
            risks.append("High debt-to-income ratio")
            recommendations.append("Focus on debt reduction strategies")
        
        # Diversification risk
        if balance > 50000 and "investment" not in str(user_data).lower():
            risks.append("Lack of investment diversification")
            recommendations.append("Consider diversifying into investment accounts")
        
        return {
            "financial_health_score": max(0, 1 - len(risks) * 0.2),
            "emergency_fund_ratio": emergency_fund_ratio,
            "identified_risks": risks,
            "security_recommendations": recommendations
        }
    
    async def generate_security_assessment(self, user_data: Dict, context: Dict) -> Dict:
        """Generate comprehensive security assessment using Vertex AI Gemini"""
        
        transactions = user_data.get("recent_transactions", [])
        balance = user_data.get("balance", {})
        spending_analysis = user_data.get("spending_analysis", {})
        
        # Analyze transaction patterns
        transaction_analysis = self.analyze_transaction_patterns(transactions)
        financial_health = self.assess_financial_health_risks(user_data)
        
        prompt = f"""
        As a financial security expert, analyze this user's financial situation for risks and security concerns:
        
        Financial Data:
        - Current Balance: ${balance.get('amount', 0)}
        - Monthly Spending: ${spending_analysis.get('average_monthly', 0)}
        - Transaction Pattern Risk Score: {transaction_analysis['risk_score']}
        - Financial Health Score: {financial_health['financial_health_score']}
        
        Transaction Analysis:
        - Anomalies: {transaction_analysis['anomalies']}
        - Risk Factors: {transaction_analysis['risk_factors']}
        
        Financial Health Risks:
        - Identified Risks: {financial_health['identified_risks']}
        
        User Context: {json.dumps(context, indent=2)}
        
        Provide security assessment in JSON format:
        {{
            "overall_security_score": 0.85,
            "security_assessment": "Overall assessment of financial security",
            "fraud_risk_level": "low|medium|high",
            "identity_protection": ["Identity protection recommendations"],
            "account_security": ["Account security best practices"],
            "financial_stability": ["Financial stability recommendations"],
            "monitoring_alerts": ["What to monitor for security"],
            "emergency_procedures": ["What to do if security breach occurs"],
            "confidence": 0.90
        }}
        
        Focus on practical, actionable security measures.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)
            
            # Add our analysis
            result.update({
                "transaction_pattern_analysis": transaction_analysis,
                "financial_health_analysis": financial_health,
                "agent_type": "security",
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Security analysis failed: {str(e)}")
            return {
                "error": f"Security analysis failed: {str(e)}",
                "confidence": 0.0,
                "recommendations": ["Unable to perform security analysis at this time"]
            }

# Initialize agent with environment variables
PROJECT_ID = os.getenv('PROJECT_ID', 'your-project-id')
REGION = os.getenv('REGION', 'us-central1')

security_agent = SecurityAgent(PROJECT_ID, REGION)

@app.route('/assess', methods=['POST'])
async def assess_security():
    """A2A Protocol endpoint for security assessment"""
    try:
        data = request.get_json()
        
        user_data = data.get("user_data", {})
        context = data.get("context", {})
        requesting_agent = data.get("requesting_agent", "unknown")
        
        # Perform security analysis
        result = await security_agent.generate_security_assessment(user_data, context)
        
        # A2A Protocol response format
        response = {
            "agent_type": "security",
            "requesting_agent": requesting_agent,
            "result": result,
            "confidence": result.get("confidence", 0.9),
            "recommendations": result.get("account_security", []) + result.get("financial_stability", []),
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Security assessment error: {str(e)}")
        return jsonify({
            "agent_type": "security",
            "error": str(e),
            "confidence": 0.0,
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "agent": "security",
        "status": "healthy",
        "project_id": PROJECT_ID,
        "region": REGION,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
