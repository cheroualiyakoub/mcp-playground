"""
Configuration for Enterprise MCP Workshop
"""

# API Configuration
OPENROUTER_API_KEY = None  # Set via environment variable

# Default users for demo
DEMO_USERS = {
    "alice": {
        "role": "admin",
        "token": "admin-token",
        "email": "alice@company.com"
    },
    "bob": {
        "role": "operator",
        "token": "operator-token",
        "email": "bob@company.com"
    },
    "charlie": {
        "role": "viewer",
        "token": "viewer-token",
        "email": "charlie@company.com"
    }
}

# RBAC Policies
RBAC_POLICIES = {
    "admin": {
        "allowed_actions": ["restart_service", "stop_service", "view_logs", "view_status"],
        "description": "Full access to all operations"
    },
    "operator": {
        "allowed_actions": ["restart_service", "view_logs", "view_status"],
        "description": "Can restart services and view logs"
    },
    "viewer": {
        "allowed_actions": ["view_logs", "view_status"],
        "description": "Read-only access"
    }
}