#!/usr/bin/env python3
"""
SMS System Testing Script
=========================

Consolidated script for testing SMS functionality, creating collections, and populating test data.
This replaces multiple redundant testing files with a single, comprehensive testing solution.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test user ID
TEST_USER_ID = "test_user_sms_integration"

# Sample SMS test data (15 records)
SMS_TEST_DATA = [
    # Bank Debit Transactions
    {
        "sms_id": "sms_test_001",
        "user_id": TEST_USER_ID,
        "provider": "android_sms",
        "sms_type": "transaction",
        "sender_number": "HDFCBANK",
        "sender_name": "HDFC Bank",
        "message_body": "Rs. 2500 debited from your account XX1234 on 15-01-2024 at 14:30. Available balance: Rs. 45,000. Transaction ID: HDFC123456789. If not you, call 1800-123-4567.",
        "received_date": "2024-01-15T14:30:00",
        "is_read": False,
        "is_archived": False,
        "is_financial": True,
        "processed_at": "2024-01-15T14:35:00",
        "extraction_confidence": 0.95,
        "financial_data_extracted": True,
        "created_at": "2024-01-15T14:35:00",
        "updated_at": "2024-01-15T14:35:00"
    },
    {
        "sms_id": "sms_test_002",
        "user_id": TEST_USER_ID,
        "provider": "android_sms",
        "sms_type": "transaction",
        "sender_number": "ICICIBANK",
        "sender_name": "ICICI Bank",
        "message_body": "Rs. 1200 credited to your account XX5678 on 16-01-2024 at 10:15. Transaction ID: ICICI123456789. Available balance: Rs. 67,800.",
        "received_date": "2024-01-16T10:15:00",
        "is_read": False,
        "is_archived": False,
        "is_financial": True,
        "processed_at": "2024-01-16T10:20:00",
        "extraction_confidence": 0.92,
        "financial_data_extracted": True,
        "created_at": "2024-01-16T10:20:00",
        "updated_at": "2024-01-16T10:20:00"
    },
    {
        "sms_id": "sms_test_003",
        "user_id": TEST_USER_ID,
        "provider": "android_sms",
        "sms_type": "transaction",
        "sender_number": "NETFLIX",
        "sender_name": "Netflix",
        "message_body": "Rs. 1499 debited from your credit card ending 1234 on 20-01-2024. Netflix subscription renewed. Transaction ID: NFLX789456123.",
        "received_date": "2024-01-20T08:00:00",
        "is_read": False,
        "is_archived": False,
        "is_financial": True,
        "processed_at": "2024-01-20T08:05:00",
        "extraction_confidence": 0.93,
        "financial_data_extracted": True,
        "created_at": "2024-01-20T08:05:00",
        "updated_at": "2024-01-20T08:05:00"
    },
    {
        "sms_id": "sms_test_004",
        "user_id": TEST_USER_ID,
        "provider": "android_sms",
        "sms_type": "transaction",
        "sender_number": "AMAZON",
        "sender_name": "Amazon",
        "message_body": "Rs. 2500 refunded to your account XX1234 on 21-01-2024. Order ID: AMZ123456789. Transaction ID: AMZ987654321.",
        "received_date": "2024-01-21T16:30:00",
        "is_read": False,
        "is_archived": False,
        "is_financial": True,
        "processed_at": "2024-01-21T16:35:00",
        "extraction_confidence": 0.96,
        "financial_data_extracted": True,
        "created_at": "2024-01-21T16:35:00",
        "updated_at": "2024-01-21T16:35:00"
    },
    {
        "sms_id": "sms_test_005",
        "user_id": TEST_USER_ID,
        "provider": "android_sms",
        "sms_type": "transaction",
        "sender_number": "UPI",
        "sender_name": "UPI Notification",
        "message_body": "Rs. 500 sent to merchant@upi on 17-01-2024 at 18:45. UPI Ref: 123456789012. Transaction ID: UPI987654321.",
        "received_date": "2024-01-17T18:45:00",
        "is_read": False,
        "is_archived": False,
        "is_financial": True,
        "processed_at": "2024-01-17T18:50:00",
        "extraction_confidence": 0.94,
        "financial_data_extracted": True,
        "created_at": "2024-01-17T18:50:00",
        "updated_at": "2024-01-17T18:50:00"
    }
]

async def create_sms_collections():
    """Create SMS collections in the database"""
    try:
        logger.info("🚀 Creating SMS Collections...")
        
        from app.db import db_manager
        
        database = db_manager.get_database_for_user(TEST_USER_ID)
        
        # Create collections by inserting a dummy document and then deleting it
        sms_data_collection = database['sms_data']
        await sms_data_collection.insert_one({
            "dummy": True,
            "created_at": datetime.now(),
            "purpose": "collection_creation"
        })
        await sms_data_collection.delete_one({"dummy": True})
        logger.info("✅ Created sms_data collection")
        
        sms_test_collection = database['sms_test']
        await sms_test_collection.insert_one({
            "dummy": True,
            "created_at": datetime.now(),
            "purpose": "collection_creation"
        })
        await sms_test_collection.delete_one({"dummy": True})
        logger.info("✅ Created sms_test collection")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating SMS collections: {e}")
        return False

async def populate_sms_test_data():
    """Populate SMS test data with extracted financial fields"""
    try:
        logger.info("📱 Populating SMS Test Data with Extracted Financial Fields...")
        
        from app.db import db_manager
        from app.services.sms_service import SMSProcessor
        
        processor = SMSProcessor()
        database = db_manager.get_database_for_user(TEST_USER_ID)
        collection = database['sms_test']
        
        # Clear existing test data
        logger.info("🧹 Clearing existing test data...")
        delete_result = await collection.delete_many({'user_id': TEST_USER_ID})
        logger.info(f"🗑️ Deleted {delete_result.deleted_count} existing records")
        
        # Process and extract financial fields from each SMS
        processed_sms_data = []
        
        for sms in SMS_TEST_DATA:
            try:
                # Extract financial transaction data
                transaction = processor._extract_single_transaction(sms)
                
                # Create enhanced SMS record with extracted fields
                enhanced_sms = {
                    # Original SMS data
                    "sms_id": sms["sms_id"],
                    "user_id": sms["user_id"],
                    "provider": sms["provider"],
                    "sms_type": sms["sms_type"],
                    "sender_number": sms["sender_number"],
                    "sender_name": sms["sender_name"],
                    "message_body": sms["message_body"],
                    "received_date": sms["received_date"],
                    "is_read": sms["is_read"],
                    "is_archived": sms["is_archived"],
                    "is_financial": sms["is_financial"],
                    "processed_at": sms["processed_at"],
                    "extraction_confidence": sms["extraction_confidence"],
                    "financial_data_extracted": sms["financial_data_extracted"],
                    "created_at": sms["created_at"],
                    "updated_at": sms["updated_at"],
                    
                    # Extracted Financial Fields
                    "amount": transaction.get("amount") if transaction else None,
                    "transaction_type": transaction.get("transaction_type") if transaction else None,
                    "currency": transaction.get("currency") if transaction else "INR",
                    "account_number": transaction.get("account_number") if transaction else None,
                    "bank_name": transaction.get("bank_name") if transaction else None,
                    "card_number": transaction.get("card_number") if transaction else None,
                    "card_type": transaction.get("card_type") if transaction else None,
                    "merchant_canonical": transaction.get("merchant_canonical") if transaction else None,
                    "service_category": transaction.get("service_category") if transaction else None,
                    "payment_method": transaction.get("payment_method") if transaction else None,
                    "payment_status": transaction.get("payment_status") if transaction else None,
                    "upi_id": transaction.get("upi_id") if transaction else None,
                    "transaction_reference": transaction.get("transaction_reference") if transaction else None,
                    "invoice_number": transaction.get("invoice_number") if transaction else None,
                    "order_id": transaction.get("order_id") if transaction else None,
                    "receipt_number": transaction.get("receipt_number") if transaction else None,
                    "available_balance": transaction.get("available_balance") if transaction else None,
                    "data_completeness": transaction.get("data_completeness") if transaction else None,
                    "source": transaction.get("source") if transaction else "sms",
                    "sms_message": transaction.get("sms_message") if transaction else sms["message_body"]
                }
                
                processed_sms_data.append(enhanced_sms)
                logger.info(f"✅ Processed SMS {sms['sms_id']}: ₹{enhanced_sms.get('amount')} {enhanced_sms.get('transaction_type')} - {enhanced_sms.get('bank_name')}")
                
            except Exception as e:
                logger.error(f"❌ Error processing SMS {sms['sms_id']}: {e}")
                processed_sms_data.append(sms)
        
        # Insert processed SMS data
        logger.info(f"📱 Inserting {len(processed_sms_data)} processed SMS records...")
        insert_result = await collection.insert_many(processed_sms_data)
        logger.info(f"✅ Successfully inserted {len(insert_result.inserted_ids)} SMS records")
        
        # Verify insertion
        count = await collection.count_documents({'user_id': TEST_USER_ID})
        logger.info(f"📊 Total SMS records in collection: {count}")
        
        # Get statistics
        financial_count = await collection.count_documents({
            'user_id': TEST_USER_ID,
            'is_financial': True
        })
        
        amount_count = await collection.count_documents({
            'user_id': TEST_USER_ID,
            'amount': {'$exists': True, '$ne': None}
        })
        
        transaction_type_count = await collection.count_documents({
            'user_id': TEST_USER_ID,
            'transaction_type': {'$exists': True, '$ne': None}
        })
        
        balance_count = await collection.count_documents({
            'user_id': TEST_USER_ID,
            'available_balance': {'$exists': True, '$ne': None}
        })
        
        account_count = await collection.count_documents({
            'user_id': TEST_USER_ID,
            'account_number': {'$exists': True, '$ne': None}
        })
        
        logger.info(f"💰 Financial SMS: {financial_count}")
        logger.info(f"💵 SMS with Amount: {amount_count}")
        logger.info(f"🔄 SMS with Transaction Type: {transaction_type_count}")
        logger.info(f"💰 SMS with Balance: {balance_count}")
        logger.info(f"📋 SMS with Account Number: {account_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error populating SMS test data: {e}")
        return False

async def test_sms_processing():
    """Test SMS processing functionality"""
    try:
        logger.info("🧪 Testing SMS Processing...")
        
        from app.services.sms_service import SMSProcessor
        
        processor = SMSProcessor()
        
        # Test with a sample SMS
        sample_sms = SMS_TEST_DATA[0]
        transaction = processor._extract_single_transaction(sample_sms)
        
        if transaction:
            logger.info("✅ SMS processing test successful!")
            logger.info(f"💰 Amount: ₹{transaction.get('amount')}")
            logger.info(f"🔄 Type: {transaction.get('transaction_type')}")
            logger.info(f"📋 Account: {transaction.get('account_number')}")
            logger.info(f"🏦 Bank: {transaction.get('bank_name')}")
            logger.info(f"🏪 Merchant: {transaction.get('merchant_canonical')}")
            logger.info(f"💳 Payment Method: {transaction.get('payment_method')}")
            logger.info(f"📂 Service Category: {transaction.get('service_category')}")
            logger.info(f"🆔 Transaction Ref: {transaction.get('transaction_reference')}")
            logger.info(f"💰 Balance: ₹{transaction.get('available_balance')}")
            logger.info(f"📊 Confidence: {transaction.get('extraction_confidence')}")
            logger.info(f"📈 Completeness: {transaction.get('data_completeness')}")
        else:
            logger.warning("⚠️ SMS processing test failed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing SMS processing: {e}")
        return False

async def verify_collections():
    """Verify that collections were created successfully"""
    try:
        logger.info("🔍 Verifying SMS Collections...")
        
        from app.db import db_manager
        
        database = db_manager.get_database_for_user(TEST_USER_ID)
        collections = await database.list_collection_names()
        
        logger.info(f"📋 Available collections: {collections}")
        
        sms_collections = [col for col in collections if 'sms' in col.lower()]
        logger.info(f"📱 SMS collections found: {sms_collections}")
        
        if 'sms_data' in collections:
            logger.info("✅ sms_data collection exists")
        else:
            logger.warning("⚠️ sms_data collection not found")
            
        if 'sms_test' in collections:
            logger.info("✅ sms_test collection exists")
            
            # Show sample records
            collection = database['sms_test']
            cursor = collection.find({'user_id': TEST_USER_ID}).limit(3)
            sample_records = await cursor.to_list(length=3)
            
            logger.info("\n📱 Sample SMS Records with Extracted Financial Fields:")
            for i, record in enumerate(sample_records, 1):
                logger.info(f"  {i}. {record.get('sender_name', 'Unknown')}")
                logger.info(f"     💰 Amount: ₹{record.get('amount', 'N/A')}")
                logger.info(f"     🔄 Type: {record.get('transaction_type', 'N/A')}")
                logger.info(f"     📋 Account: {record.get('account_number', 'N/A')}")
                logger.info(f"     🏦 Bank: {record.get('bank_name', 'N/A')}")
                logger.info(f"     💰 Balance: ₹{record.get('available_balance', 'N/A')}")
                logger.info("     ---")
        else:
            logger.warning("⚠️ sms_test collection not found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying collections: {e}")
        return False

async def cleanup_test_data():
    """Clean up test data"""
    try:
        logger.info("🧹 Cleaning up test data...")
        
        from app.db import db_manager
        
        database = db_manager.get_database_for_user(TEST_USER_ID)
        collection = database['sms_test']
        
        delete_result = await collection.delete_many({'user_id': TEST_USER_ID})
        logger.info(f"🗑️ Deleted {delete_result.deleted_count} test records")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error cleaning up test data: {e}")
        return False

async def main():
    """Main function"""
    logger.info("🚀 SMS System Testing Script")
    logger.info("=" * 60)
    
    try:
        # Step 1: Create collections
        logger.info("\n📋 Step 1: Creating SMS Collections")
        collections_created = await create_sms_collections()
        
        if not collections_created:
            logger.error("❌ Failed to create SMS collections")
            return
        
        # Step 2: Verify collections
        logger.info("\n🔍 Step 2: Verifying Collections")
        await verify_collections()
        
        # Step 3: Test SMS processing
        logger.info("\n🧪 Step 3: Testing SMS Processing")
        await test_sms_processing()
        
        # Step 4: Populate test data
        logger.info("\n📱 Step 4: Populating Test Data")
        data_populated = await populate_sms_test_data()
        
        if not data_populated:
            logger.error("❌ Failed to populate SMS test data")
            return
        
        logger.info("\n🎉 SMS System Testing Completed!")
        logger.info("=" * 60)
        logger.info("✅ SMS collections created successfully")
        logger.info("✅ SMS processing tested successfully")
        logger.info("✅ Test data populated with financial fields")
        logger.info("🧪 Ready to test your SMS integration!")
        
        # Show next steps
        logger.info("\n📋 Next Steps:")
        logger.info("1. 📊 Check MongoDB Compass for sms_test collection")
        logger.info("2. 🧪 Test your SMS API endpoints")
        logger.info("3. 🗑️ Run cleanup when done: python3 -c \"import asyncio; from test_sms_system import cleanup_test_data; asyncio.run(cleanup_test_data())\"")
        
    except Exception as e:
        logger.error(f"❌ Script failed: {e}")

if __name__ == "__main__":
    # Run the testing script
    asyncio.run(main()) 