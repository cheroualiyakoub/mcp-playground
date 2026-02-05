#!/usr/bin/env python3
"""
Enterprise MCP Workshop Server
Built with FastMCP - demonstrates Identity, Operations, and Audit MCPs
"""

from datetime import datetime, timedelta
import json
import uuid
from typing import Optional

import pandas as pd
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Enterprise MCP Workshop")

# =============================================================================
# SIMULATED DATABASES
# =============================================================================

# Users database
users_df = pd.DataFrame([
    {
        "user_id": "alice",
        "role": "admin",
        "token": "admin-token",
        "email": "alice@company.com",
        "created_at": datetime(2024, 1, 1, 9, 0, 0)
    },
    {
        "user_id": "bob",
        "role": "operator",
        "token": "operator-token",
        "email": "bob@company.com",
        "created_at": datetime(2024, 1, 15, 10, 30, 0)
    },
    {
        "user_id": "charlie",
        "role": "viewer",
        "token": "viewer-token",
        "email": "charlie@company.com",
        "created_at": datetime(2024, 2, 1, 14, 0, 0)
    }
]).set_index("user_id")

# Policies database (RBAC)
policies_df = pd.DataFrame([
    {
        "role": "admin",
        "allowed_actions": ["restart_service", "stop_service", "view_logs", "view_status"],
        "description": "Full access to all operations",
        "max_risk_level": 100
    },
    {
        "role": "operator",
        "allowed_actions": ["restart_service", "view_logs", "view_status"],
        "description": "Can restart services and view logs, cannot stop services",
        "max_risk_level": 70
    },
    {
        "role": "viewer",
        "allowed_actions": ["view_logs", "view_status"],
        "description": "Read-only access to logs and status",
        "max_risk_level": 20
    }
]).set_index("role")

# Audit log (append-only)
audit_df = pd.DataFrame(columns=[
    "timestamp", "trace_id", "user_id", "action", "result", "reason", "mcp_source"
])
audit_df["timestamp"] = pd.to_datetime(audit_df["timestamp"])

# Services state
services_state = {
    "web_server": {
        "status": "running",
        "last_restart": datetime.now() - timedelta(days=5),
        "uptime_seconds": 5 * 24 * 60 * 60
    },
    "database": {
        "status": "running",
        "last_restart": datetime.now() - timedelta(days=30),
        "uptime_seconds": 30 * 24 * 60 * 60
    },
    "cache": {
        "status": "running",
        "last_restart": datetime.now() - timedelta(hours=12),
        "uptime_seconds": 12 * 60 * 60
    }
}

# =============================================================================
# MCP TOOLS - Identity & Authorization
# =============================================================================

@mcp.tool()
def authorize(user_id: str, token: str, action: str, trace_id: str) -> dict:
    """
    Check if user is authorized to perform an action.
    
    Args:
        user_id: The user attempting the action
        token: Authentication token
        action: Action to authorize (restart_service, stop_service, view_logs, view_status)
        trace_id: Unique trace identifier for auditing
        
    Returns:
        Dictionary with allowed (bool), reason (str), and user info
    """
    global audit_df
    
    # Check if user exists
    if user_id not in users_df.index:
        result = {"allowed": False, "reason": f"user '{user_id}' not found", "user": None}
        _log_audit(trace_id, user_id, action, "denied", result["reason"], "identity")
        return result
    
    # Validate token
    user = users_df.loc[user_id].to_dict()
    if user.get("token") != token:
        result = {
            "allowed": False,
            "reason": "invalid token",
            "user": {"user_id": user_id, "role": user.get("role")}
        }
        _log_audit(trace_id, user_id, action, "denied", result["reason"], "identity")
        return result
    
    # Check role permissions
    role = user.get("role")
    if role not in policies_df.index:
        result = {
            "allowed": False,
            "reason": f"role '{role}' has no policy",
            "user": {"user_id": user_id, "role": role}
        }
        _log_audit(trace_id, user_id, action, "denied", result["reason"], "identity")
        return result
    
    allowed_actions = policies_df.loc[role, "allowed_actions"]
    if action in allowed_actions:
        result = {
            "allowed": True,
            "reason": "authorized",
            "user": {"user_id": user_id, "role": role}
        }
        _log_audit(trace_id, user_id, action, "success", result["reason"], "identity")
        return result
    else:
        result = {
            "allowed": False,
            "reason": f"role '{role}' cannot perform '{action}'",
            "user": {"user_id": user_id, "role": role}
        }
        _log_audit(trace_id, user_id, action, "denied", result["reason"], "identity")
        return result


# =============================================================================
# MCP TOOLS - Operations
# =============================================================================

@mcp.tool()
def execute_action(action: str, trace_id: str, user_id: str) -> dict:
    """
    Execute a system action after authorization.
    
    Args:
        action: Action to execute (restart_service, stop_service, view_logs, view_status)
        trace_id: Unique trace identifier for auditing
        user_id: User executing the action (for audit)
        
    Returns:
        Dictionary with success (bool), result, reason, and optional details
    """
    global services_state
    
    if action == "restart_service":
        services_state["web_server"]["status"] = "running"
        services_state["web_server"]["last_restart"] = datetime.now()
        result = {
            "success": True,
            "result": "ok",
            "reason": "web_server restarted successfully"
        }
        _log_audit(trace_id, user_id, action, "success", result["reason"], "operations")
        return result
        
    elif action == "stop_service":
        services_state["web_server"]["status"] = "stopped"
        result = {
            "success": True,
            "result": "ok",
            "reason": "web_server stopped successfully"
        }
        _log_audit(trace_id, user_id, action, "success", result["reason"], "operations")
        return result
        
    elif action == "view_status":
        status = {svc: state["status"] for svc, state in services_state.items()}
        result = {
            "success": True,
            "result": "ok",
            "reason": "status retrieved",
            "details": status
        }
        _log_audit(trace_id, user_id, action, "success", result["reason"], "operations")
        return result
        
    elif action == "view_logs":
        logs = [
            "[INFO] System started",
            "[INFO] Database connected",
            "[INFO] Cache initialized",
            "[INFO] Ready to serve requests"
        ]
        result = {
            "success": True,
            "result": "ok",
            "reason": "logs retrieved",
            "details": {"logs": logs}
        }
        _log_audit(trace_id, user_id, action, "success", result["reason"], "operations")
        return result
        
    else:
        result = {
            "success": False,
            "result": "error",
            "reason": f"unknown action: '{action}'"
        }
        _log_audit(trace_id, user_id, action, "error", result["reason"], "operations")
        return result


