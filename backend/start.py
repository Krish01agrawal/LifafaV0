#!/usr/bin/env python3
"""
Pluto Money - Startup Script
Simple script to start the FastAPI application with proper configuration.
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Start the Pluto Money application."""
    
    # Add the current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Check if .env file exists
    env_file = current_dir / ".env"
    if not env_file.exists():
        print("❌ Error: .env file not found!")
        print("Please copy env.example to .env and configure your settings.")
        sys.exit(1)
    
    # Check required environment variables
    required_vars = [
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET", 
        "OPENAI_API_KEY",
        "SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease check your .env file and ensure all required variables are set.")
        sys.exit(1)
    
    print("🚀 Starting Pluto Money - GenAI Email Intelligence Platform")
    print("=" * 60)
    
    # Start the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 