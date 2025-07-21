#!/usr/bin/env python3
"""
Fix Database Indexes
===================

This script fixes database index issues and cleans up problematic data.
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

async def fix_database_indexes():
    """Fix database indexes and clean up problematic data."""
    try:
        logger.info("🔧 Starting database index fixes...")
        
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        # Step 1: Drop problematic indexes
        logger.info("📋 Step 1: Dropping problematic indexes...")
        
        try:
            # Drop the problematic user_id index
            await db.users.drop_index("user_id_1")
            logger.info("✅ Dropped user_id_1 index")
        except Exception as e:
            logger.warning(f"⚠️ Could not drop user_id_1 index: {e}")
        
        try:
            # Drop any other problematic indexes
            await db.users.drop_index("user_id_1")
            logger.info("✅ Dropped duplicate user_id_1 index")
        except Exception as e:
            logger.warning(f"⚠️ Could not drop duplicate user_id_1 index: {e}")
        
        # Step 2: Clean up problematic user documents
        logger.info("📋 Step 2: Cleaning up problematic user documents...")
        
        # Find users with null user_id
        problematic_users = await db.users.find({"user_id": None}).to_list(length=None)
        logger.info(f"Found {len(problematic_users)} users with null user_id")
        
        for user in problematic_users:
            try:
                # Delete problematic user
                await db.users.delete_one({"_id": user["_id"]})
                logger.info(f"🗑️ Deleted user with null user_id: {user.get('email', 'unknown')}")
            except Exception as e:
                logger.error(f"❌ Error deleting user {user.get('_id')}: {e}")
        
        # Step 3: Recreate proper indexes
        logger.info("📋 Step 3: Recreating proper indexes...")
        
        # Users collection indexes
        await db.users.create_index([("email", 1)], unique=True)
        logger.info("✅ Created email index")
        
        await db.users.create_index([("google_id", 1)])
        logger.info("✅ Created google_id index")
        
        # Step 4: Verify indexes
        logger.info("📋 Step 4: Verifying indexes...")
        
        indexes = await db.users.list_indexes().to_list(length=None)
        logger.info("📊 Current user collection indexes:")
        for index in indexes:
            logger.info(f"   - {index['name']}: {index['key']}")
        
        # Step 5: Test user creation
        logger.info("📋 Step 5: Testing user creation...")
        
        test_user = {
            "email": "test@example.com",
            "name": "Test User",
            "google_id": "test_google_id",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        try:
            result = await db.users.insert_one(test_user)
            logger.info(f"✅ Test user created successfully: {result.inserted_id}")
            
            # Clean up test user
            await db.users.delete_one({"_id": result.inserted_id})
            logger.info("🗑️ Test user cleaned up")
            
        except Exception as e:
            logger.error(f"❌ Test user creation failed: {e}")
        
        logger.info("🎉 Database index fixes completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error fixing database indexes: {e}")
        raise

async def main():
    """Main function."""
    try:
        await fix_database_indexes()
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 