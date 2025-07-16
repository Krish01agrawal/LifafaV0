import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
import hashlib
from bson import ObjectId

from app.services.database_service import DatabaseService
from app.services.llm_service import llm_service
from app.services.cache_service import cache
from app.config.settings import settings

logger = logging.getLogger(__name__)

class EmailWorker:
    """Background worker for processing emails."""
    
    def __init__(self):
        self.db = None
        self.batch_size = settings.email_batch_size
        self.max_retries = settings.max_retries
    
    def _get_db(self):
        """Get database instance (lazy initialization)."""
        if self.db is None:
            self.db = DatabaseService.get_database()
        return self.db
    
    async def process_email_batch(self, user_id: str, email_ids: List[str]):
        """Process a batch of emails."""
        try:
            logger.info(f"Processing batch of {len(email_ids)} emails for user {user_id}")
            
            # Get emails from database
            emails = await self._get_db().email_logs.find({
                "_id": {"$in": [ObjectId(eid) for eid in email_ids]},
                "user_id": user_id
            }).to_list(length=None)
            
            if not emails:
                logger.warning(f"No emails found for batch processing")
                return
            
            # Process emails in parallel (with concurrency limit)
            semaphore = asyncio.Semaphore(5)  # Limit concurrent LLM calls
            tasks = []
            
            for email in emails:
                task = asyncio.create_task(
                    self._process_single_email_with_semaphore(semaphore, email)
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count successes and failures
            success_count = sum(1 for r in results if r is True)
            failure_count = len(results) - success_count
            
            logger.info(f"Batch processing completed: {success_count} success, {failure_count} failures")
            
            # Update cache with progress
            await self._update_progress_cache(user_id, success_count, failure_count)
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            raise
    
    async def _process_single_email_with_semaphore(self, semaphore: asyncio.Semaphore, email: Dict[str, Any]):
        """Process a single email with semaphore for concurrency control."""
        async with semaphore:
            return await self._process_single_email(email)
    
    async def _process_single_email(self, email: Dict[str, Any]) -> bool:
        """Process a single email through the complete pipeline."""
        try:
            email_id = str(email["_id"])
            user_id = email["user_id"]
            
            # Check if already processed
            if email.get("classification_status") in ["classified", "extracted"]:
                logger.debug(f"Email {email_id} already processed, skipping")
                return True
            
            # Update status to processing
            await self._get_db().email_logs.update_one(
                {"_id": email["_id"]},
                {
                    "$set": {
                        "classification_status": "processing",
                        "processing_attempts": email.get("processing_attempts", 0) + 1,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Step 1: Classify email
            category = await self._classify_email(email)
            
            # Update with classification
            await self._get_db().email_logs.update_one(
                {"_id": email["_id"]},
                {
                    "$set": {
                        "email_category": category,
                        "classification_status": "classified",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Step 2: Extract structured data based on category
            if category in ["finance", "travel", "job", "promotion"]:
                extracted_data = await self._extract_structured_data(email, category)
                
                if extracted_data:
                    # Store in appropriate collection
                    await self._store_extracted_data(user_id, email_id, category, extracted_data)
                    
                    # Update email status
                    await self._get_db().email_logs.update_one(
                        {"_id": email["_id"]},
                        {
                            "$set": {
                                "classification_status": "extracted",
                                "extraction_confidence": extracted_data.get("extraction_confidence", 0.0),
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                else:
                    # Mark as failed extraction
                    await self._get_db().email_logs.update_one(
                        {"_id": email["_id"]},
                        {
                            "$set": {
                                "classification_status": "extraction_failed",
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
            else:
                # For other categories, just mark as classified
                await self._get_db().email_logs.update_one(
                    {"_id": email["_id"]},
                    {
                        "$set": {
                            "classification_status": "classified",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
            
            logger.debug(f"Successfully processed email {email_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing email {email.get('_id', 'unknown')}: {e}")
            
            # Update status to failed
            try:
                await self._get_db().email_logs.update_one(
                    {"_id": email["_id"]},
                    {
                        "$set": {
                            "classification_status": "failed",
                            "error_message": str(e),
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
            except:
                pass
            
            return False
    
    async def _classify_email(self, email: Dict[str, Any]) -> str:
        """Classify email into categories using LLM."""
        try:
            subject = email.get("email_subject", "")
            body = email.get("email_body", "")
            
            # Use LLM to classify
            category = await llm_service.classify_email(subject, body)
            
            return category
            
        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            return "other"
    
    async def _extract_structured_data(self, email: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Extract structured data based on email category."""
        try:
            subject = email.get("email_subject", "")
            body = email.get("email_body", "")
            
            if category == "finance":
                return await llm_service.extract_financial_data(subject, body)
            elif category == "travel":
                return await llm_service.extract_travel_data(subject, body)
            elif category == "job":
                return await llm_service.extract_job_data(subject, body)
            elif category == "promotion":
                return await llm_service.extract_promotional_data(subject, body)
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error extracting data for category {category}: {e}")
            return {}
    
    async def _store_extracted_data(self, user_id: str, email_id: str, category: str, data: Dict[str, Any]):
        """Store extracted data in appropriate collection."""
        try:
            # Add common fields
            data["user_id"] = user_id
            data["email_id"] = email_id
            data["created_at"] = datetime.utcnow()
            data["updated_at"] = datetime.utcnow()
            
            # Store in appropriate collection
            if category == "finance":
                await self._get_db().financial_transactions.insert_one(data)
            elif category == "travel":
                await self._get_db().travel_bookings.insert_one(data)
            elif category == "job":
                await self._get_db().job_communications.insert_one(data)
            elif category == "promotion":
                await self._get_db().promotional_emails.insert_one(data)
            
            logger.debug(f"Stored {category} data for email {email_id}")
            
        except Exception as e:
            logger.error(f"Error storing extracted data: {e}")
            raise
    
    async def _update_progress_cache(self, user_id: str, success_count: int, failure_count: int):
        """Update progress in cache."""
        try:
            cache_key = f"sync_status:{user_id}"
            cached_status = cache.get(cache_key)
            
            if cached_status:
                cached_status["emails_processed"] += success_count
                cached_status["emails_failed"] += failure_count
                cached_status["last_updated"] = datetime.utcnow()
                
                cache.set(cache_key, cached_status, ttl=3600)
                
        except Exception as e:
            logger.error(f"Error updating progress cache: {e}")

# Global worker instance
email_worker = EmailWorker()

async def queue_email_processing(user_id: str, email_ids: List[str]):
    """Queue emails for background processing."""
    try:
        logger.info(f"Queueing {len(email_ids)} emails for processing")
        
        # Process in batches
        batch_size = settings.email_batch_size
        for i in range(0, len(email_ids), batch_size):
            batch = email_ids[i:i + batch_size]
            
            # Add to MongoDB queue (simple implementation)
            await DatabaseService.get_database().email_queue.insert_one({
                "user_id": user_id,
                "email_ids": batch,
                "status": "pending",
                "priority": 1,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            # Process immediately (in production, you'd use a proper task queue)
            await email_worker.process_email_batch(user_id, batch)
            
    except Exception as e:
        logger.error(f"Error queueing email processing: {e}")
        raise

async def process_queue():
    """Process queued emails (background task)."""
    try:
        db = DatabaseService.get_database()
        
        while True:
            # Get pending items from queue
            queue_item = await db.email_queue.find_one_and_update(
                {"status": "pending"},
                {"$set": {"status": "processing", "updated_at": datetime.utcnow()}},
                sort=[("priority", -1), ("created_at", 1)]
            )
            
            if not queue_item:
                # No items in queue, wait
                await asyncio.sleep(10)
                continue
            
            try:
                # Process the batch
                await email_worker.process_email_batch(
                    queue_item["user_id"],
                    queue_item["email_ids"]
                )
                
                # Mark as completed
                await db.email_queue.update_one(
                    {"_id": queue_item["_id"]},
                    {"$set": {"status": "completed", "updated_at": datetime.utcnow()}}
                )
                
            except Exception as e:
                logger.error(f"Error processing queue item: {e}")
                
                # Mark as failed
                await db.email_queue.update_one(
                    {"_id": queue_item["_id"]},
                    {"$set": {"status": "failed", "error": str(e), "updated_at": datetime.utcnow()}}
                )
                
    except Exception as e:
        logger.error(f"Error in queue processor: {e}")
        raise 