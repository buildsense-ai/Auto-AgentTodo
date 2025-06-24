#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Startup script for AI Document Processing MCP Server
"""

import os
import sys

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'fastmcp',
        'openai', 
        'python-docx',
        'PyMuPDF',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment():
    """Check if environment is properly configured"""
    env_file = ".env"
    if not os.path.exists(env_file):
        print("⚠️ Warning: .env file not found")
        print("   Create a .env file with: OPENROUTER_API_KEY=your-api-key-here")
        print("   Or set TEST_MODE=true for testing")
    
    api_key = os.environ.get("OPENROUTER_API_KEY")
    test_mode = os.environ.get("TEST_MODE", "false").lower() == "true"
    
    if not api_key and not test_mode:
        print("❌ Missing OPENROUTER_API_KEY and TEST_MODE is not enabled")
        print("   Either set OPENROUTER_API_KEY or set TEST_MODE=true")
        return False
    
    return True

if __name__ == "__main__":
    print("🤖 AI Document Processing MCP Server")
    print("=" * 50)
    
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies found")
    
    print("\n🔍 Checking environment...")
    if not check_environment():
        sys.exit(1)
    print("✅ Environment configured")
    
    print("\n🚀 Starting MCP server...")
    print("=" * 50)
    
    # Import and run the MCP server
    from mcp_server import mcp
    mcp.run() 