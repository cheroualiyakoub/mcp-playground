#!/usr/bin/env python3
"""
Enterprise MCP Workshop Client
Demonstrates connecting to MCP server and using LangGraph agent
"""

import os
import sys
import uuid
import json
from typing import Optional
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

# Try to load .env from src directory or project root
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try project root
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# For MCP client connection
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("⚠️  MCP client library not available. Install with: uv add mcp")
    print("    For demo purposes, we'll use direct tool calls instead.")
    ClientSession = None


class EnterpriseMCPClient:
    """Client for Enterprise MCP Workshop with LangGraph agent"""
    
    def __init__(self, openrouter_api_key: Optional[str] = None):
        """
        Initialize the MCP client with LangGraph agent.
        
        Args:
            openrouter_api_key: OpenRouter API key (or set OPENROUTER_API_KEY env var)
        """
        # Setup API key
        self.api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY env var or pass to constructor.\n"
                "Get free key at: https://openrouter.ai/keys"
            )
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            openai_api_key=self.api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0
        )
        
        # Context for current request
        self.current_context = {
            "user_id": None,
            "token": None,
            "trace_id": None
        }
        
        # Create tools
        self.tools = self._create_tools()
        
        # Create agent
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools
        )
        
        print("✅ Enterprise MCP Client initialized")
        print(f"   Model: google/gemini-2.0-flash-thinking-exp:free")
        print(f"   Tools: {len(self.tools)} available")
    
    def _create_tools(self):
        """Create LangChain tools that wrap MCP calls"""
        
        @tool
        def authorize(action: str) -> str:
            """
            Check if the current user is authorized to perform an action.
            Call this FIRST before executing any system action.
            
            Args:
                action: One of: restart_service, stop_service, view_logs, view_status
                
            Returns:
                JSON with allowed (bool) and reason (str)
            """
            # In a real implementation, this would call the MCP server
            # For demo, we simulate the authorization logic
            result = self._simulate_authorize(
                user_id=self.current_context["user_id"],
                token=self.current_context["token"],
                action=action,
                trace_id=self.current_context["trace_id"]
            )
            return json.dumps(result)
        
        @tool
        def execute_action(action: str) -> str:
            """
            Execute a system action. Only call this AFTER authorize returns allowed=true.
            
            Args:
                action: One of: restart_service, stop_service, view_logs, view_status
                
            Returns:
                JSON with success (bool), result, and reason
            """
            result = self._simulate_execute(
                action=action,
                trace_id=self.current_context["trace_id"]
            )
            return json.dumps(result)
        
        @tool
        def query_audit_log(user_id: Optional[str] = None, limit: int = 5) -> str:
            """
            Query the audit log for recent actions.
            
            Args:
                user_id: Filter by user (optional)
                limit: Maximum entries to return (default: 5)
                
            Returns:
                JSON with audit entries
            """
            result = self._simulate_audit_query(user_id=user_id, limit=limit)
            return json.dumps(result)
        
        return [authorize, execute_action, query_audit_log]
    
    def _simulate_authorize(self, user_id: str, token: str, action: str, trace_id: str) -> dict:
        """Simulate authorization check (would call MCP server in production)"""
        # Hardcoded demo data
        users = {
            "alice": {"role": "admin", "token": "admin-token"},
            "bob": {"role": "operator", "token": "operator-token"},
            "charlie": {"role": "viewer", "token": "viewer-token"}
        }
        
        policies = {
            "admin": ["restart_service", "stop_service", "view_logs", "view_status"],
            "operator": ["restart_service", "view_logs", "view_status"],
            "viewer": ["view_logs", "view_status"]
        }
        
        if user_id not in users:
            return {"allowed": False, "reason": f"user '{user_id}' not found"}
        
        if users[user_id]["token"] != token:
            return {"allowed": False, "reason": "invalid token"}
        
        role = users[user_id]["role"]
        if action in policies[role]:
            return {"allowed": True, "reason": "authorized", "user": {"user_id": user_id, "role": role}}
        else:
            return {"allowed": False, "reason": f"role '{role}' cannot perform '{action}'"}
    
    def _simulate_execute(self, action: str, trace_id: str) -> dict:
        """Simulate action execution (would call MCP server in production)"""
        if action == "restart_service":
            return {"success": True, "result": "ok", "reason": "web_server restarted successfully"}
        elif action == "stop_service":
            return {"success": True, "result": "ok", "reason": "web_server stopped successfully"}
        elif action == "view_status":
            return {
                "success": True,
                "result": "ok",
                "reason": "status retrieved",
                "details": {"web_server": "running", "database": "running", "cache": "running"}
            }
        elif action == "view_logs":
            return {
                "success": True,
                "result": "ok",
                "reason": "logs retrieved",
                "details": {"logs": ["[INFO] System started", "[INFO] Ready"]}
            }
        else:
            return {"success": False, "result": "error", "reason": f"unknown action: '{action}'"}
    
    def _simulate_audit_query(self, user_id: Optional[str] = None, limit: int = 5) -> dict:
        """Simulate audit query (would call MCP server in production)"""
        return {
            "total": 0,
            "entries": [],
            "note": "Audit log is empty or no matching entries"
        }
    
    def run_prompt(self, user_id: str, token: str, prompt: str, verbose: bool = True) -> dict:
        """
        Process a user prompt through the LangGraph agent.
        
        Args:
            user_id: User making the request
            token: Authentication token
            prompt: Natural language prompt
            verbose: Print detailed execution info
            
        Returns:
            Dictionary with response and metadata
        """
        trace_id = str(uuid.uuid4())[:8]
        
        # Set context
        self.current_context = {
            "user_id": user_id,
            "token": token,
            "trace_id": trace_id
        }
        
        # Get user role for system prompt
        users = {
            "alice": "admin",
            "bob": "operator",
            "charlie": "viewer"
        }
        user_role = users.get(user_id, "unknown")
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"🚀 USER: {user_id} ({user_role})")
            print(f"📝 PROMPT: {prompt}")
            print(f"🔗 TRACE ID: {trace_id}")
            print(f"{'='*80}\n")
        
        # System prompt
        system_message = f"""You are the Enterprise MCP Orchestrator, a helpful AI assistant for system management.

CURRENT USER: {user_id} (role: {user_role})
TRACE ID: {trace_id}

CRITICAL RULE: Respond to ALL parts of the user's message!

RESPONSE PROTOCOL:
1. GREETINGS: If user says hello/hi/hey → greet them warmly
2. QUESTIONS: If user asks questions → answer them
3. SYSTEM ACTIONS: If user requests operations → use the tools

SYSTEM ACTIONS PROCEDURE:
Available actions: restart_service, stop_service, view_logs, view_status

When user requests a system action:
1. FIRST: Call 'authorize' tool with the action
2. IF allowed=true → Call 'execute_action' tool
3. IF allowed=false → Inform user they lack permission

ROLE PERMISSIONS:
- admin: All actions (restart, stop, view)
- operator: restart_service, view_logs, view_status
- viewer: view_logs, view_status only

Answer ALL questions and greetings while handling system actions."""
        
        try:
            # Collect messages
            all_messages = []
            step_count = 0
            
            if verbose:
                print("🤖 AGENT THINKING...\n" + "-"*80)
            
            for chunk in self.agent.stream(
                {
                    "messages": [
                        SystemMessage(content=system_message),
                        HumanMessage(content=prompt)
                    ]
                },
                stream_mode="values"
            ):
                all_messages.extend(chunk.get("messages", []))
                if verbose and len(chunk.get("messages", [])) > 0:
                    msg = chunk["messages"][-1]
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        step_count += 1
                        for tc in msg.tool_calls:
                            print(f"  🔧 Step {step_count}: Calling {tc['name']}({tc['args']})")
            
            if verbose:
                print("-"*80 + "\n")
            
            # Extract final response
            final_response = all_messages[-1] if all_messages else None
            response = final_response.content if final_response else "No response generated"
            
            if verbose:
                print(f"✅ FINAL ANSWER:")
                print("="*80)
                print(response)
                print("="*80)
                print(f"\n📊 STATISTICS:")
                print(f"   • Total messages: {len(all_messages)}")
                print(f"   • Processing steps: {step_count}")
                print(f"   • Trace ID: {trace_id}")
                print("="*80 + "\n")
            
            return {
                "trace_id": trace_id,
                "response": response,
                "success": True,
                "steps": step_count,
                "total_messages": len(all_messages)
            }
            
        except Exception as e:
            if verbose:
                print(f"\n❌ ERROR: {str(e)}\n")
            return {
                "trace_id": trace_id,
                "response": f"Error: {str(e)}",
                "success": False
            }


