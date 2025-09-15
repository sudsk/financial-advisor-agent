# agents/coordinator/agent_logic.py
import asyncio
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import httpx
import vertexai
from vertexai.generative_models import GenerativeModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentRequest:
    agent_type: str
    data: Dict[str, Any]
    priority: int = 1

@dataclass 
class AgentResponse:
    agent_type: str
    result: Dict[str, Any]
    confidence: float
    recommendations: List[str]

class FinancialCoordinator:
    def __init__(self, project_id: str, region: str, mcp_server_url: str):
        self.project_id = project_id
        self.region = region
        self.mcp_server_url = mcp_server_url
        self.client = None
        self.model = None
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=region)
        self.model = GenerativeModel('gemini-pro')
        
        # Agent endpoints (A2A Protocol)
        self.agents = {
            "budget": "http://budget-agent.financial-advisor.svc.cluster.local:8080/analyze",
            "investment": "http://investment-agent.financial-advisor.svc.cluster.local:8080/recommend", 
            "security": "http://security-agent.financial-advisor.svc.cluster.local:8080/assess"
        }
    
    async def initialize(self):
        """Initialize the coordinator"""
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("Financial Coordinator initialized")
    
    async def get_user_financial_data(self, user_id: str, account_id: str) -> Dict:
        """Get comprehensive financial data via MCP"""
        try:
            response = await self.client.post(
                f"{self.mcp_server_url}/tools/get_financial_snapshot",
                json={"user_id": user_id, "account_id": account_id}
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"MCP server error: {response.status_code}")
                return {"error": f"MCP server error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Failed to get financial data: {str(e)}")
            return {"error": f"Failed to get financial data: {str(e)}"}
    
    async def analyze_user_query(self, query: str, user_data: Dict) -> Dict:
        """Use Gemini to understand user intent and plan agent coordination"""
        
        prompt = f"""
        Analyze this financial query and determine what agents should be involved:
        
        User Query: "{query}"
        
        User Financial Context:
        - Current Balance: ${user_data.get('balance', {}).get('amount', 0)}
        - Monthly Spending: ${user_data.get('spending_analysis', {}).get('average_monthly', 0)}
        - Top Spending Categories: {list(user_data.get('spending_analysis', {}).get('categories', {}).keys())[:3]}
        
        Return a JSON response with:
        1. "intent": What the user wants to accomplish
        2. "required_agents": List of agents needed ["budget", "investment", "security"]  
        3. "agent_priorities": Priority order (1=highest)
        4. "context_for_agents": Specific data each agent needs
        5. "expected_outcome": What kind of response to provide
        
        Focus on practical, actionable financial advice.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Error analyzing user query: {str(e)}")
            # Fallback plan
            return {
                "intent": "general_financial_advice",
                "required_agents": ["budget", "investment", "security"],
                "agent_priorities": {"budget": 1, "investment": 2, "security": 3},
                "context_for_agents": {"all": user_data},
                "expected_outcome": "comprehensive_financial_plan"
            }
    
    async def coordinate_agents(self, plan: Dict, user_data: Dict) -> List[AgentResponse]:
        """Coordinate multiple agents using A2A protocol"""
        
        agent_tasks = []
        for agent_name in plan["required_agents"]:
            if agent_name in self.agents:
                task = self.call_agent(
                    agent_name, 
                    user_data, 
                    plan["context_for_agents"]
                )
                agent_tasks.append(task)
        
        # Execute agents in parallel
        agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # Process results
        responses = []
        for i, result in enumerate(agent_results):
            agent_name = plan["required_agents"][i]
            if not isinstance(result, Exception):
                responses.append(AgentResponse(
                    agent_type=agent_name,
                    result=result,
                    confidence=result.get("confidence", 0.8),
                    recommendations=result.get("recommendations", [])
                ))
        
        return responses
    
    async def call_agent(self, agent_name: str, user_data: Dict, context: Dict) -> Dict:
        """Call individual agent via A2A protocol"""
        
        agent_url = self.agents[agent_name]
        
        payload = {
            "user_data": user_data,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "requesting_agent": "coordinator"
        }
        
        try:
            response = await self.client.post(
                agent_url,
                json=payload,
                timeout=30.0
            )
            return response.json()
        except Exception as e:
            return {
                "error": f"Agent {agent_name} failed: {str(e)}",
                "confidence": 0.0,
                "recommendations": []
            }
    
    async def synthesize_response(self, query: str, agent_responses: List[AgentResponse]) -> Dict:
        """Use Gemini to create final coordinated response"""
        
        # Prepare agent insights for Gemini
        agent_insights = {}
        for response in agent_responses:
            agent_insights[response.agent_type] = {
                "recommendations": response.recommendations,
                "confidence": response.confidence,
                "key_data": response.result
            }
        
        prompt = f"""
        Create a comprehensive financial advice response based on these agent analyses:
        
        Original User Query: "{query}"
        
        Agent Insights:
        {json.dumps(agent_insights, indent=2)}
        
        Create a response that:
        1. Directly answers the user's question
        2. Combines insights from all agents
        3. Provides specific, actionable recommendations
        4. Explains the reasoning
        5. Suggests next steps
        
        Format as JSON with:
        - "summary": Brief answer to user's query
        - "detailed_plan": Step-by-step recommendations  
        - "key_insights": Important findings from agents
        - "next_actions": Specific things user should do
        - "monitoring": How to track progress
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            return {
                "summary": "I've analyzed your financial situation with our specialized agents.",
                "detailed_plan": [rec for resp in agent_responses for rec in resp.recommendations],
                "key_insights": [f"{resp.agent_type} agent provided analysis" for resp in agent_responses],
                "next_actions": ["Review the recommendations", "Consider implementing suggested changes"],
                "monitoring": "Track your progress monthly"
            }
    
    async def process_financial_query(self, user_id: str, account_id: str, query: str) -> Dict:
        """Main coordination workflow"""
        
        # Step 1: Get user financial data via MCP
        user_data = await self.get_user_financial_data(user_id, account_id)
        
        # Step 2: Analyze query and plan agent coordination  
        plan = await self.analyze_user_query(query, user_data)
        
        # Step 3: Coordinate agents using A2A protocol
        agent_responses = await self.coordinate_agents(plan, user_data)
        
        # Step 4: Synthesize final response
        final_response = await self.synthesize_response(query, agent_responses)
        
        # Step 5: Add metadata
        final_response["metadata"] = {
            "agents_used": [resp.agent_type for resp in agent_responses],
            "confidence_scores": {resp.agent_type: resp.confidence for resp in agent_responses},
            "processing_time": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        return final_response
    
    async def close(self):
        await self.client.aclose()
