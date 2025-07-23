#!/usr/bin/env python3
"""
Load Environment Variables
=========================

Script to manually load .env file and test environment variables.
"""

import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(current_dir, '.env')
    
    print(f"🔍 Looking for .env file at: {env_file}")
    print(f"📋 File exists: {os.path.exists(env_file)}")
    
    if os.path.exists(env_file):
        # Load the .env file
        load_dotenv(env_file)
        print("✅ .env file loaded successfully")
        
        # Check environment variables
        mongo_uri = os.getenv('MONGO_URI')
        mongo_connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        
        print(f"📋 MONGO_URI: {mongo_uri}")
        print(f"📋 MONGODB_CONNECTION_STRING: {mongo_connection_string}")
        
        return True
    else:
        print("❌ .env file not found")
        return False

if __name__ == "__main__":
    load_environment() 