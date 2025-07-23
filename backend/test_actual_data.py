#!/usr/bin/env python3
"""
Test Actual Data
===============

Test script to get actual transaction data and see the structure.
"""

import asyncio
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_actual_data():
    """Test actual transaction data"""
    try:
        logger.info("🔍 Testing Actual Transaction Data...")
        
        from app.db import db_manager
        
        # Test with specific user ID from MongoDB Compass
        test_user_id = "687f39590f9441b971249881"
        
        database = db_manager.get_database_for_user(test_user_id)
        collection = database['financial_transactions']
        
        # Get all transactions for this user
        cursor = collection.find({'user_id': test_user_id})
        transactions = await cursor.to_list(length=None)
        
        logger.info(f"📊 Found {len(transactions)} transactions")
        
        # Show first 3 transactions with all fields
        for i, transaction in enumerate(transactions[:3], 1):
            logger.info(f"📋 Transaction {i}:")
            logger.info(f"   _id: {transaction.get('_id')}")
            logger.info(f"   user_id: {transaction.get('user_id')}")
            logger.info(f"   email_id: {transaction.get('email_id')}")
            logger.info(f"   transaction_type: {transaction.get('transaction_type')}")
            logger.info(f"   amount: {transaction.get('amount')}")
            logger.info(f"   currency: {transaction.get('currency')}")
            logger.info(f"   merchant_canonical: {transaction.get('merchant_canonical')}")
            logger.info(f"   merchant_original: {transaction.get('merchant_original')}")
            logger.info(f"   payment_method: {transaction.get('payment_method')}")
            logger.info(f"   bank_name: {transaction.get('bank_name')}")
            logger.info(f"   account_number: {transaction.get('account_number')}")
            logger.info(f"   is_subscription: {transaction.get('is_subscription')}")
            logger.info("   ---")
        
        # Test subscriptions
        subscriptions_collection = database['subscriptions']
        cursor = subscriptions_collection.find({'user_id': test_user_id})
        subscriptions = await cursor.to_list(length=None)
        
        logger.info(f"📊 Found {len(subscriptions)} subscriptions")
        
        # Show first 2 subscriptions
        for i, subscription in enumerate(subscriptions[:2], 1):
            logger.info(f"📋 Subscription {i}:")
            logger.info(f"   _id: {subscription.get('_id')}")
            logger.info(f"   user_id: {subscription.get('user_id')}")
            logger.info(f"   service_name: {subscription.get('service_name')}")
            logger.info(f"   service_category: {subscription.get('service_category')}")
            logger.info(f"   amount: {subscription.get('amount')}")
            logger.info(f"   billing_frequency: {subscription.get('billing_frequency')}")
            logger.info(f"   status: {subscription.get('status')}")
            logger.info("   ---")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 Actual Data Test")
    logger.info("=" * 50)
    
    success = await test_actual_data()
    
    if success:
        logger.info("🎉 Actual data test completed successfully!")
    else:
        logger.error("❌ Actual data test failed!")

if __name__ == "__main__":
    asyncio.run(main()) 