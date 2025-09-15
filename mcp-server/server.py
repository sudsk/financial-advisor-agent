# mcp-server/server.py
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
import asyncio
import json
from bank_anthos_client import BankOfAnthosClient
from typing import Dict, Any, List

# Initialize MCP Server
app = Server("financial-advisor-mcp")
bank_client = BankOfAnthosClient()

@app.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="bank://user-profile",
            name="User Profile Data",
            mimeType="application/json"
        ),
        Resource(
            uri="bank://account-balance", 
            name="Account Balance Information",
            mimeType="application/json"
        ),
        Resource(
            uri="bank://transaction-history",
            name="Transaction History",
            mimeType="application/json"
        ),
        Resource(
            uri="bank://spending-analysis",
            name="Spending Pattern Analysis",
            mimeType="application/json"
        )
    ]

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_user_data",
            description="Get comprehensive user financial data",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "include_transactions": {"type": "boolean", "default": True},
                    "transaction_days": {"type": "integer", "default": 30}
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="analyze_spending",
            description="Analyze user spending patterns for budgeting",
            inputSchema={
                "type": "object", 
                "properties": {
                    "account_id": {"type": "string"},
                    "analysis_days": {"type": "integer", "default": 90}
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="get_financial_snapshot",
            description="Get complete financial snapshot for investment analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "account_id": {"type": "string"}
                },
                "required": ["user_id", "account_id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    
    if name == "get_user_data":
        user_id = arguments["user_id"]
        include_transactions = arguments.get("include_transactions", True)
        transaction_days = arguments.get("transaction_days", 30)
        
        # Get user profile
        profile = await bank_client.get_user_profile(user_id)
        
        result = {"profile": profile}
        
        if include_transactions and "account_id" in profile:
            transactions = await bank_client.get_transaction_history(
                profile["account_id"], transaction_days
            )
            result["transactions"] = transactions
            
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "analyze_spending":
        account_id = arguments["account_id"]
        analysis_days = arguments.get("analysis_days", 90)
        
        analysis = await bank_client.analyze_spending_patterns(account_id, analysis_days)
        
        return [TextContent(
            type="text", 
            text=json.dumps(analysis, indent=2)
        )]
    
    elif name == "get_financial_snapshot":
        user_id = arguments["user_id"] 
        account_id = arguments["account_id"]
        
        # Get comprehensive financial data
        profile = await bank_client.get_user_profile(user_id)
        balance = await bank_client.get_account_balance(account_id)
        transactions = await bank_client.get_transaction_history(account_id, 30)
        spending_analysis = await bank_client.analyze_spending_patterns(account_id, 90)
        contacts = await bank_client.get_user_contacts(user_id)
        
        snapshot = {
            "profile": profile,
            "balance": balance, 
            "recent_transactions": transactions[:10],  # Latest 10
            "spending_analysis": spending_analysis,
            "contacts": contacts,
            "timestamp": str(asyncio.get_event_loop().time())
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(snapshot, indent=2)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"})
        )]

async def main():
    # Import transport implementation
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, 
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
