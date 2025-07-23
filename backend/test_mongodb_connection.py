#!/usr/bin/env python3
"""
MongoDB Connection Test Script
=============================

Simple script to test MongoDB connection after SSL configuration fixes.
"""

import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        logger.info("🔍 Testing MongoDB Connection...")
        
        from app.db import db_manager
        
        # Test basic connection
        database = db_manager.get_database_for_user("test_user")
        if database is None:
            logger.error("❌ Failed to get database")
            return False
        
        logger.info("✅ Database connection successful")
        
        # Test collection access
        test_collection = database['test_collection']
        
        # Test insert
        test_doc = {
            "test": True,
            "timestamp": datetime.now(),
            "message": "Connection test successful"
        }
        
        result = await test_collection.insert_one(test_doc)
        logger.info(f"✅ Insert test successful: {result.inserted_id}")
        
        # Test find
        found_doc = await test_collection.find_one({"_id": result.inserted_id})
        if found_doc:
            logger.info("✅ Find test successful")
        else:
            logger.error("❌ Find test failed")
            return False
        
        # Test delete
        delete_result = await test_collection.delete_one({"_id": result.inserted_id})
        if delete_result.deleted_count == 1:
            logger.info("✅ Delete test successful")
        else:
            logger.error("❌ Delete test failed")
            return False
        
        logger.info("🎉 All MongoDB connection tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ MongoDB connection test failed: {e}")
        return False

async def test_sms_collections():
    """Test SMS collections specifically"""
    try:
        logger.info("📱 Testing SMS Collections...")
        
        from app.db import db_manager
        
        database = db_manager.get_database_for_user("test_user_sms")
        
        # Test SMS collections
        sms_collections = ['sms_data', 'sms_test']
        
        for collection_name in sms_collections:
            try:
                collection = database[collection_name]
                
                # Test basic operations
                test_doc = {
                    "test": True,
                    "collection": collection_name,
                    "timestamp": datetime.now()
                }
                
                result = await collection.insert_one(test_doc)
                logger.info(f"✅ {collection_name} insert successful: {result.inserted_id}")
                
                # Clean up
                await collection.delete_one({"_id": result.inserted_id})
                logger.info(f"✅ {collection_name} cleanup successful")
                
            except Exception as e:
                logger.error(f"❌ {collection_name} test failed: {e}")
                return False
        
        logger.info("🎉 All SMS collection tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ SMS collections test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 MongoDB Connection Test Script")
    logger.info("=" * 50)
    
    # Test basic connection
    connection_ok = await test_mongodb_connection()
    if not connection_ok:
        logger.error("❌ Basic connection test failed")
        return
    
    # Test SMS collections
    sms_ok = await test_sms_collections()
    if not sms_ok:
        logger.error("❌ SMS collections test failed")
        return
    
    logger.info("🎉 All tests passed! MongoDB connection is working correctly.")
    logger.info("✅ You can now start the server with: python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001")

if __name__ == "__main__":
    asyncio.run(main()) 