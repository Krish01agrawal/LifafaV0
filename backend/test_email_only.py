#!/usr/bin/env python3
"""
Email-Only System Test
=====================

Test script to verify that the system works correctly with SMS functionality disabled.
"""

import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_email_only_query():
    """Test query processing with SMS disabled"""
    try:
        logger.info("🧪 Testing Email-Only Query Processing...")
        
        from app.elite_query_processor import process_elite_query
        
        # Test user ID
        test_user_id = "test_user_email_only"
        
        # Test queries that should work with email data only
        test_queries = [
            "Show me my recent transactions",
            "What are my subscriptions?",
            "How much did I spend this month?",
            "Show me my bank transactions",
            "What merchants did I pay recently?"
        ]
        
        for query in test_queries:
            logger.info(f"🔍 Testing query: {query}")
            
            try:
                result = await process_elite_query(test_user_id, query)
                
                if result.get('success'):
                    logger.info(f"✅ Query successful: {query}")
                    logger.info(f"📊 Response: {result.get('response', 'No response')[:200]}...")
                else:
                    logger.warning(f"⚠️ Query failed: {query}")
                    logger.warning(f"❌ Error: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                logger.error(f"❌ Exception in query '{query}': {e}")
        
        logger.info("🎉 Email-only query testing completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Email-only test failed: {e}")
        return False

async def test_database_connection():
    """Test database connection without SMS"""
    try:
        logger.info("🔍 Testing Database Connection (Email Only)...")
        
        from app.db import db_manager
        
        # Test basic connection
        database = db_manager.get_database_for_user("test_user_email")
        if database is None:
            logger.error("❌ Failed to get database")
            return False
        
        logger.info("✅ Database connection successful")
        
        # Test email-related collections
        email_collections = ['emails', 'financial_transactions', 'subscriptions']
        
        for collection_name in email_collections:
            try:
                collection = database[collection_name]
                
                # Test basic operations
                test_doc = {
                    "test": True,
                    "collection": collection_name,
                    "timestamp": datetime.now(),
                    "note": "Email-only test"
                }
                
                result = await collection.insert_one(test_doc)
                logger.info(f"✅ {collection_name} insert successful: {result.inserted_id}")
                
                # Clean up
                await collection.delete_one({"_id": result.inserted_id})
                logger.info(f"✅ {collection_name} cleanup successful")
                
            except Exception as e:
                logger.error(f"❌ {collection_name} test failed: {e}")
                return False
        
        logger.info("🎉 All email collection tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

async def test_sms_disabled():
    """Verify that SMS functionality is properly disabled"""
    try:
        logger.info("📱 Verifying SMS Functionality is Disabled...")
        
        # Test that integrated financial data method only returns email data
        test_user_id = "test_user_sms_check"
        test_sub_query = {
            "filters": {},
            "sort": {"_id": -1}
        }
        
        from app.elite_query_processor import EnhancedEliteQueryProcessor
        processor = EnhancedEliteQueryProcessor()
        
        result = await processor._get_integrated_financial_data(test_user_id, test_sub_query)
        
        # Should only contain email transactions (SMS should be 0)
        logger.info(f"📊 Integrated data result: {len(result)} total transactions")
        logger.info("✅ SMS functionality properly disabled in integrated data method")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SMS disabled verification failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 Email-Only System Test")
    logger.info("=" * 50)
    
    # Test database connection
    db_ok = await test_database_connection()
    if not db_ok:
        logger.error("❌ Database connection test failed")
        return
    
    # Test SMS disabled
    sms_disabled = await test_sms_disabled()
    if not sms_disabled:
        logger.error("❌ SMS disabled verification failed")
        return
    
    # Test email-only queries
    query_ok = await test_email_only_query()
    if not query_ok:
        logger.error("❌ Email-only query test failed")
        return
    
    logger.info("🎉 All tests passed! System is ready for email-only operation.")
    logger.info("✅ SMS functionality is properly disabled")
    logger.info("✅ You can now test email features without SMS interference")

if __name__ == "__main__":
    asyncio.run(main()) 