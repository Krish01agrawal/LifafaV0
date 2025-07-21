#!/usr/bin/env python3
"""
Complete Database Reset
======================

This script completely resets the database to remove all problematic indexes and data.
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

async def complete_database_reset():
    """Complete database reset to remove all problematic indexes and data."""
    try:
        logger.info("🔧 Starting complete database reset...")
        
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        # Step 1: Drop ALL indexes from users collection
        logger.info("📋 Step 1: Dropping ALL indexes from users collection...")
        
        try:
            # Drop all indexes except _id_
            await db.users.drop_indexes()
            logger.info("✅ Dropped all indexes from users collection")
        except Exception as e:
            logger.warning(f"⚠️ Could not drop all indexes: {e}")
        
        # Step 2: Drop the entire users collection and recreate it
        logger.info("📋 Step 2: Dropping and recreating users collection...")
        
        try:
            await db.users.drop()
            logger.info("✅ Dropped users collection")
        except Exception as e:
            logger.warning(f"⚠️ Could not drop users collection: {e}")
        
        # Step 3: Create only the necessary indexes
        logger.info("📋 Step 3: Creating only necessary indexes...")
        
        # Create only email and google_id indexes (no user_id index)
        await db.users.create_index([("email", 1)], unique=True)
        await db.users.create_index([("google_id", 1)])
        
        logger.info("✅ Created necessary indexes")
        
        # Step 4: Create proper user
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
        
        # Step 5: Add user_id field (as string)
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
        
        # Verify no user_id_1 index exists
        user_id_indexes = [idx for idx in indexes if "user_id" in idx.get("name", "")]
        if user_id_indexes:
            logger.error(f"❌ Found user_id indexes: {user_id_indexes}")
            return {"success": False, "error": "user_id indexes still exist"}
        else:
            logger.info("✅ No user_id indexes found")
        
        # Check user
        user = await db.users.find_one({"_id": user_id})
        if user:
            logger.info(f"✅ User verified: {user['email']} (ID: {user['_id']})")
            logger.info(f"   - user_id field: {user.get('user_id')}")
            logger.info(f"   - google_id field: {user.get('google_id')}")
        else:
            logger.error("❌ User not found after creation")
            return {"success": False, "error": "User not found after creation"}
        
        # Test lookups
        user_by_email = await db.users.find_one({"email": "krishagrawal3914@gmail.com"})
        if user_by_email:
            logger.info(f"✅ User lookup by email works: {user_by_email['_id']}")
        else:
            logger.error("❌ User lookup by email failed")
            return {"success": False, "error": "User lookup by email failed"}
        
        user_by_id = await db.users.find_one({"_id": user_id})
        if user_by_id:
            logger.info(f"✅ User lookup by ObjectId works: {user_by_id['_id']}")
        else:
            logger.error("❌ User lookup by ObjectId failed")
            return {"success": False, "error": "User lookup by ObjectId failed"}
        
        logger.info("🎉 Complete database reset completed successfully!")
        
        return {
            "success": True,
            "user_id": str(user_id),
            "email": "krishagrawal3914@gmail.com",
            "indexes": [idx["name"] for idx in indexes]
        }
        
    except Exception as e:
        logger.error(f"❌ Error during complete database reset: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(complete_database_reset())
    print(f"Result: {result}") 