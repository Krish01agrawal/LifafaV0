#!/usr/bin/env python3
"""
Final Comprehensive Fix
=======================

This script fixes the remaining database and user creation issues.
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

async def final_fix():
    """Final comprehensive fix for all remaining issues."""
    try:
        logger.info("🔧 Starting final comprehensive fix...")
        
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        # Step 1: Force drop the problematic index using raw MongoDB command
        logger.info("📋 Step 1: Force dropping problematic index...")
        
        try:
            # Use raw MongoDB command to drop the index
            await db.command("dropIndexes", "users", index="user_id_1")
            logger.info("✅ Force dropped user_id_1 index")
        except Exception as e:
            if "index not found" in str(e).lower():
                logger.info("✅ user_id_1 index already removed")
            else:
                logger.warning(f"⚠️ Could not force drop user_id_1 index: {e}")
        
        # Step 2: Clean up ALL problematic users
        logger.info("📋 Step 2: Cleaning up ALL problematic users...")
        
        # Find and delete ALL users with any issues
        problematic_users = await db.users.find({
            "$or": [
                {"user_id": None},
                {"user_id": {"$exists": False}},
                {"email": {"$exists": False}},
                {"email": "krishagrawal3914@gmail.com"}  # Remove existing user
            ]
        }).to_list(length=None)
        
        if problematic_users:
            logger.info(f"🗑️ Found {len(problematic_users)} problematic users to clean up")
            for user in problematic_users:
                logger.info(f"   - User: {user.get('email', 'NO_EMAIL')} (ID: {user.get('_id')})")
                await db.users.delete_one({"_id": user["_id"]})
            logger.info("✅ All problematic users cleaned up")
        else:
            logger.info("✅ No problematic users found")
        
        # Step 3: Verify no user_id_1 index exists
        logger.info("📋 Step 3: Verifying no user_id_1 index exists...")
        
        indexes = await db.users.list_indexes().to_list(length=None)
        user_id_indexes = [idx for idx in indexes if "user_id" in idx.get("name", "")]
        
        if user_id_indexes:
            logger.warning(f"⚠️ Found user_id indexes: {user_id_indexes}")
            for idx in user_id_indexes:
                try:
                    await db.users.drop_index(idx["name"])
                    logger.info(f"✅ Dropped index: {idx['name']}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not drop index {idx['name']}: {e}")
        else:
            logger.info("✅ No user_id indexes found")
        
        # Step 4: Create proper user with correct structure
        logger.info("📋 Step 4: Creating proper user...")
        
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
        
        # Create new user
        result = await db.users.insert_one(test_user_data)
        user_id = result.inserted_id
        logger.info(f"✅ New user created with ID: {user_id}")
        
        # Step 5: Update user with user_id field (as string)
        logger.info("📋 Step 5: Adding user_id field...")
        
        await db.users.update_one(
            {"_id": user_id},
            {"$set": {"user_id": str(user_id)}}
        )
        logger.info(f"✅ Updated user with user_id: {user_id}")
        
        # Step 6: Verify final state
        logger.info("📋 Step 6: Verifying final state...")
        
        # Check indexes
        indexes = await db.users.list_indexes().to_list(length=None)
        logger.info("Final user indexes:")
        for idx in indexes:
            logger.info(f"   - {idx['name']}: {idx['key']}")
        
        # Check user
        user = await db.users.find_one({"_id": user_id})
        if user:
            logger.info(f"✅ User verified: {user['email']} (ID: {user['_id']})")
            logger.info(f"   - user_id field: {user.get('user_id')}")
            logger.info(f"   - google_id field: {user.get('google_id')}")
        else:
            logger.error("❌ User not found after creation")
        
        # Test lookups
        user_by_email = await db.users.find_one({"email": "krishagrawal3914@gmail.com"})
        if user_by_email:
            logger.info(f"✅ User lookup by email works: {user_by_email['_id']}")
        else:
            logger.error("❌ User lookup by email failed")
        
        user_by_id = await db.users.find_one({"_id": user_id})
        if user_by_id:
            logger.info(f"✅ User lookup by ObjectId works: {user_by_id['_id']}")
        else:
            logger.error("❌ User lookup by ObjectId failed")
        
        logger.info("🎉 Final comprehensive fix completed successfully!")
        
        return {
            "success": True,
            "user_id": str(user_id),
            "email": "krishagrawal3914@gmail.com",
            "indexes": [idx["name"] for idx in indexes]
        }
        
    except Exception as e:
        logger.error(f"❌ Error during final fix: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(final_fix())
    print(f"Result: {result}") 