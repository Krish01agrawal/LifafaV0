#!/usr/bin/env python3
"""
Cleanup and Reprocess Script
============================

This script cleans up invalid financial transactions and reprocesses emails
with improved classification and extraction logic.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
from bson import ObjectId

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import required modules
from app.services.database_service import DatabaseService
from app.services.llm_service import LLMService
from app.workers.email_worker import EmailWorker

async def cleanup_invalid_financial_transactions(user_id: str):
    """Remove invalid financial transactions with mostly null values."""
    try:
        logger.info(f"🧹 Cleaning up invalid financial transactions for user {user_id}")
        
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        # Get all financial transactions for the user
        transactions = await db.financial_transactions.find({"user_id": user_id}).to_list(length=None)
        logger.info(f"📊 Found {len(transactions)} financial transactions")
        
        # Count invalid transactions (those with mostly null values)
        invalid_count = 0
        valid_count = 0
        
        for transaction in transactions:
            # Check if transaction has meaningful data
            key_fields = [
                "amount", "merchant_canonical", "merchant_name", 
                "transaction_type", "payment_method", "transaction_reference",
                "invoice_number", "order_id", "receipt_number"
            ]
            
            meaningful_fields = 0
            for field in key_fields:
                value = transaction.get(field)
                if value and value != "" and value != 0:
                    meaningful_fields += 1
            
            # If less than 2 meaningful fields, consider it invalid
            if meaningful_fields < 2:
                invalid_count += 1
                await db.financial_transactions.delete_one({"_id": transaction["_id"]})
                logger.info(f"🗑️ Deleted invalid transaction: {transaction.get('_id')} - {transaction.get('service_name', 'Unknown')}")
            else:
                valid_count += 1
        
        logger.info(f"✅ Cleanup completed: {valid_count} valid, {invalid_count} invalid transactions removed")
        return valid_count, invalid_count
        
    except Exception as e:
        logger.error(f"❌ Error in cleanup: {e}")
        raise

async def reprocess_with_improved_logic(user_id: str):
    """Reprocess emails with improved classification and extraction."""
    try:
        logger.info(f"🔄 Starting reprocessing with improved logic for user {user_id}")
        
        db = DatabaseService.get_database()
        
        # Get all emails for the user
        emails = await db.email_logs.find({"user_id": user_id}).to_list(length=None)
        logger.info(f"📧 Found {len(emails)} emails to reprocess")
        
        # Initialize email worker
        email_worker = EmailWorker()
        
        # Process emails in batches
        batch_size = 10
        total_processed = 0
        total_financial = 0
        
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]
            logger.info(f"🔄 Processing batch {i//batch_size + 1}/{(len(emails) + batch_size - 1)//batch_size}")
            
            for email in batch:
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
                        total_processed += 1
                        
                        # Check if it was classified as financial
                        updated_email = await db.email_logs.find_one({"_id": email["_id"]})
                        if updated_email and updated_email.get("email_category") == "finance":
                            total_financial += 1
                            logger.info(f"✅ Email {email_id} classified as FINANCE")
                    
                except Exception as e:
                    logger.error(f"❌ Error reprocessing email {email.get('_id', 'unknown')}: {e}")
        
        # Update user status
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "categorization_status": "completed",
                    "emails_categorized": total_processed,
                    "emails_failed": len(emails) - total_processed,
                    "categorization_completed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"🎉 Reprocessing completed!")
        logger.info(f"📊 Total processed: {total_processed}")
        logger.info(f"💰 Financial emails detected: {total_financial}")
        logger.info(f"❌ Failed: {len(emails) - total_processed}")
        
        # Show financial transactions count
        financial_count = await db.financial_transactions.count_documents({"user_id": user_id})
        logger.info(f"💳 Financial transactions in database: {financial_count}")
        
        return {
            "total_emails": len(emails),
            "processed": total_processed,
            "financial_detected": total_financial,
            "financial_stored": financial_count,
            "failed": len(emails) - total_processed
        }
        
    except Exception as e:
        logger.error(f"❌ Error in reprocessing: {e}")
        raise

async def main():
    """Main function to run cleanup and reprocessing."""
    try:
        # Use the correct user ID from the database
        user_id = "687a27f91a9e0ecec8a8c585"  # Correct user ID from database
        
        logger.info(f"🚀 Starting cleanup and reprocessing with improved logic")
        logger.info(f"👤 User ID: {user_id}")
        
        # Step 1: Clean up invalid financial transactions
        valid_count, invalid_count = await cleanup_invalid_financial_transactions(user_id)
        
        # Step 2: Reprocess with improved logic
        result = await reprocess_with_improved_logic(user_id)
        
        logger.info("=" * 50)
        logger.info("📋 FINAL SUMMARY")
        logger.info("=" * 50)
        logger.info(f"🧹 Cleanup: {valid_count} valid, {invalid_count} invalid transactions removed")
        logger.info(f"📧 Total emails: {result['total_emails']}")
        logger.info(f"✅ Successfully processed: {result['processed']}")
        logger.info(f"💰 Financial emails detected: {result['financial_detected']}")
        logger.info(f"💳 Financial transactions stored: {result['financial_stored']}")
        logger.info(f"❌ Failed: {result['failed']}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 