#!/usr/bin/env python3
"""
Test Query Processor
===================

Test script to test the query processor with the actual user ID.
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_query_processor():
    """Test query processor with actual user ID"""
    try:
        logger.info("🧪 Testing Query Processor...")
        
        from app.elite_query_processor import process_elite_query
        
        # Test with actual user ID from MongoDB Compass
        test_user_id = "687f39590f9441b971249881"
        
        # Test queries
        test_queries = [
            "List all my transactions I have done on any type of buying subscriptions or any",
            "provide me credit card details used by me",
            "What are my subscriptions?",
            "Show me my bank transactions"
        ]
        
        for query in test_queries:
            logger.info(f"🔍 Testing query: {query}")
            
            try:
                result = await process_elite_query(test_user_id, query)
                
                if result.get('success'):
                    logger.info(f"✅ Query successful: {query}")
                    response = result.get('response', 'No response')
                    logger.info(f"📊 Response length: {len(response)} characters")
                    logger.info(f"📊 Response preview: {response[:300]}...")
                    
                    # Check if response contains actual data
                    if "no" in response.lower() and "found" in response.lower():
                        logger.warning(f"⚠️ Response indicates no data found for: {query}")
                    else:
                        logger.info(f"✅ Response contains data for: {query}")
                        
                else:
                    logger.warning(f"⚠️ Query failed: {query}")
                    logger.warning(f"❌ Error: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                logger.error(f"❌ Exception in query '{query}': {e}")
            
            logger.info("---")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Query processor test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 Query Processor Test")
    logger.info("=" * 50)
    
    success = await test_query_processor()
    
    if success:
        logger.info("🎉 Query processor test completed successfully!")
    else:
        logger.error("❌ Query processor test failed!")

if __name__ == "__main__":
    asyncio.run(main()) 