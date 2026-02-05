#!/bin/bash
# Complete setup script for workshop attendees

echo "🚀 MCP Workshop Demo - Complete Setup"
echo "======================================================================"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed."
    echo ""
    echo "Install uv with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    exit 1
fi

echo "✅ uv is installed"

# Install Python 3.12
echo ""
echo "📦 Installing Python 3.12..."
uv python install 3.12

# Create .python-version
echo "3.12" > .python-version
echo "✅ Set Python version to 3.12"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
uv sync

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Run tests
echo ""
echo "🧪 Running pre-flight checks..."
uv run python test_setup.py

echo ""
echo "======================================================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Get an API key from: https://openrouter.ai/keys"
echo "  2. Set it: export OPENROUTER_API_KEY='your-key'"
echo "  3. Run demo: ./run_client.sh"
echo "======================================================================"
