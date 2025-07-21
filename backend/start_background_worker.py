#!/usr/bin/env python3
"""
Background Email Processing Worker
=================================

This script runs a persistent background worker that processes email queues
to ensure categorization tasks are completed properly.
"""

import asyncio
import os
import sys
import signal
import logging
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.database_service import DatabaseService
from app.workers.email_worker import EmailWorker, process_queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackgroundWorker:
    """Background worker for processing emails."""
    
    def __init__(self):
        self.running = False
        self.worker = EmailWorker()
        
    async def start(self):
        """Start the background worker."""
        try:
            logger.info("🚀 Starting background email processing worker...")
            
            # Initialize database
            await DatabaseService.initialize()
            logger.info("✅ Database initialized")
            
            self.running = True
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            logger.info("🔄 Background worker started successfully")
            
            # Main processing loop
            while self.running:
                try:
                    await self._process_pending_emails()
                    await asyncio.sleep(30)  # Check every 30 seconds
                    
                except Exception as e:
                    logger.error(f"❌ Error in main processing loop: {e}")
                    await asyncio.sleep(60)  # Wait longer on error
                    
        except Exception as e:
            logger.error(f"❌ Error starting background worker: {e}")
            raise
        finally:
            await self.stop()
    
    async def _process_pending_emails(self):
        """Process pending emails for all users."""
        try:
            db = DatabaseService.get_database()
            
            # Find users with pending emails
            users_with_pending = await db.users.find({
                "categorization_status": "in_progress"
            }).to_list(length=None)
            
            if not users_with_pending:
                return
            
            logger.info(f"📊 Found {len(users_with_pending)} users with pending emails")
            
            for user in users_with_pending:
                user_id = str(user["_id"])
                email = user.get("email", "unknown")
                
                # Check for pending emails
                pending_emails = await db.email_logs.find({
                    "user_id": user_id,
                    "$or": [
                        {"classification_status": {"$in": ["pending", None]}},
                        {"classification_status": {"$exists": False}}
                    ]
                }).to_list(length=None)
                
                if not pending_emails:
                    # No pending emails, check if we should update status to completed
                    total_emails = await db.email_logs.count_documents({"user_id": user_id})
                    processed_emails = await db.email_logs.count_documents({
                        "user_id": user_id,
                        "classification_status": {"$in": ["classified", "extracted"]}
                    })
                    
                    if processed_emails >= total_emails and total_emails > 0:
                        await db.users.update_one(
                            {"_id": user["_id"]},
                            {
                                "$set": {
                                    "categorization_status": "completed",
                                    "categorization_completed_at": datetime.utcnow(),
                                    "updated_at": datetime.utcnow()
                                }
                            }
                        )
                        logger.info(f"✅ Updated user {email} status to 'completed'")
                    continue
                
                logger.info(f"🔄 Processing {len(pending_emails)} pending emails for user {email}")
                
                # Process emails in batches
                email_ids = [str(doc["_id"]) for doc in pending_emails]
                batch_size = 16
                
                for i in range(0, len(email_ids), batch_size):
                    if not self.running:
                        break
                        
                    batch = email_ids[i:i + batch_size]
                    logger.info(f"📦 Processing batch {i//batch_size + 1}/{(len(email_ids) + batch_size - 1)//batch_size} for {email}")
                    
                    try:
                        await self.worker.process_email_batch(user_id, batch)
                        await self.worker._update_user_categorization_status(user_id)
                    except Exception as e:
                        logger.error(f"❌ Error processing batch for user {email}: {e}")
                
                if not self.running:
                    break
                    
        except Exception as e:
            logger.error(f"❌ Error processing pending emails: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"📡 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def stop(self):
        """Stop the background worker."""
        logger.info("🛑 Stopping background worker...")
        self.running = False
        
        try:
            await DatabaseService.close()
            logger.info("✅ Database connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing database connection: {e}")

async def main():
    """Main function."""
    worker = BackgroundWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("👋 Worker stopped by user")
    except Exception as e:
        logger.error(f"❌ Worker stopped due to error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 