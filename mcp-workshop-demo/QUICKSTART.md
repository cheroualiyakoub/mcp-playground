# 🚀 Quick Start Guide

Get the MCP Workshop Demo running in 5 minutes!

## 1️⃣ Install Dependencies

```bash
# Navigate to project directory
cd mcp-workshop-demo

# Install everything with uv (auto-creates venv)
uv sync
```

**Expected output:**
```
Resolved 121 packages...
Installed 109 packages...
✓ Done!
```

## 2️⃣ Get Your API Key

1. Go to [openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign up (free)
3. Create an API key
4. Copy it

## 3️⃣ Set Environment Variable

```bash
# macOS/Linux
export OPENROUTER_API_KEY='your-key-here'

# Or add to ~/.zshrc for persistence
echo 'export OPENROUTER_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## 4️⃣ Run the Demo

### Option A: Use the Helper Scripts

```bash
# Terminal 1: Start server
./run_server.sh

# Terminal 2: Run client demo (in a new terminal)
./run_client.sh
```

### Option B: Run Directly with uv

```bash
# Terminal 1: Start server
uv run python src/server.py

# Terminal 2: Run client demo
uv run python src/client.py
```

### Option C: Run Simple Example

```bash
# Single scenario demo
uv run python examples/simple_example.py
```

## ✅ What to Expect

### Server Output:
```
🚀 Starting Enterprise MCP Workshop Server...
============================================================
📊 Loaded 3 users
📋 Loaded 3 roles
⚙️  Monitoring 3 services
============================================================
```

### Client Output:
```
🧪 SCENARIO 1: Admin restarts service
================================================================================
🚀 USER: alice (admin)
📝 PROMPT: Hello! Please restart the web server.
🔗 TRACE ID: a7b3c2d1
================================================================================

🤖 AGENT THINKING...
  🔧 Step 1: Calling authorize({'action': 'restart_service'})
  🔧 Step 2: Calling execute_action({'action': 'restart_service'})

✅ FINAL ANSWER:
================================================================================
Hello! I've successfully restarted the web server for you. The service is now 
running and ready to handle requests.
================================================================================
```

## 🎯 Next Steps

1. **Modify scenarios** in `src/client.py`
2. **Add new actions** in `src/server.py`
3. **Add new users/roles** in server's database initialization
4. **Try different prompts** - the agent handles mixed requests like:
   - "Hello! What's 2+2? Also restart the server."
   - "Show me the system status and tell me about Paris."

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `Import "fastmcp" could not be resolved` | Run `uv sync` |
| `OPENROUTER_API_KEY not set` | Export the environment variable |
| Server doesn't start | Check Python version: `python --version` (need 3.10+) |
| Client shows errors | Make sure server is running first |

## 📚 Learn More

- See [README.md](README.md) for full documentation
- Check `src/server.py` for MCP implementation details
- Read `src/client.py` for LangGraph agent setup

---

**Need help?** Check the main README or open an issue!
