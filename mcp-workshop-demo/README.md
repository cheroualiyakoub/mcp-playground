# Enterprise MCP Workshop Demo

A hands-on demonstration of Model Context Protocol (MCP) with FastMCP, showcasing enterprise patterns like Identity/Authorization, Operations, and Audit logging.

## 🎯 What You'll Learn

- **MCP Architecture**: Build servers with tools, resources, and prompts
- **FastMCP**: Simplified MCP server development
- **LangGraph Agents**: Connect LLMs to MCP tools
- **Enterprise Patterns**: Authorization, RBAC, audit logging
- **Workshop Ready**: Perfect for live demonstrations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LangGraph Agent                      │
│              (OpenRouter + Gemini 2.0)                  │
└───────────────────┬─────────────────────────────────────┘
                    │
                    │ Uses Tools
                    ▼
┌─────────────────────────────────────────────────────────┐
│              FastMCP Server (server.py)                 │
├─────────────────────────────────────────────────────────┤
│  Tools:                                                 │
│   • authorize() - Check permissions (Identity MCP)      │
│   • execute_action() - Run operations (Operations MCP)  │
│   • query_audit_log() - View audit trail (Audit MCP)   │
│                                                         │
│  Resources:                                             │
│   • system://services/status                           │
│   • system://users/list                                │
│   • system://policies/rbac                             │
│                                                         │
│  Prompts:                                               │
│   • enterprise_workflow() - System guidance            │
└─────────────────────────────────────────────────────────┘
```

## Project Structure
```
mcp-workshop-demo
├── src
│   ├── __init__.py
│   ├── server.py       # FastMCP server with tools, resources, prompts
│   ├── client.py       # LangGraph agent client
│   └── config.py       # Configuration and demo data
├── pyproject.toml      # uv/pip dependencies
├── uv.lock            # Locked dependencies
└── README.md
```

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.10+**
- **uv** package manager ([install here](https://github.com/astral-sh/uv))
- **OpenRouter API Key** (free at [openrouter.ai/keys](https://openrouter.ai/keys))

### 2. Installation

```bash
# Navigate to the project
cd mcp-workshop-demo

# Install dependencies with uv (creates venv automatically)
uv sync

# Set your OpenRouter API key
export OPENROUTER_API_KEY='your-key-here'
```

### 3. Run the MCP Server

```bash
# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows

# Start the FastMCP server
uv run python src/server.py
```

The server will start and display:
```
🚀 Starting Enterprise MCP Workshop Server...
============================================================
📊 Loaded 3 users
📋 Loaded 3 roles
⚙️  Monitoring 3 services
============================================================
```

### 4. Run the Client Demo

In a **new terminal**:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Set API key
export OPENROUTER_API_KEY='your-key-here'

# Run the interactive demo
uv run python src/client.py
```

You'll see 4 demo scenarios:
1. ✅ Admin restarts service (allowed)
2. ✅ Viewer views status (allowed)
3. ❌ Viewer tries to restart (denied)
4. ❌ Operator tries to stop service (denied)

## 📚 Understanding the Code

### Server (`src/server.py`)

The server implements three enterprise MCPs in one:

#### 1. **Identity MCP** - Authorization
```python
@mcp.tool()
def authorize(user_id: str, token: str, action: str, trace_id: str) -> dict:
    """Check if user is authorized to perform an action"""
    # Validates user, token, and role permissions
    # Logs to audit trail
```

#### 2. **Operations MCP** - Execution
```python
@mcp.tool()
def execute_action(action: str, trace_id: str, user_id: str) -> dict:
    """Execute a system action after authorization"""
    # Performs: restart_service, stop_service, view_logs, view_status
    # Logs to audit trail
```

#### 3. **Audit MCP** - Compliance
```python
@mcp.tool()
def query_audit_log(...) -> str:
    """Query the immutable audit log"""
    # Provides audit trail for compliance
```

### Client (`src/client.py`)

The client uses LangGraph to create an intelligent agent:

```python
# Agent decides which tools to call based on natural language
client = EnterpriseMCPClient(openrouter_api_key=api_key)

client.run_prompt(
    user_id="alice",
    token="admin-token",
    prompt="Hello! Please restart the web server."
)
```

The agent will:
1. Greet the user
2. Call `authorize()` to check permissions
3. If allowed, call `execute_action()` to restart
4. Return a natural language response

## 👥 Demo Users & Permissions

| User    | Role     | Token           | Permissions                           |
|---------|----------|-----------------|---------------------------------------|
| alice   | admin    | admin-token     | All actions (restart, stop, view)     |
| bob     | operator | operator-token  | restart_service, view_logs, view_status |
| charlie | viewer   | viewer-token    | view_logs, view_status only           |

## 🎬 Workshop Scenarios

### Scenario 1: Successful Authorization
```python
client.run_prompt(
    user_id="alice",
    token="admin-token",
    prompt="Restart the web server"
)
```
**Result**: ✅ Authorized → ✅ Service restarted

### Scenario 2: Permission Denied
```python
client.run_prompt(
    user_id="charlie",
    token="viewer-token",
    prompt="Stop the database"
)
```
**Result**: ❌ Denied → User informed they lack permission

### Scenario 3: Mixed Request
```python
client.run_prompt(
    user_id="bob",
    token="operator-token",
    prompt="Hello! What's 2+2? Also show me the system status."
)
```
**Result**: Agent responds to all parts: greeting + math + system action

## 🔧 Customization

### Add a New Action

1. **Update RBAC policies** in `server.py`:
```python
policies_df = pd.DataFrame([
    {
        "role": "admin",
        "allowed_actions": ["restart_service", "stop_service", "view_logs", "view_status", "deploy_app"],
        ...
    }
])
```

2. **Implement the action** in `execute_action()`:
```python
elif action == "deploy_app":
    # Your deployment logic
    return {"success": True, "reason": "app deployed"}
```

### Add a New User

```python
users_df = pd.DataFrame([
    {
        "user_id": "dave",
        "role": "developer",
        "token": "dev-token",
        "email": "dave@company.com",
        ...
    }
])
```

## 🧪 Testing

Run individual components:

```bash
# Test the server tools directly
uv run python -c "from src.server import mcp; print(mcp.list_tools())"

# Test authorization logic
uv run python -c "
from src.server import users_df, policies_df
print('Users:', users_df.index.tolist())
print('Roles:', policies_df.index.tolist())
"
```

## 📊 Monitoring & Debugging

### View Audit Log

The audit log tracks all actions:
```python
# In server.py, the audit_df DataFrame stores:
# - timestamp: When the action occurred
# - trace_id: Unique ID linking related actions
# - user_id: Who performed the action
# - action: What was attempted
# - result: success | denied | error
# - reason: Explanation
# - mcp_source: Which MCP processed it (identity/operations)
```

### Enable Verbose Mode

```python
client.run_prompt(
    user_id="alice",
    token="admin-token",
    prompt="Restart server",
    verbose=True  # Shows all agent steps
)
```

## 🐛 Troubleshooting

### "Import fastmcp could not be resolved"
```bash
uv sync  # Reinstall dependencies
```

### "OPENROUTER_API_KEY not set"
```bash
export OPENROUTER_API_KEY='your-key-here'
```

### "Connection refused" when running client
Make sure the server is running first in a separate terminal.

### Agent not calling tools correctly
Check the system prompt in `client.py` - it guides the agent's behavior.

## 🔗 Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://modelcontextprotocol.io)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [OpenRouter API](https://openrouter.ai/docs)

## 📝 License

This project is licensed under the MIT License.

## 🙏 Credits

Built for MCP workshops to demonstrate:
- Model Context Protocol patterns
- FastMCP framework
- LangGraph agent development
- Enterprise security patterns (RBAC, audit logging)

---

**Ready for your workshop?** 🚀

Start with `uv run python src/client.py` and watch the agent in action!