def main():
    """Demo scenarios for workshop"""
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENROUTER_API_KEY environment variable not set")
        print("\nTo fix:")
        print("  export OPENROUTER_API_KEY='your-key-here'")
        print("\nGet a free key at: https://openrouter.ai/keys")
        sys.exit(1)
    
    # Initialize client
    print("🚀 Initializing Enterprise MCP Workshop Client...")
    print("="*80)
    client = EnterpriseMCPClient(openrouter_api_key=api_key)
    print("="*80 + "\n")
    
    # Demo scenarios
    scenarios = [
        {
            "name": "Admin restarts service",
            "user": "alice",
            "token": "admin-token",
            "prompt": "Hello! Please restart the web server."
        },
        {
            "name": "Viewer views status",
            "user": "charlie",
            "token": "viewer-token",
            "prompt": "Show me the system status and tell me what's the capital of France?"
        },
        {
            "name": "Viewer denied restart",
            "user": "charlie",
            "token": "viewer-token",
            "prompt": "Restart the server please"
        },
        {
            "name": "Operator stops service (denied)",
            "user": "bob",
            "token": "operator-token",
            "prompt": "Stop the web server"
        },
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'🧪 SCENARIO ' + str(i)}: {scenario['name']} {'='*50}")
        client.run_prompt(
            user_id=scenario["user"],
            token=scenario["token"],
            prompt=scenario["prompt"],
            verbose=True
        )
        
        if i < len(scenarios):
            input("\n⏸️  Press Enter to continue to next scenario...")


if __name__ == "__main__":
    main()