# =============================================================================
# MCP TOOLS - Audit
# =============================================================================

@mcp.tool()
def query_audit_log(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    result: Optional[str] = None,
    trace_id: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    Query the audit log with optional filters.
    
    Args:
        user_id: Filter by user (optional)
        action: Filter by action (optional)
        result: Filter by result (success/denied/error) (optional)
        trace_id: Filter by trace_id (optional)
        limit: Maximum number of entries to return (default: 10)
        
    Returns:
        JSON string with audit entries
    """
    df = audit_df.copy()
    
    if user_id:
        df = df[df["user_id"] == user_id]
    if action:
        df = df[df["action"] == action]
    if result:
        df = df[df["result"] == result]
    if trace_id:
        df = df[df["trace_id"] == trace_id]
    
    entries = df.tail(limit).to_dict('records')
    
    # Convert timestamps to strings
    for entry in entries:
        if 'timestamp' in entry:
            entry['timestamp'] = str(entry['timestamp'])
    
    return json.dumps({
        "total": len(entries),
        "entries": entries
    }, indent=2)


@mcp.tool()
def get_user_info(user_id: str) -> dict:
    """
    Get information about a user.
    
    Args:
        user_id: The user ID to look up
        
    Returns:
        Dictionary with user information or error
    """
    if user_id in users_df.index:
        user = users_df.loc[user_id].to_dict()
        user["user_id"] = user_id
        # Don't expose the token
        user.pop("token", None)
        user["created_at"] = str(user.get("created_at"))
        return user
    return {"error": f"User '{user_id}' not found"}


@mcp.tool()
def get_role_permissions(role: str) -> dict:
    """
    Get the permissions for a specific role.
    
    Args:
        role: The role to look up (admin, operator, viewer)
        
    Returns:
        Dictionary with role permissions or error
    """
    if role in policies_df.index:
        return policies_df.loc[role].to_dict()
    return {"error": f"Role '{role}' not found"}


# =============================================================================
# MCP RESOURCES - Provide access to current state
# =============================================================================

@mcp.resource("system://services/status")
def get_services_status() -> str:
    """Get current status of all services"""
    return json.dumps(services_state, indent=2, default=str)


@mcp.resource("system://users/list")
def get_users_list() -> str:
    """Get list of all users (without tokens)"""
    users = []
    for user_id in users_df.index:
        user = users_df.loc[user_id].to_dict()
        user["user_id"] = user_id
        user.pop("token", None)
        user["created_at"] = str(user.get("created_at"))
        users.append(user)
    return json.dumps(users, indent=2)


@mcp.resource("system://policies/rbac")
def get_rbac_policies() -> str:
    """Get all RBAC policies"""
    policies = []
    for role in policies_df.index:
        policy = policies_df.loc[role].to_dict()
        policy["role"] = role
        policies.append(policy)
    return json.dumps(policies, indent=2)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _log_audit(trace_id: str, user_id: str, action: str, result: str, reason: str, mcp_source: str):
    """Internal helper to log to audit trail"""
    global audit_df
    entry = {
        "timestamp": datetime.now(),
        "trace_id": trace_id,
        "user_id": user_id,
        "action": action,
        "result": result,
        "reason": reason,
        "mcp_source": mcp_source
    }
    new_row = pd.DataFrame([entry])
    if len(audit_df) == 0:
        audit_df = new_row
    else:
        audit_df = pd.concat([audit_df, new_row], ignore_index=True)


# =============================================================================
# PROMPTS - Provide guidance to LLMs
# =============================================================================

@mcp.prompt()
def enterprise_workflow(user_id: str, user_role: str) -> str:
    """
    System prompt for enterprise MCP workflow.
    
    Args:
        user_id: The current user ID
        user_role: The current user's role
    """
    return f"""You are the Enterprise MCP Orchestrator, managing system operations with security and audit controls.

CURRENT USER: {user_id} (role: {user_role})

WORKFLOW FOR SYSTEM ACTIONS:
1. First call 'authorize' with user_id, token, action, and trace_id
2. If allowed=true, call 'execute_action' with the action and trace_id
3. If allowed=false, inform the user they lack permission
4. All actions are automatically logged in the audit trail

AVAILABLE ACTIONS:
- restart_service: Restart the web server
- stop_service: Stop the web server (admin only)
- view_logs: View system logs
- view_status: Check service status

ROLE PERMISSIONS:
- admin: All actions (restart, stop, view)
- operator: restart_service, view_logs, view_status
- viewer: view_logs, view_status only

Always generate a unique trace_id (use UUID) for each request to track related actions.
Be helpful and conversational, but enforce security policies strictly."""


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    print("🚀 Starting Enterprise MCP Workshop Server...")
    print("=" * 60)
    print(f"📊 Loaded {len(users_df)} users")
    print(f"📋 Loaded {len(policies_df)} roles")
    print(f"⚙️  Monitoring {len(services_state)} services")
    print("=" * 60)
    mcp.run()