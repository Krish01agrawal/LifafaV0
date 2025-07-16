#!/usr/bin/env python3
"""
List All Users
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.database_service import DatabaseService

async def list_users():
    """List all users in the database."""
    try:
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        users = await db.users.find({}).to_list(length=100)
        
        print("=" * 60)
        print("👥 ALL USERS IN DATABASE")
        print("=" * 60)
        
        if not users:
            print("❌ No users found in database")
            return
        
        for i, user in enumerate(users, 1):
            print(f"\n{i}. User ID: {user['_id']}")
            print(f"   Email: {user.get('email', 'N/A')}")
            print(f"   Name: {user.get('name', 'N/A')}")
            print(f"   Gmail Sync Status: {user.get('gmail_sync_status', 'N/A')}")
            print(f"   Email Count: {user.get('email_count', 0)}")
            print(f"   Created: {user.get('created_at', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("✅ USER LISTING COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")
    finally:
        await DatabaseService.close()

if __name__ == "__main__":
    asyncio.run(list_users()) 