# 🚀 MCP Orchestrator - Enterprise Demo

A production-ready demonstration of **Model Context Protocol (MCP)** implementation for secure, governed AI-driven operations. This project showcases how to separate AI "talking" from AI "acting" using microservice governance patterns.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Workshop Guide](#workshop-guide)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This project demonstrates an **AI Orchestrator** that can handle natural language prompts while enforcing enterprise-grade security governance. The system uses LangChain agents with OpenRouter LLMs to decompose user requests into actionable tasks, then routes them through a series of MCP (Microservice Control Plane) services for authorization, risk evaluation, approval, and execution.

### Key Principle

> **"The AI may speak freely. The AI may NOT act freely."**

- ✅ **Conversational responses** - No restrictions
- 🔒 **System actions** - Strictly governed through MCP chain

## 🏗️ Architecture

The system consists of:

1. **Orchestrator** - LangChain agent with OpenRouter GPT-4o-mini
2. **7 MCP Services** - Each handling specific governance concerns
3. **Isolated Databases** - Domain-separated data stores
4. **Interactive Frontend** - Web-based testing and debugging console

### MCP Services

| Service | Port | Purpose |
|---------|------|---------|
| **Identity MCP** | 8001 | User authorization and policy enforcement |
| **Operations MCP** | 8002 | Action execution (restart, deploy, etc.) |
| **Risk & Approval MCP** | 8003 | Risk scoring and approval workflows |
| **Observability MCP** | 8004 | System metrics and log queries |
| **Secrets & Security MCP** | 8005 | Sensitive path access control |
| **Audit Reporting MCP** | 8006 | Immutable audit trail logging |
| **Orchestrator** | 8000 | Main entry point and AI agent |

### Security Governance Flow

```
User Prompt → Orchestrator → LLM Analysis
                ↓
         [Conversation?] → Direct Response
                ↓
         [System Action?]
                ↓
    1. Identity MCP (Authorize)
                ↓
    2. Risk MCP (Evaluate Risk)
                ↓
    3. Approval MCP (if high risk)
                ↓
    4. Operations MCP (Execute)
                ↓
    5. Audit MCP (Log Everything)
                ↓
         Natural Language Response
```

## ✨ Features

### Core Capabilities

- 🤖 **Multi-Step Prompt Handling** - Decomposes complex requests into subtasks
- 🔐 **Role-Based Access Control** - Admin, Operator, Viewer roles
- ⚠️ **Risk-Based Approval** - Automatic approval for low-risk, human approval for high-risk
- 📊 **Complete Audit Trail** - Immutable logging of all actions
- 💬 **Natural Language Interface** - Friendly, conversational responses
- 🔄 **Mixed Prompts** - Handles "Hello! And restart the service" style requests

### Workshop Features

- 🖥️ **Interactive Web Console** - Test prompts with real-time feedback
- 📋 **Architecture Diagrams** - 4 interactive Mermaid diagrams
- 🎯 **Quick Test Scenarios** - Pre-configured test cases
- 🔍 **Execution Flow Visualization** - See tool calls step-by-step
- 📝 **JSON Response Viewer** - Formatted, readable output

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- OpenRouter API Key ([Get one here](https://openrouter.ai/))
- 8GB RAM minimum
- Ports 8000-8006 available

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/cheroualiyakoub/mcp-playground.git
cd mcp-playground/mcp-enterprise-demo
```

2. **Set up environment variables**

```bash
# Create .env file
cat > .env << EOF
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
EOF
```

3. **Start all services**

```bash
docker compose up -d --build
```

4. **Verify services are running**

```bash
docker compose ps
```

All 7 containers should show "Up" status.

5. **Open the frontend**

```bash
# macOS
open frontend/index.html

# Linux
xdg-open frontend/index.html

# Windows
start frontend/index.html
```

## 📖 Usage

### Testing with the Web Console

1. **Open** `frontend/index.html` in your browser
2. **Select a user** (alice/admin, bob/operator, charlie/viewer)
3. **Enter a prompt** or click a quick action button
4. **Click "Send Request"** and watch the execution flow

### Example Prompts

| Prompt | Expected Behavior |
|--------|-------------------|
| `"Hello, how are you?"` | Direct conversational response |
| `"What is 5 + 5?"` | Direct answer (10) |
| `"Restart the service"` | Authorization → Risk → Approval → Execute/Deny |
| `"Hello! And restart the service"` | Mixed: Greeting + Action flow |
| `"Check system metrics"` | Query observability MCP |

### Testing with curl

```bash
# Simple conversational request
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "token": "admin-token",
    "prompt": "Hello! What is 1 + 1?"
  }'

# System action request
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "token": "admin-token",
    "prompt": "Restart the service"
  }'
```

### Understanding Responses

```json
{
  "trace_id": "uuid-here",
  "summary": "Human-readable response from the AI",
  "logs": [
    {
      "tool": "authorize",
      "user": {"user_id": "alice", "role": "admin"},
      "action": "restart_service",
      "result": {"allowed": true}
    },
    {
      "tool": "evaluate_risk",
      "user": {"user_id": "alice", "role": "admin"},
      "action": "restart_service",
      "result": {"risk_score": 23, "requires_approval": false}
    }
  ]
}
```

## 🎓 Workshop Guide

### Learning Path

1. **Start with Architecture** (`frontend/architecture.html`)
   - Review system overview diagram
   - Understand the governance flow
   - Study decision points

2. **Test Conversational Prompts**
   - "Hello!"
   - "What is 2 + 2?"
   - Observe: No tool calls, direct responses

3. **Test System Actions**
   - "Restart the service"
   - Observe: Authorization → Risk → Approval → Execute flow
   - Watch the logs panel

4. **Test Mixed Prompts**
   - "Hello! And restart the service"
   - Observe: Greeting + Action combined

5. **Experiment with Roles**
   - Switch between alice (admin), bob (operator), charlie (viewer)
   - Try the same action with different users
   - Observe authorization failures

### Workshop Scenarios

#### Scenario 1: Low-Risk Action (Auto-Approved)
```
User: alice (admin)
Prompt: "restart the service"
Expected: Risk score < 50 → Execute directly
```

#### Scenario 2: High-Risk Action (Needs Approval)
```
User: alice (admin)
Prompt: "restart the service"
Expected: Risk score ≥ 50 → Denied (needs human approver)
Note: Risk scores are randomized for demo purposes
```

#### Scenario 3: Unauthorized Action
```
User: charlie (viewer)
Prompt: "restart the service"
Expected: Authorization denied at Identity MCP
```

#### Scenario 4: Pure Conversation
```
User: any
Prompt: "Tell me a joke"
Expected: Direct response, no tool calls
```

## 📁 Project Structure

```
mcp-enterprise-demo/
├── orchestrator/              # Main orchestrator service
│   ├── agent.py              # LangChain agent builder
│   ├── tools.py              # MCP tool wrappers
│   ├── prompt.py             # Agent system prompt
│   ├── server.py             # FastAPI server + CORS
│   └── requirements.txt      # Python dependencies
│
├── mcps/                      # MCP microservices
│   ├── identity_policy_mcp/  # Authorization (port 8001)
│   ├── operations_mcp/       # Execution (port 8002)
│   ├── risk_approval_mcp/    # Risk & Approval (port 8003)
│   ├── observability_mcp/    # Metrics & Logs (port 8004)
│   ├── secrets_security_mcp/ # Secrets (port 8005)
│   └── audit_reporting_mcp/  # Audit Trail (port 8006)
│
├── frontend/                  # Web interface
│   ├── index.html            # Interactive console
│   └── architecture.html     # Architecture diagrams
│
├── shared/                    # Shared utilities
│   ├── schemas/              # Common data models
│   ├── auth.py               # Authentication helpers
│   └── errors.py             # Error handlers
│
├── data/                      # SQLite databases (created at runtime)
│   ├── operational.db        # User roles & policies
│   ├── observability.db      # Logs & metrics
│   ├── risk.db               # Risk scores
│   ├── secrets.db            # Vault paths
│   └── audit.db              # Audit trail
│
├── docker-compose.yml         # Service orchestration
├── .env                       # Environment variables (create this)
└── README.md                  # This file
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | *(required)* | Your OpenRouter API key |
| `OPENROUTER_MODEL` | `openai/gpt-4o-mini` | LLM model to use |
| `IDENTITY_MCP_URL` | `http://identity:8001` | Identity service URL |
| `OPERATIONS_MCP_URL` | `http://operations:8002` | Operations service URL |
| `RISK_MCP_URL` | `http://risk:8003` | Risk service URL |
| `OBSERVABILITY_MCP_URL` | `http://observability:8004` | Observability service URL |
| `SECRETS_MCP_URL` | `http://secrets:8005` | Secrets service URL |
| `AUDIT_MCP_URL` | `http://audit:8006` | Audit service URL |

### User Roles & Tokens

| User | Role | Token | Permissions |
|------|------|-------|-------------|
| alice | admin | admin-token | Full access |
| bob | operator | token-ops | Limited access |
| charlie | viewer | token-view | Read-only |

### Risk Scoring

- **Score < 50** - Low risk, auto-approved
- **Score ≥ 50** - High risk, requires human approval
- Scores are calculated by Risk MCP based on action type and user role

## 📚 API Reference

### POST /run

Execute a prompt through the orchestrator.

**Request:**
```json
{
  "user_id": "alice",
  "token": "admin-token",
  "prompt": "Your natural language prompt here"
}
```

**Response:**
```json
{
  "trace_id": "uuid",
  "summary": "Natural language response",
  "logs": [
    {
      "tool": "tool_name",
      "user": {"user_id": "alice", "role": "admin"},
      "action": "action_name",
      "result": { /* tool result */ }
    }
  ]
}
```

### MCP Endpoints

Each MCP exposes specific endpoints:

- **Identity MCP**: `POST /authorize`
- **Operations MCP**: `POST /execute_action`
- **Risk MCP**: `POST /evaluate`
- **Approval MCP**: `POST /approve`
- **Observability MCP**: `GET /query`
- **Secrets MCP**: `POST /check`
- **Audit MCP**: `POST /log`

## 🛠️ Development

### Running Individual Services

```bash
# Start only the orchestrator
docker compose up orchestrator

# Start a specific MCP
docker compose up identity

# View logs
docker compose logs -f orchestrator
```

### Rebuilding After Changes

```bash
# Rebuild all services
docker compose up -d --build

# Rebuild specific service
docker compose up -d --build orchestrator
```

### Testing Locally Without Docker

```bash
# Install dependencies
cd orchestrator
pip install -r requirements.txt

# Set environment variables
export OPENROUTER_API_KEY=your_key
export IDENTITY_MCP_URL=http://localhost:8001
# ... other URLs ...

# Run the orchestrator
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Adding New MCPs

1. Create new directory in `mcps/`
2. Add `server.py` with FastAPI app
3. Create `requirements.txt`
4. Add service to `docker-compose.yml`
5. Create tool wrapper in `orchestrator/tools.py`
6. Register tool in `get_langchain_tools()`

## 🐛 Troubleshooting

### Common Issues

**Issue: "Could not connect to orchestrator"**
```bash
# Check if services are running
docker compose ps

# Check orchestrator logs
docker compose logs orchestrator

# Restart services
docker compose restart
```

**Issue: "LLM parsing errors"**
- This is expected occasionally
- The agent logic is working correctly
- The final response is what matters

**Issue: "404 error on MCP endpoint"**
```bash
# Check MCP logs
docker compose logs identity  # or other MCP name

# Verify port mappings
docker compose ps
```

**Issue: "Risk score always requires approval"**
- Risk scores are randomized (0-100)
- This is by design for demo purposes
- High scores (≥50) require approval

### Resetting the System

```bash
# Stop all services
docker compose down

# Remove volumes and data
docker compose down -v

# Remove data directory
rm -rf data/

# Start fresh
docker compose up -d --build
```

## 🤝 Contributing

This is a workshop demo project. Feel free to:

- Add more MCP services
- Implement real approval workflows
- Add more test scenarios
- Improve the frontend
- Create additional diagrams

## 📄 License

This project is for educational and workshop purposes.

## 🙏 Acknowledgments

- Built with [LangChain](https://www.langchain.com/)
- LLM powered by [OpenRouter](https://openrouter.ai/)
- Diagrams created with [Mermaid](https://mermaid.js.org/)
- Model Context Protocol (MCP) pattern

## 📧 Contact

For workshop questions or support:
- GitHub: [@cheroualiyakoub](https://github.com/cheroualiyakoub)
- Repository: [mcp-playground](https://github.com/cheroualiyakoub/mcp-playground)

---

**Happy Testing! 🚀**

*Last Updated: January 2026*

