#!/usr/bin/env python3
"""
Test Swiggy Classification Script
=================================

This script tests the improved classification for Swiggy emails.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from bson import ObjectId

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import required modules
from app.services.database_service import DatabaseService
from app.services.llm_service import LLMService
from app.workers.email_worker import EmailWorker

async def test_swiggy_classification():
    """Test classification of Swiggy emails."""
    try:
        logger.info("🧪 Testing Swiggy email classification")
        
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        # Find Swiggy emails
        swiggy_emails = await db.email_logs.find({
            "snippet": {"$regex": "swiggy", "$options": "i"}
        }).to_list(length=None)
        
        logger.info(f"📧 Found {len(swiggy_emails)} Swiggy emails")
        
        if not swiggy_emails:
            # Look for emails with swiggy in any field
            swiggy_emails = await db.email_logs.find({
                "$or": [
                    {"snippet": {"$regex": "swiggy", "$options": "i"}},
                    {"subject": {"$regex": "swiggy", "$options": "i"}},
                    {"raw_data.payload.headers": {"$elemMatch": {"value": {"$regex": "swiggy", "$options": "i"}}}}
                ]
            }).to_list(length=None)
            logger.info(f"📧 Found {len(swiggy_emails)} Swiggy emails (expanded search)")
        
        # Initialize services
        llm_service = LLMService()
        email_worker = EmailWorker()
        
        for email in swiggy_emails:
            email_id = str(email["_id"])
            user_id = email["user_id"]
            
            logger.info(f"🔍 Testing email: {email_id}")
            logger.info(f"📧 Subject: {email.get('subject', 'No subject')}")
            logger.info(f"📝 Snippet: {email.get('snippet', 'No snippet')[:100]}...")
            logger.info(f"🏷️ Current category: {email.get('email_category', 'None')}")
            
            # Test classification
            subject, body = email_worker._extract_email_content(email)
            full_content = f"Subject: {subject}\n\nBody: {body}"
            
            logger.info(f"📝 Full content preview: {full_content[:200]}...")
            
            # Test new classification
            new_category = await llm_service.classify_email(subject, full_content)
            logger.info(f"🎯 New classification: {new_category}")
            
            # If it's now classified as finance, test extraction
            if new_category == "finance":
                logger.info("💰 Testing financial extraction...")
                try:
                    extracted_data = await llm_service.extract_financial_data(subject, full_content)
                    logger.info(f"📊 Extracted data: {extracted_data}")
                    
                    # Test validation
                    is_valid = email_worker._is_valid_financial_data(extracted_data)
                    logger.info(f"✅ Valid financial data: {is_valid}")
                    
                except Exception as e:
                    logger.error(f"❌ Extraction error: {e}")
            
            logger.info("-" * 50)
        
    except Exception as e:
        logger.error(f"❌ Error in test: {e}")
        raise

async def reprocess_swiggy_emails():
    """Reprocess Swiggy emails with improved logic."""
    try:
        logger.info("🔄 Reprocessing Swiggy emails with improved logic")
        
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        # Find Swiggy emails
        swiggy_emails = await db.email_logs.find({
            "$or": [
                {"snippet": {"$regex": "swiggy", "$options": "i"}},
                {"subject": {"$regex": "swiggy", "$options": "i"}},
                {"raw_data.payload.headers": {"$elemMatch": {"value": {"$regex": "swiggy", "$options": "i"}}}}
            ]
        }).to_list(length=None)
        
        logger.info(f"📧 Found {len(swiggy_emails)} Swiggy emails to reprocess")
        
        # Initialize email worker
        email_worker = EmailWorker()
        
        processed_count = 0
        financial_count = 0
        
        for email in swiggy_emails:
            try:
                email_id = str(email["_id"])
                
                # Reset email status for reprocessing
                await db.email_logs.update_one(
                    {"_id": email["_id"]},
                    {
                        "$set": {
                            "classification_status": "pending",
                            "email_category": None,
                            "extraction_confidence": None,
                            "error_message": None,
                            "processing_attempts": 0,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                # Process email with improved logic
                success = await email_worker._process_single_email(email)
                
                if success:
                    processed_count += 1
                    
                    # Check if it was classified as financial
                    updated_email = await db.email_logs.find_one({"_id": email["_id"]})
                    if updated_email and updated_email.get("email_category") == "finance":
                        financial_count += 1
                        logger.info(f"✅ Swiggy email {email_id} classified as FINANCE")
                
            except Exception as e:
                logger.error(f"❌ Error reprocessing Swiggy email {email.get('_id', 'unknown')}: {e}")
        
        logger.info(f"🎉 Swiggy reprocessing completed!")
        logger.info(f"📊 Total processed: {processed_count}")
        logger.info(f"💰 Financial emails detected: {financial_count}")
        
        # Show financial transactions count
        financial_count_db = await db.financial_transactions.count_documents({})
        logger.info(f"💳 Total financial transactions in database: {financial_count_db}")
        
        # Show Swiggy transactions specifically
        swiggy_transactions = await db.financial_transactions.find({
            "$or": [
                {"merchant_name": {"$regex": "swiggy", "$options": "i"}},
                {"merchant_canonical": {"$regex": "swiggy", "$options": "i"}},
                {"service_name": {"$regex": "swiggy", "$options": "i"}}
            ]
        }).to_list(length=None)
        
        logger.info(f"🍕 Swiggy transactions in database: {len(swiggy_transactions)}")
        
        for transaction in swiggy_transactions:
            logger.info(f"🍕 Swiggy transaction: {transaction.get('merchant_name')} - {transaction.get('amount')} {transaction.get('currency')}")
        
        return {
            "total_swiggy_emails": len(swiggy_emails),
            "processed": processed_count,
            "financial_detected": financial_count,
            "swiggy_transactions": len(swiggy_transactions)
        }
        
    except Exception as e:
        logger.error(f"❌ Error in reprocessing: {e}")
        raise

async def main():
    """Main function to run tests."""
    try:
        logger.info("🚀 Starting Swiggy classification tests")
        
        # Step 1: Test classification
        await test_swiggy_classification()
        
        # Step 2: Reprocess Swiggy emails
        result = await reprocess_swiggy_emails()
        
        logger.info("=" * 50)
        logger.info("📋 FINAL SUMMARY")
        logger.info("=" * 50)
        logger.info(f"📧 Total Swiggy emails: {result['total_swiggy_emails']}")
        logger.info(f"✅ Successfully processed: {result['processed']}")
        logger.info(f"💰 Financial emails detected: {result['financial_detected']}")
        logger.info(f"🍕 Swiggy transactions stored: {result['swiggy_transactions']}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 