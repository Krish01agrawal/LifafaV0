#!/usr/bin/env python3
"""
Fix Categorization Status
=========================

This script fixes the stuck categorization status by:
1. Processing all pending emails
2. Updating user status correctly
3. Ensuring background tasks are properly handled
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.database_service import DatabaseService
from app.workers.email_worker import EmailWorker, queue_email_processing

async def fix_categorization_status():
    """Fix the categorization status for all users."""
    try:
        print("=" * 60)
        print("🔧 FIXING CATEGORIZATION STATUS")
        print("=" * 60)
        
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        # Get all users with stuck categorization status
        users = await db.users.find({
            "categorization_status": "in_progress"
        }).to_list(length=None)
        
        if not users:
            print("✅ No users with stuck categorization status found")
            return
        
        print(f"📊 Found {len(users)} users with stuck categorization status")
        
        for user in users:
            user_id = str(user["_id"])
            email = user.get("email", "unknown")
            
            print(f"\n👤 Processing user: {email} (ID: {user_id})")
            
            # Check current email processing status
            total_emails = await db.email_logs.count_documents({"user_id": user_id})
            processed_emails = await db.email_logs.count_documents({
                "user_id": user_id,
                "classification_status": {"$in": ["classified", "extracted"]}
            })
            failed_emails = await db.email_logs.count_documents({
                "user_id": user_id,
                "classification_status": "failed"
            })
            pending_emails = await db.email_logs.count_documents({
                "user_id": user_id,
                "$or": [
                    {"classification_status": {"$in": ["pending", None]}},
                    {"classification_status": {"$exists": False}}
                ]
            })
            
            print(f"   📧 Total emails: {total_emails}")
            print(f"   ✅ Processed: {processed_emails}")
            print(f"   ❌ Failed: {failed_emails}")
            print(f"   ⏳ Pending: {pending_emails}")
            
            # If all emails are processed, update status to completed
            if processed_emails >= total_emails and total_emails > 0:
                await db.users.update_one(
                    {"_id": user["_id"]},
                    {
                        "$set": {
                            "categorization_status": "completed",
                            "emails_categorized": processed_emails,
                            "emails_failed": failed_emails,
                            "categorization_completed_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                print(f"   ✅ Updated status to 'completed'")
                
            # If there are pending emails, process them
            elif pending_emails > 0:
                print(f"   🔄 Processing {pending_emails} pending emails...")
                
                # Get pending email IDs
                pending_email_docs = await db.email_logs.find({
                    "user_id": user_id,
                    "$or": [
                        {"classification_status": {"$in": ["pending", None]}},
                        {"classification_status": {"$exists": False}}
                    ]
                }).to_list(length=None)
                
                email_ids = [str(doc["_id"]) for doc in pending_email_docs]
                
                # Process emails in batches
                batch_size = 16
                for i in range(0, len(email_ids), batch_size):
                    batch = email_ids[i:i + batch_size]
                    print(f"   📦 Processing batch {i//batch_size + 1}/{(len(email_ids) + batch_size - 1)//batch_size}")
                    
                    # Create email worker and process batch
                    worker = EmailWorker()
                    await worker.process_email_batch(user_id, batch)
                    
                    # Update user status after each batch
                    await worker._update_user_categorization_status(user_id)
                
                print(f"   ✅ Finished processing pending emails")
                
            else:
                print(f"   ⚠️  No action needed - status appears correct")
        
        print("\n" + "=" * 60)
        print("🎉 CATEGORIZATION STATUS FIX COMPLETED")
        print("=" * 60)
        
        # Show final status
        final_users = await db.users.find({
            "categorization_status": "in_progress"
        }).to_list(length=None)
        
        if final_users:
            print(f"⚠️  {len(final_users)} users still have 'in_progress' status")
            for user in final_users:
                print(f"   - {user.get('email', 'unknown')}")
        else:
            print("✅ All users now have correct categorization status")
            
    except Exception as e:
        print(f"❌ Error fixing categorization status: {e}")
        raise

async def check_email_processing_status():
    """Check the current email processing status."""
    try:
        print("=" * 60)
        print("📊 EMAIL PROCESSING STATUS CHECK")
        print("=" * 60)
        
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        # Get all users
        users = await db.users.find({}).to_list(length=None)
        
        for user in users:
            user_id = str(user["_id"])
            email = user.get("email", "unknown")
            
            print(f"\n👤 User: {email}")
            print(f"   🏷️  Categorization Status: {user.get('categorization_status', 'unknown')}")
            print(f"   📧 Email Count: {user.get('email_count', 0)}")
            print(f"   ✅ Emails Categorized: {user.get('emails_categorized', 0)}")
            print(f"   ❌ Emails Failed: {user.get('emails_failed', 0)}")
            
            # Check actual email processing status
            total_emails = await db.email_logs.count_documents({"user_id": user_id})
            processed_emails = await db.email_logs.count_documents({
                "user_id": user_id,
                "classification_status": {"$in": ["classified", "extracted"]}
            })
            failed_emails = await db.email_logs.count_documents({
                "user_id": user_id,
                "classification_status": "failed"
            })
            pending_emails = await db.email_logs.count_documents({
                "user_id": user_id,
                "$or": [
                    {"classification_status": {"$in": ["pending", None]}},
                    {"classification_status": {"$exists": False}}
                ]
            })
            
            print(f"   📊 Actual Status:")
            print(f"      - Total emails in DB: {total_emails}")
            print(f"      - Processed: {processed_emails}")
            print(f"      - Failed: {failed_emails}")
            print(f"      - Pending: {pending_emails}")
            
            if total_emails > 0:
                progress = (processed_emails / total_emails) * 100
                print(f"      - Progress: {progress:.1f}%")
                
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix categorization status")
    parser.add_argument("--check-only", action="store_true", help="Only check status, don't fix")
    
    args = parser.parse_args()
    
    if args.check_only:
        asyncio.run(check_email_processing_status())
    else:
        asyncio.run(fix_categorization_status()) 