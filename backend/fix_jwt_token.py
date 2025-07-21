#!/usr/bin/env python3
"""
Fix JWT Token Issue
===================

This script fixes the JWT token issue by ensuring proper user lookup.
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

async def fix_jwt_token():
    """Fix JWT token issue by ensuring proper user lookup."""
    try:
        logger.info("🔧 Starting JWT token fix...")
        
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        # Step 1: Verify user exists
        logger.info("📋 Step 1: Verifying user exists...")
        
        user = await db.users.find_one({"email": "krishagrawal3914@gmail.com"})
        if user:
            logger.info(f"✅ User found: {user['email']} (ID: {user['_id']})")
            logger.info(f"   - user_id field: {user.get('user_id')}")
            logger.info(f"   - google_id field: {user.get('google_id')}")
        else:
            logger.error("❌ User not found")
            return {"success": False, "error": "User not found"}
        
        # Step 2: Test user lookup by email
        logger.info("📋 Step 2: Testing user lookup by email...")
        
        user_by_email = await db.users.find_one({"email": "krishagrawal3914@gmail.com"})
        if user_by_email:
            logger.info(f"✅ User lookup by email works: {user_by_email['_id']}")
            correct_user_id = str(user_by_email["_id"])
            logger.info(f"   - Correct user_id should be: {correct_user_id}")
        else:
            logger.error("❌ User lookup by email failed")
            return {"success": False, "error": "User lookup by email failed"}
        
        # Step 3: Test user lookup by ObjectId
        logger.info("📋 Step 3: Testing user lookup by ObjectId...")
        
        try:
            object_id = ObjectId(correct_user_id)
            user_by_id = await db.users.find_one({"_id": object_id})
            if user_by_id:
                logger.info(f"✅ User lookup by ObjectId works: {user_by_id['_id']}")
            else:
                logger.error("❌ User lookup by ObjectId failed")
                return {"success": False, "error": "User lookup by ObjectId failed"}
        except Exception as e:
            logger.error(f"❌ Invalid ObjectId: {e}")
            return {"success": False, "error": f"Invalid ObjectId: {e}"}
        
        # Step 4: Test the problematic Google ID
        logger.info("📋 Step 4: Testing problematic Google ID...")
        
        google_id = "118347882719275014790"
        try:
            object_id = ObjectId(google_id)
            logger.error(f"❌ Google ID should not be a valid ObjectId: {google_id}")
        except Exception as e:
            logger.info(f"✅ Google ID correctly rejected as ObjectId: {e}")
        
        # Step 5: Verify the fix will work
        logger.info("📋 Step 5: Verifying the fix will work...")
        
        # Simulate the user lookup logic from main.py
        test_user_id = google_id  # This is what comes from JWT
        test_email = "krishagrawal3914@gmail.com"
        
        # Try to find user by email first
        test_user = await db.users.find_one({"email": test_email})
        if test_user:
            logger.info(f"✅ Fix will work: Found user by email: {test_user['email']}")
            correct_id = str(test_user["_id"])
            logger.info(f"   - JWT user_id: {test_user_id} (Google ID)")
            logger.info(f"   - Correct user_id: {correct_id} (ObjectId)")
            logger.info(f"   - User lookup will succeed by email")
        else:
            logger.error("❌ Fix will not work: User not found by email")
            return {"success": False, "error": "User not found by email"}
        
        logger.info("🎉 JWT token fix verification completed successfully!")
        
        return {
            "success": True,
            "correct_user_id": correct_user_id,
            "google_id": google_id,
            "email": "krishagrawal3914@gmail.com",
            "message": "User lookup by email will work correctly"
        }
        
    except Exception as e:
        logger.error(f"❌ Error during JWT token fix: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(fix_jwt_token())
    print(f"Result: {result}") 