#!/usr/bin/env python3
"""
Database Connection Test
=======================

Test script to check which database URL is being used and verify the connection.
"""

import asyncio
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_database_configuration():
    """Test database configuration and connection"""
    try:
        logger.info("🔍 Testing Database Configuration...")
        
        # Check environment variables
        logger.info(f"📋 Environment Variables:")
        logger.info(f"   MONGO_URI: {os.getenv('MONGO_URI', 'NOT SET')}")
        logger.info(f"   MONGODB_CONNECTION_STRING: {os.getenv('MONGODB_CONNECTION_STRING', 'NOT SET')}")
        
        # Check settings
        from app.config.settings import settings
        logger.info(f"📋 Settings Configuration:")
        logger.info(f"   mongodb_url: {settings.mongodb_url}")
        logger.info(f"   mongodb_database: {settings.mongodb_database}")
        logger.info(f"   is_production: {settings.is_production}")
        
        # Check config
        from app.config import SHARD_DATABASES, LOCAL_MONGODB_URL
        logger.info(f"📋 Config Configuration:")
        logger.info(f"   SHARD_DATABASES: {SHARD_DATABASES}")
        logger.info(f"   LOCAL_MONGODB_URL: {LOCAL_MONGODB_URL}")
        
        # Test database connection
        from app.db import db_manager
        
        logger.info(f"📋 Database Manager Configuration:")
        logger.info(f"   Number of clients: {len(db_manager.clients)}")
        for i, client in db_manager.clients.items():
            if client:
                logger.info(f"   Client {i}: Connected")
            else:
                logger.info(f"   Client {i}: Not connected")
        
        # Test with specific user ID from MongoDB Compass
        test_user_id = "687f39590f9441b971249881"  # From the MongoDB Compass image
        
        logger.info(f"🔍 Testing with user ID: {test_user_id}")
        
        database = db_manager.get_database_for_user(test_user_id)
        if database is None:
            logger.error("❌ Failed to get database")
            return False
        
        logger.info(f"✅ Database connection successful")
        logger.info(f"📋 Database name: {database.name}")
        
        # Test financial_transactions collection
        collection = database['financial_transactions']
        
        # Count documents for this user
        count = await collection.count_documents({'user_id': test_user_id})
        logger.info(f"📊 Financial transactions for user {test_user_id}: {count}")
        
        if count > 0:
            # Get a sample document
            sample = await collection.find_one({'user_id': test_user_id})
            if sample:
                logger.info(f"📋 Sample transaction:")
                logger.info(f"   Transaction ID: {sample.get('_id')}")
                logger.info(f"   Amount: {sample.get('amount')}")
                logger.info(f"   Merchant: {sample.get('merchant_canonical')}")
                logger.info(f"   Payment Method: {sample.get('payment_method')}")
                logger.info(f"   Bank Name: {sample.get('bank_name')}")
                logger.info(f"   Account Number: {sample.get('account_number')}")
        
        # Test subscriptions collection
        subscriptions_collection = database['subscriptions']
        sub_count = await subscriptions_collection.count_documents({'user_id': test_user_id})
        logger.info(f"📊 Subscriptions for user {test_user_id}: {sub_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database configuration test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 Database Configuration Test")
    logger.info("=" * 50)
    
    success = await test_database_configuration()
    
    if success:
        logger.info("🎉 Database configuration test completed successfully!")
    else:
        logger.error("❌ Database configuration test failed!")

if __name__ == "__main__":
    asyncio.run(main()) 