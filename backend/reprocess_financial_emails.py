#!/usr/bin/env python3
"""
Reprocess Financial Emails Script
================================

This script reprocesses existing emails to identify financial transactions
that were misclassified and extract financial data from them.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import required modules
from app.services.database_service import DatabaseService
from app.services.llm_service import LLMService
from app.workers.email_worker import EmailWorker

async def reprocess_financial_emails(user_id: str):
    """Reprocess emails to identify financial transactions."""
    try:
        logger.info(f"🔄 Starting financial email reprocessing for user {user_id}")
        
        # Initialize services
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        llm_service = LLMService()
        email_worker = EmailWorker()
        
        # Find emails that might be financial but weren't classified as such
        potential_financial_emails = await db.email_logs.find({
            "user_id": user_id,
            "$or": [
                {"email_category": "subscription"},
                {"email_category": "technology"},
                {"email_category": "other"},
                {"email_category": {"$exists": False}}
            ]
        }).to_list(length=None)
        
        logger.info(f"📧 Found {len(potential_financial_emails)} emails to reprocess")
        
        financial_count = 0
        processed_count = 0
        
        for email in potential_financial_emails:
            try:
                # Extract subject and body
                raw_data = email.get("raw_data", {})
                subject = ""
                body = email.get("snippet", "")
                
                # Get subject from headers
                if raw_data and "payload" in raw_data:
                    headers = raw_data["payload"].get("headers", [])
                    for header in headers:
                        if header.get("name", "").lower() == "subject":
                            subject = header.get("value", "")
                            break
                
                # Check if this email should be financial
                content = f"{subject} {body}".lower()
                financial_keywords = [
                    'payment', 'transaction', 'bill', 'subscription', 'upi', 'debit', 'credit',
                    'amount', 'rs.', '₹', 'inr', 'bank', 'account', 'transfer', 'alert',
                    'statement', 'invoice', 'receipt', 'order', 'purchase', 'refund',
                    'netflix', 'spotify', 'amazon', 'flipkart', 'swiggy', 'zomato'
                ]
                
                is_financial = any(keyword in content for keyword in financial_keywords)
                
                if is_financial:
                    logger.info(f"💰 Found potential financial email: {subject[:50]}...")
                    
                    # Reclassify as finance
                    new_category = await llm_service.classify_email(subject, body)
                    
                    if new_category == "finance":
                        logger.info(f"✅ Reclassified as finance: {subject[:50]}...")
                        
                        # Extract financial data
                        financial_data = await llm_service.extract_financial_data(subject, body)
                        
                        if financial_data:
                            # Store in financial_transactions
                            email_id = str(email["_id"])
                            structured_data = email_worker._structure_financial_data(financial_data, user_id, email_id)
                            
                            await db.financial_transactions.update_one(
                                {"user_id": user_id, "email_id": email_id},
                                {"$set": structured_data},
                                upsert=True
                            )
                            
                            # Update categorized_emails
                            await db.categorized_emails.update_one(
                                {"user_id": user_id, "email_id": email_id},
                                {
                                    "$set": {
                                        "primary_category": "finance",
                                        "financial_data_extracted": True,
                                        "extracted_at": datetime.utcnow(),
                                        "updated_at": datetime.utcnow()
                                    }
                                }
                            )
                            
                            financial_count += 1
                            logger.info(f"✅ Stored financial data for email {email_id}")
                    
                    processed_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error reprocessing email {email.get('_id')}: {e}")
                continue
        
        logger.info(f"✅ Reprocessing complete:")
        logger.info(f"   📧 Processed: {processed_count} emails")
        logger.info(f"   💰 Financial transactions found: {financial_count}")
        
        # Update user status
        await db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "categorization_status": "completed",
                    "categorization_completed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "processed_count": processed_count,
            "financial_count": financial_count
        }
        
    except Exception as e:
        logger.error(f"❌ Error in reprocess_financial_emails: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def main():
    """Main function to run the reprocessing."""
    # Replace with actual user ID
    user_id = "687a4e40b269aaefa64563a3"
    
    result = await reprocess_financial_emails(user_id)
    print(f"Reprocessing result: {result}")

if __name__ == "__main__":
    asyncio.run(main()) 