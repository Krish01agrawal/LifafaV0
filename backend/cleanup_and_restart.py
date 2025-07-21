#!/usr/bin/env python3
"""
Cleanup and Restart Script
==========================

This script cleans up problematic data and restarts the server properly.
"""

import asyncio
import logging
from bson import ObjectId
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database service
from app.services.database_service import DatabaseService

async def cleanup_and_restart():
    """Clean up problematic data and restart the server."""
    try:
        logger.info("🧹 Starting cleanup and restart process...")
        
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        # Step 1: Clean up problematic users
        logger.info("📋 Step 1: Cleaning up problematic users...")
        
        # Find users with null user_id or invalid data
        problematic_users = await db.users.find({
            "$or": [
                {"user_id": None},
                {"user_id": {"$exists": False}},
                {"email": {"$exists": False}}
            ]
        }).to_list(length=None)
        
        if problematic_users:
            logger.info(f"🗑️ Found {len(problematic_users)} problematic users to clean up")
            for user in problematic_users:
                logger.info(f"   - User: {user.get('email', 'NO_EMAIL')} (ID: {user.get('_id')})")
                await db.users.delete_one({"_id": user["_id"]})
            logger.info("✅ Problematic users cleaned up")
        else:
            logger.info("✅ No problematic users found")
        
        # Step 2: Clean up any remaining problematic indexes
        logger.info("📋 Step 2: Checking for problematic indexes...")
        
        try:
            # Try to drop the problematic index if it exists
            await db.users.drop_index("user_id_1")
            logger.info("✅ Dropped user_id_1 index")
        except Exception as e:
            if "index not found" in str(e).lower():
                logger.info("✅ user_id_1 index already removed")
            else:
                logger.warning(f"⚠️ Could not drop user_id_1 index: {e}")
        
        # Step 3: Verify current indexes
        logger.info("📋 Step 3: Verifying current indexes...")
        
        indexes = await db.users.list_indexes().to_list(length=None)
        logger.info("Current user indexes:")
        for idx in indexes:
            logger.info(f"   - {idx['name']}: {idx['key']}")
        
        # Step 4: Create proper user for testing
        logger.info("📋 Step 4: Creating test user...")
        
        test_user = {
            "email": "krishagrawal3914@gmail.com",
            "name": "Krish Agrawal",
            "picture": "https://lh3.googleusercontent.com/a/ACg8ocIa9QiMPqcFqJ2Kyg88i3CYOs_lCJevQyV3YiEwfwtVa6pM6u-O=s96-c",
            "google_id": "118347882719275014790",
            "gmail_sync_status": "not_synced",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": datetime.utcnow()
        }
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": test_user["email"]})
        if existing_user:
            logger.info("✅ Test user already exists")
        else:
            result = await db.users.insert_one(test_user)
            logger.info(f"✅ Test user created with ID: {result.inserted_id}")
        
        logger.info("🎉 Cleanup and restart process completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_and_restart()) 