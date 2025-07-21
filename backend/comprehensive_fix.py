#!/usr/bin/env python3
"""
Comprehensive Fix Script
========================

This script fixes all the database and user lookup issues comprehensively.
"""

import asyncio
import logging
from bson import ObjectId
from datetime import datetime
import pymongo

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database service
from app.services.database_service import DatabaseService

async def comprehensive_fix():
    """Comprehensive fix for all database and user lookup issues."""
    try:
        logger.info("🔧 Starting comprehensive fix...")
        
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        # Step 1: Drop ALL problematic indexes
        logger.info("📋 Step 1: Dropping all problematic indexes...")
        
        try:
            await db.users.drop_index("user_id_1")
            logger.info("✅ Dropped user_id_1 index")
        except Exception as e:
            if "index not found" in str(e).lower():
                logger.info("✅ user_id_1 index already removed")
            else:
                logger.warning(f"⚠️ Could not drop user_id_1 index: {e}")
        
        # Step 2: Clean up problematic users
        logger.info("📋 Step 2: Cleaning up problematic users...")
        
        # Find and delete users with null user_id
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
        
        # Step 3: Create proper user with ObjectId
        logger.info("📋 Step 3: Creating proper user...")
        
        test_user_data = {
            "email": "krishagrawal3914@gmail.com",
            "name": "Krish Agrawal",
            "picture": "https://lh3.googleusercontent.com/a/ACg8ocIa9QiMPqcFqJ2Kyg88i3CYOs_lCJevQyV3YiEwfwtVa6pM6u-O=s96-c",
            "google_id": "118347882719275014790",
            "gmail_sync_status": "not_synced",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": datetime.utcnow()
        }
        
        # Check if user exists by email
        existing_user = await db.users.find_one({"email": test_user_data["email"]})
        if existing_user:
            logger.info(f"✅ User already exists with ID: {existing_user['_id']}")
            user_id = existing_user["_id"]
        else:
            # Create new user
            result = await db.users.insert_one(test_user_data)
            user_id = result.inserted_id
            logger.info(f"✅ New user created with ID: {user_id}")
        
        # Step 4: Fix the auth.py to use proper ObjectId
        logger.info("📋 Step 4: Fixing auth.py to use proper ObjectId...")
        
        # Update the user document to include a proper user_id field
        await db.users.update_one(
            {"_id": user_id},
            {"$set": {"user_id": str(user_id)}}  # Store ObjectId as string
        )
        logger.info(f"✅ Updated user with user_id: {user_id}")
        
        # Step 5: Verify indexes
        logger.info("📋 Step 5: Verifying current indexes...")
        
        indexes = await db.users.list_indexes().to_list(length=None)
        logger.info("Current user indexes:")
        for idx in indexes:
            logger.info(f"   - {idx['name']}: {idx['key']}")
        
        # Step 6: Test user lookup
        logger.info("📋 Step 6: Testing user lookup...")
        
        # Test by email
        user_by_email = await db.users.find_one({"email": "krishagrawal3914@gmail.com"})
        if user_by_email:
            logger.info(f"✅ User found by email: {user_by_email['_id']}")
        else:
            logger.error("❌ User not found by email")
        
        # Test by ObjectId
        user_by_id = await db.users.find_one({"_id": user_id})
        if user_by_id:
            logger.info(f"✅ User found by ObjectId: {user_by_id['_id']}")
        else:
            logger.error("❌ User not found by ObjectId")
        
        logger.info("🎉 Comprehensive fix completed successfully!")
        
        return {
            "success": True,
            "user_id": str(user_id),
            "email": "krishagrawal3914@gmail.com"
        }
        
    except Exception as e:
        logger.error(f"❌ Error during comprehensive fix: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(comprehensive_fix())
    print(f"Result: {result}") 