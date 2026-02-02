"""Tool wrappers for LangChain that call MCPs over HTTP.

Each tool appends a structured record to action_logs so the orchestrator
can build a single natural-language summary after the agent finishes.
"""
from typing import Dict, List
import os
import json
import requests
from langchain_core.tools import Tool


# In-memory action log for a single agent run. Cleared by orchestrator before each run.
action_logs: List[Dict] = []


def clear_action_logs():
    global action_logs
    action_logs = []


def get_action_logs() -> List[Dict]:
    return action_logs


def _post(url: str, path: str, payload: Dict):
    r = requests.post(f"{url}{path}", json=payload, timeout=8)
    r.raise_for_status()
    return r.json()


def _record(entry: Dict):
    action_logs.append(entry)


def authorize_tool(tool_input: str) -> str:
    """Check if user is authorized for an action"""
    try:
        data = json.loads(tool_input)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON input: {str(e)}", "allowed": False})
    
    id_url = os.getenv("IDENTITY_MCP_URL", "http://identity:8001")
    resp = _post(id_url, "/authorize", data)
    entry = {"tool": "authorize", "user": data.get("user"), "action": data.get("action"), "result": resp}
    _record(entry)
    return json.dumps(resp)


def execute_action_tool(tool_input: str) -> str:
    """Execute an action like restarting a service.
    
    IMPORTANT: This tool enforces Identity validation internally.
    If the user is not authorized, the action will be denied.
    """
    try:
        data = json.loads(tool_input)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON input: {str(e)}", "success": False})
    
    # First check authorization
    id_url = os.getenv("IDENTITY_MCP_URL", "http://identity:8001")
    try:
        auth_resp = _post(id_url, "/authorize", data)
        if not auth_resp.get("allowed"):
            entry = {"tool": "execute_action", "user": data.get("user"), "action": data.get("action"), "result": {"success": False, "message": "Authorization denied"}}
            _record(entry)
            return json.dumps({"success": False, "message": "Authorization denied. User not authorized for this action."})
    except Exception as e:
        entry = {"tool": "execute_action", "user": data.get("user"), "action": data.get("action"), "result": {"success": False, "message": f"Authorization check failed: {str(e)}"}}
        _record(entry)
        return json.dumps({"success": False, "message": f"Authorization check failed: {str(e)}"})
    
    # If authorized, execute the action
    ops_url = os.getenv("OPERATIONS_MCP_URL", "http://operations:8003")
    resp = _post(ops_url, "/execute_action", data)
    entry = {"tool": "execute_action", "user": data.get("user"), "action": data.get("action"), "result": resp}
    _record(entry)
    return json.dumps(resp)


def log_audit_tool(tool_input: str) -> str:
    """Log an audit entry"""
    try:
        data = json.loads(tool_input)
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Invalid JSON input: {str(e)}", "logged": False})
    
    audit_url = os.getenv("AUDIT_MCP_URL", "http://audit:8006")
    resp = _post(audit_url, "/log", data)
    entry = {"tool": "log_audit", "user_id": data.get("user_id"), "action": data.get("action"), "result": resp}
    _record(entry)
    return json.dumps(resp)


def get_langchain_tools():
    """Returns all MCP tools wrapped as LangChain Tools."""
    return [
        Tool(
            name="authorize",
            func=authorize_tool,
            description='Check if user is authorized for an action. Input: JSON string with user dict, action string, and trace_id'
        ),
        Tool(
            name="execute_action",
            func=execute_action_tool,
            description='Execute an action like restarting a service. Input: JSON string with user dict, action string, and trace_id'
        ),
        Tool(
            name="log_audit",
            func=log_audit_tool,
            description='Log an audit entry. Input: JSON string with user_id, action, result, reason, and trace_id'
        ),
    ]
