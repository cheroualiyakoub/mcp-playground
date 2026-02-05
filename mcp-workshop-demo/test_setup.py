#!/usr/bin/env python3
"""
Test script to verify the MCP server is working correctly
Run this before the workshop to ensure everything is set up
"""

import sys
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Try to load .env from src directory or project root
    env_path = Path(__file__).parent / 'src' / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
except ImportError:
    pass  # dotenv not required for basic tests

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import pandas as pd
        print("  ✅ pandas")
    except ImportError as e:
        print(f"  ❌ pandas: {e}")
        return False
    
    try:
        from fastmcp import FastMCP
        print("  ✅ fastmcp")
    except ImportError as e:
        print(f"  ❌ fastmcp: {e}")
        return False
    
    try:
        from langchain_openai import ChatOpenAI
        print("  ✅ langchain-openai")
    except ImportError as e:
        print(f"  ❌ langchain-openai: {e}")
        return False
    
    try:
        from langgraph.prebuilt import create_react_agent
        print("  ✅ langgraph")
    except ImportError as e:
        print(f"  ❌ langgraph: {e}")
        return False
    
    return True


def test_server():
    """Test that the server module loads correctly"""
    print("\n🧪 Testing server module...")
    
    try:
        from src.server import mcp, users_df, policies_df, services_state
        print("  ✅ Server module imported")
        print(f"  ✅ Loaded {len(users_df)} users")
        print(f"  ✅ Loaded {len(policies_df)} roles")
        print(f"  ✅ Monitoring {len(services_state)} services")
        return True
    except Exception as e:
        print(f"  ❌ Server module failed: {e}")
        return False


def test_api_key():
    """Test that API key is set"""
    print("\n🧪 Testing API configuration...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        print(f"  ✅ OPENROUTER_API_KEY is set (length: {len(api_key)})")
        return True
    else:
        print("  ⚠️  OPENROUTER_API_KEY not set (required for client)")
        print("     Set it with: export OPENROUTER_API_KEY='your-key'")
        print("     Get key at: https://openrouter.ai/keys")
        return False


def test_authorization():
    """Test authorization logic"""
    print("\n🧪 Testing authorization logic...")
    
    try:
        from src.server import users_df, policies_df
        
        # Test 1: Admin can restart
        admin_role = users_df.loc["alice", "role"]
        admin_actions = policies_df.loc[admin_role, "allowed_actions"]
        
        if "restart_service" in admin_actions:
            print("  ✅ Admin can restart service")
        else:
            print("  ❌ Admin should be able to restart service")
            return False
        
        # Test 2: Viewer cannot restart
        viewer_role = users_df.loc["charlie", "role"]
        viewer_actions = policies_df.loc[viewer_role, "allowed_actions"]
        
        if "restart_service" not in viewer_actions:
            print("  ✅ Viewer cannot restart service")
        else:
            print("  ❌ Viewer should not be able to restart service")
            return False
        
        # Test 3: All users can view logs
        for user_id in users_df.index:
            role = users_df.loc[user_id, "role"]
            actions = policies_df.loc[role, "allowed_actions"]
            if "view_logs" not in actions:
                print(f"  ❌ {user_id} should be able to view logs")
                return False
        
        print("  ✅ All users can view logs")
        
        return True
    except Exception as e:
        print(f"  ❌ Authorization test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("🚀 MCP Workshop Demo - Pre-flight Checks")
    print("=" * 80)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Server Module", test_server()))
    results.append(("API Configuration", test_api_key()))
    results.append(("Authorization Logic", test_authorization()))
    
    print("\n" + "=" * 80)
    print("📊 Test Results")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name:.<50} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 80)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready for the workshop!")
        print("\nNext steps:")
        print("  1. Start the server: ./run_server.sh")
        print("  2. Run the demo:    ./run_client.sh")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Run: uv sync")
        print("  - Set: export OPENROUTER_API_KEY='your-key'")
        return 1


if __name__ == "__main__":
    sys.exit(main())
