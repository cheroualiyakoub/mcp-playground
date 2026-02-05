#!/usr/bin/env python3
"""
Simple example showing how to use the Enterprise MCP Client
Run this instead of client.py for a simpler, single-scenario demo
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Try to load .env from src directory or project root
    env_path = Path(__file__).parent.parent / 'src' / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
except ImportError:
    pass

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from client import EnterpriseMCPClient


def main():
    """Run a simple example"""
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENROUTER_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export OPENROUTER_API_KEY='your-key-here'")
        print("\nGet a free key at: https://openrouter.ai/keys")
        sys.exit(1)
    
    print("🚀 Enterprise MCP Simple Example")
    print("="*80)
    
    # Initialize client
    client = EnterpriseMCPClient(openrouter_api_key=api_key)
    
    print("\n📝 Example: Admin user restarts web server")
    print("="*80)
    
    # Run a simple scenario
    result = client.run_prompt(
        user_id="alice",
        token="admin-token",
        prompt="Hello! Please restart the web server and show me its status.",
        verbose=True
    )
    
    print(f"\n✅ Done! Trace ID: {result['trace_id']}")
    print("="*80)


if __name__ == "__main__":
    main()
