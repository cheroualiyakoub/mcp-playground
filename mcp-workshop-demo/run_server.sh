#!/bin/bash
# Quick start script for MCP server

echo "🚀 Starting Enterprise MCP Workshop Server..."
echo "============================================================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run 'uv sync' first."
    exit 1
fi

# Activate virtual environment and run server
source .venv/bin/activate
python src/server.py
