#!/bin/bash
# Quick start script for MCP client demo

echo "🚀 Starting Enterprise MCP Workshop Client Demo..."
echo "============================================================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run 'uv sync' first."
    exit 1
fi

# Check if .env file exists (will be loaded automatically by client.py)
if [ ! -f "src/.env" ] && [ ! -f ".env" ]; then
    # Only check environment variable if no .env file exists
    if [ -z "$OPENROUTER_API_KEY" ]; then
        echo "⚠️  No .env file found and OPENROUTER_API_KEY not set."
        echo ""
        echo "Option 1: Create src/.env file with:"
        echo "  OPENROUTER_API_KEY='your-key-here'"
        echo ""
        echo "Option 2: Export environment variable:"
        echo "  export OPENROUTER_API_KEY='your-key-here'"
        echo ""
        echo "Get a free key at: https://openrouter.ai/keys"
        exit 1
    fi
else
    echo "✅ Found .env file - API key will be loaded automatically"
fi

# Activate virtual environment and run client
source .venv/bin/activate
python src/client.py
