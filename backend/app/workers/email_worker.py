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
            
            # Update user categorization status
            await self._update_user_categorization_status(user_id)
            
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
            
            # Step 2: Store in categorized_emails collection for ALL categories
            await self._store_categorized_email(user_id, email_id, category, email)
            
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
            if category in ["finance", "subscription", "travel", "job", "promotion"]:
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
            
            # cleanup raw data for non-financial categories to save space
            if category not in [
                "finance", "subscription", "shopping", "food", "transport", "technology", "finance_investment"
            ]:
                await self._get_db().email_logs.update_one(
                    {"_id": email["_id"]},
                    {"$unset": {"raw_data": "", "raw_data_gzip": ""}}
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
                
                # Update user failure count
                await self._get_db().users.update_one(
                    {"_id": user_id},
                    {
                        "$inc": {"emails_failed": 1}
                    }
                )
            except:
                pass
            
            return False
    
    async def _classify_email(self, email: Dict[str, Any]) -> str:
        """Classify email into categories using LLM."""
        try:
            # Extract subject and body using helper method
            subject, body = self._extract_email_content(email)
            
            # Combine subject and body for better classification
            full_content = f"Subject: {subject}\n\nBody: {body}"
            
            logger.info(f"Classifying email - Subject: {subject[:50]}..., Body length: {len(body)} chars")
            
            # Use LLM to classify with full content
            category = await llm_service.classify_email(subject, full_content)
            
            return category
            
        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            return "other"
    
    async def _extract_structured_data(self, email: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Extract structured data based on email category."""
        try:
            # Extract subject and body using helper method
            subject, body = self._extract_email_content(email)
            
            # Combine subject and body for better extraction
            full_content = f"Subject: {subject}\n\nBody: {body}"
            
            logger.info(f"Extracting {category} data - Subject: {subject[:50]}..., Body length: {len(body)} chars")
            
            if category == "finance":
                return await llm_service.extract_financial_data(subject, full_content)
            elif category == "travel":
                return await llm_service.extract_travel_data(subject, full_content)
            elif category == "job":
                return await llm_service.extract_job_data(subject, full_content)
            elif category == "promotion":
                return await llm_service.extract_promotional_data(subject, full_content)
            elif category == "subscription":
                return await llm_service.extract_subscription_data(subject, full_content)
            elif category in ["shopping", "food", "transport", "technology", "finance_investment"]:
                return await llm_service.extract_financial_data(subject, full_content)  # Use financial extraction for these
            elif category in ["utilities", "insurance", "real_estate", "health", "education", "entertainment"]:
                return await llm_service.extract_financial_data(subject, full_content)  # Use financial extraction for these
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error extracting data for category {category}: {e}")
            return {}
    
    async def _store_extracted_data(self, user_id: str, email_id: str, category: str, data: Dict[str, Any]):
        """Store extracted data in appropriate collection."""
        try:
            # Safely handle None data
            if not data:
                logger.warning(f"No data to store for email {email_id}")
                return
            
            # Validate financial data - only store if it has meaningful information
            if category == "finance":
                if not self._is_valid_financial_data(data):
                    logger.info(f"Skipping financial data for email {email_id} - insufficient data")
                    return
            
            # Add common fields
            data["user_id"] = user_id
            data["email_id"] = email_id
            data["created_at"] = datetime.utcnow()
            data["updated_at"] = datetime.utcnow()
            
            # Update categorized_emails collection with extracted data
            update_data = {
                "secondary_category": self._safe_get(data, "service_category"),
                "tertiary_category": self._safe_get(data, "merchant_category"),
                "confidence": self._safe_get(data, "confidence_score", 0.8),
                "key_indicators": self._generate_key_indicators(data),
                "merchant_detected": self._safe_get(data, "merchant_canonical"),
                "priority": self._calculate_priority(data),
                "importance_score": self._safe_get(data, "importance_score", 5.0),
                "financial_data_extracted": True,
                "extracted_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await self._get_db().categorized_emails.update_one(
                {"user_id": user_id, "email_id": email_id},
                {"$set": update_data}
            )
            
            # Store in appropriate specialized collection
            if category == "finance":
                # Structure the data properly for financial_transactions collection
                financial_data = self._structure_financial_data(data, user_id, email_id)
                await self._get_db().financial_transactions.insert_one(financial_data)
            elif category == "travel":
                await self._get_db().travel_bookings.insert_one(data)
            elif category == "job":
                await self._get_db().job_communications.insert_one(data)
            elif category == "promotion":
                await self._get_db().promotional_emails.insert_one(data)
            elif category == "subscription":
                # Store subscription data in both collections
                await self._get_db().subscriptions.insert_one(data)
                # Also store as financial transaction since subscriptions involve payments
                financial_data = self._structure_financial_data(data, user_id, email_id)
                await self._get_db().financial_transactions.insert_one(financial_data)
            elif category in ["shopping", "food", "transport", "technology", "finance_investment", "utilities", "insurance", "real_estate", "health", "education", "entertainment"]:
                # Store financial-like data in financial_transactions
                financial_data = self._structure_financial_data(data, user_id, email_id)
                await self._get_db().financial_transactions.insert_one(financial_data)
            
            # Update user progress
            await self._get_db().users.update_one(
                {"_id": user_id},
                {"$inc": {"emails_categorized": 1}}
            )
            
            logger.debug(f"Stored {category} data for email {email_id}")
            
        except Exception as e:
            logger.error(f"Error storing extracted data: {e}")
            raise
    
    async def _store_categorized_email(self, user_id: str, email_id: str, category: str, email: Dict[str, Any]):
        """Store categorized email in categorized_emails collection for ALL categories."""
        try:
            # Extract subject and body from raw Gmail data
            raw_data = email.get("raw_data", {})
            
            # Find subject from headers
            subject = ""
            body = email.get("snippet", "")
            
            # Try to get headers from payload
            if raw_data and "payload" in raw_data:
                headers = raw_data["payload"].get("headers", [])
                for header in headers:
                    if header.get("name", "").lower() == "subject":
                        subject = header.get("value", "")
                        break
                
                # Try to get body from payload parts
                if "parts" in raw_data["payload"]:
                    for part in raw_data["payload"]["parts"]:
                        if part.get("mimeType") == "text/plain":
                            encoded_body = part.get("body", {}).get("data", "")
                            if encoded_body:
                                try:
                                    import base64
                                    body = base64.urlsafe_b64decode(encoded_body + '=' * (-len(encoded_body) % 4)).decode('utf-8')
                                except:
                                    body = encoded_body
                            break
                        elif part.get("mimeType") == "text/html":
                            encoded_body = part.get("body", {}).get("data", "")
                            if encoded_body:
                                try:
                                    import base64
                                    body = base64.urlsafe_b64decode(encoded_body + '=' * (-len(encoded_body) % 4)).decode('utf-8')
                                except:
                                    body = encoded_body
                            break
                else:
                    # Try to get body from payload body directly
                    encoded_body = raw_data["payload"].get("body", {}).get("data", "")
                    if encoded_body:
                        try:
                            import base64
                            body = base64.urlsafe_b64decode(encoded_body + '=' * (-len(encoded_body) % 4)).decode('utf-8')
                        except:
                            body = encoded_body
            
            # If no body found, use snippet
            if not body:
                body = email.get("snippet", "")
            
            # Generate key indicators
            key_indicators = []
            if subject:
                key_indicators.append(f"Subject: {subject[:50]}")
            if body:
                # Extract first few words as indicators
                words = body.split()[:5]
                key_indicators.append(f"Content: {' '.join(words)}")
            
            # Create categorized email document
            categorized_email = {
                "user_id": user_id,
                "email_id": email_id,
                "primary_category": category,
                "secondary_category": None,
                "tertiary_category": None,
                "confidence": 0.8,  # Default confidence
                "key_indicators": key_indicators,
                "merchant_detected": None,
                "transaction_likely": category in ["finance", "subscription", "shopping", "food", "transport", "technology", "finance_investment", "utilities", "insurance", "real_estate", "health", "education", "entertainment"],
                "priority": "low",  # Default priority
                "importance_score": 5.0,  # Default importance
                "original_email": email,
                "categorized": True,
                "categorized_at": datetime.utcnow(),
                "financial_data_extracted": False,  # Will be updated if structured data is extracted
                "extracted_at": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Store in categorized_emails collection
            await self._get_db().categorized_emails.update_one(
                {"user_id": user_id, "email_id": email_id},
                {"$set": categorized_email},
                upsert=True
            )
            
            logger.debug(f"Stored categorized email for {email_id} with category {category}")
            
        except Exception as e:
            logger.error(f"Error storing categorized email: {e}")
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
    
    async def _update_user_categorization_status(self, user_id: str):
        """Update user's categorization status based on email processing results."""
        try:
            from bson import ObjectId
            
            # Get processing statistics
            total_emails = await self._get_db().email_logs.count_documents({"user_id": user_id})
            processed_emails = await self._get_db().email_logs.count_documents({
                "user_id": user_id,
                "classification_status": {"$in": ["classified", "extracted"]}
            })
            failed_emails = await self._get_db().email_logs.count_documents({
                "user_id": user_id,
                "classification_status": "failed"
            })
            pending_emails = await self._get_db().email_logs.count_documents({
                "user_id": user_id,
                "$or": [
                    {"classification_status": {"$in": ["pending", None]}},
                    {"classification_status": {"$exists": False}}
                ]
            })
            
            # Fetch expected total from user document
            user_doc = await self._get_db().users.find_one({"_id": ObjectId(user_id)})
            expected_total = user_doc.get("emails_to_categorize", total_emails)

            # Determine categorization status with more robust logic
            if total_emails == 0:
                categorization_status = "not_started"
            elif (processed_emails + failed_emails) >= total_emails and total_emails > 0:
                categorization_status = "completed"
            elif processed_emails > 0 or failed_emails > 0 or pending_emails > 0:
                categorization_status = "in_progress"
            else:
                categorization_status = "not_started"
            
            # Update user status
            await self._get_db().users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "categorization_status": categorization_status,
                        "emails_categorized": processed_emails,
                        "emails_failed": failed_emails,
                        "emails_to_categorize": total_emails,  # Update with actual total
                        "categorization_completed_at": datetime.utcnow() if categorization_status == "completed" else None,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            # If categorization finished, also mark gmail_sync_status -> completed for UI
            if categorization_status == "completed":
                await self._get_db().users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"gmail_sync_status": "completed", "updated_at": datetime.utcnow()}}
                )
                logger.info(f"🎉 DASHBOARD READY for user {user_id} - all emails processed")
            
            logger.info(f"Updated user {user_id} categorization status to: {categorization_status} ({processed_emails}/{total_emails} processed, {pending_emails} pending)")
            
        except Exception as e:
            logger.error(f"Error updating user categorization status: {e}")
    
    def _generate_key_indicators(self, data: Dict[str, Any]) -> List[str]:
        """Generate key indicators from extracted data"""
        indicators = []
        
        # Safely handle None data
        if not data:
            return indicators
        
        if data.get("merchant_canonical"):
            indicators.append(f"Merchant: {data['merchant_canonical']}")
        
        if data.get("amount") is not None:
            indicators.append(f"Amount: {data['amount']}")
        
        if data.get("transaction_type"):
            indicators.append(f"Type: {data['transaction_type']}")
        
        if data.get("payment_method"):
            indicators.append(f"Payment: {data['payment_method']}")
        
        if data.get("service_category"):
            indicators.append(f"Service: {data['service_category']}")
        
        return indicators
    
    def _calculate_priority(self, data: Dict[str, Any]) -> str:
        """Calculate priority based on data"""
        # Safely handle None data
        if not data:
            return "low"
        
        if data.get("requires_action"):
            return "high"
        
        # Safely handle amount comparison
        amount = data.get("amount")
        if amount is not None and isinstance(amount, (int, float)) and amount > 1000:
            return "medium"
        
        return "low"
    
    def _safe_get(self, data: Dict[str, Any], key: str, default=None):
        """Safely get value from data, handling None values"""
        if not data:
            return default
        
        value = data.get(key, default)
        if value is None:
            return default
        
        return value
    
    def _is_valid_financial_data(self, data: Dict[str, Any]) -> bool:
        """Check if financial data has meaningful information."""
        if not data:
            return False
        
        # Check for food delivery services - these are always valid
        merchant_name = self._safe_get(data, "merchant_name", "").lower()
        merchant_canonical = self._safe_get(data, "merchant_canonical", "").lower()
        service_name = self._safe_get(data, "service_name", "").lower()
        
        food_delivery_keywords = ["swiggy", "zomato", "blinkit", "grofers", "dunzo", "zepto"]
        
        # If it's a food delivery service, it's always valid
        for keyword in food_delivery_keywords:
            if (keyword in merchant_name or 
                keyword in merchant_canonical or 
                keyword in service_name):
                logger.info(f"Food delivery transaction detected: {merchant_name} - considering valid")
                return True
        
        # For other transactions, check if at least 2 key fields have meaningful values
        key_fields = [
            "amount", "merchant_canonical", "merchant_name", 
            "transaction_type", "payment_method", "transaction_reference",
            "invoice_number", "order_id", "receipt_number"
        ]
        
        meaningful_fields = 0
        for field in key_fields:
            value = self._safe_get(data, field)
            if value and value != "" and value != 0:
                meaningful_fields += 1
        
        # Must have at least 2 meaningful fields to be considered valid
        return meaningful_fields >= 2
    
    def _extract_email_content(self, email: Dict[str, Any]) -> tuple[str, str]:
        """Extract subject and body from email raw data."""
        raw_data = email.get("raw_data", {})
        
        # Find subject from headers
        subject = ""
        body = email.get("snippet", "")
        
        # Try to get headers from payload
        if raw_data and "payload" in raw_data:
            headers = raw_data["payload"].get("headers", [])
            for header in headers:
                if header.get("name", "").lower() == "subject":
                    subject = header.get("value", "")
                    break
            
            # Try to get body from payload parts
            if "parts" in raw_data["payload"]:
                # Try to get the largest text content
                best_body = ""
                best_size = 0
                
                for part in raw_data["payload"]["parts"]:
                    if part.get("mimeType") in ["text/plain", "text/html"]:
                        encoded_body = part.get("body", {}).get("data", "")
                        if encoded_body:
                            try:
                                import base64
                                decoded_body = base64.urlsafe_b64decode(encoded_body + '=' * (-len(encoded_body) % 4)).decode('utf-8')
                                if len(decoded_body) > best_size:
                                    best_body = decoded_body
                                    best_size = len(decoded_body)
                            except:
                                if len(encoded_body) > best_size:
                                    best_body = encoded_body
                                    best_size = len(encoded_body)
                
                if best_body:
                    body = best_body
            else:
                # Try to get body from payload body directly
                encoded_body = raw_data["payload"].get("body", {}).get("data", "")
                if encoded_body:
                    try:
                        import base64
                        body = base64.urlsafe_b64decode(encoded_body + '=' * (-len(encoded_body) % 4)).decode('utf-8')
                    except:
                        body = encoded_body
        
        # If no body found, use snippet
        if not body:
            body = email.get("snippet", "")
        
        return subject, body
    
    def _structure_financial_data(self, data: Dict[str, Any], user_id: str, email_id: str) -> Dict[str, Any]:
        """Structure financial data for the financial_transactions collection"""
        # Safely handle nested dictionaries
        bank_details = data.get("bank_details", {}) if data else {}
        upi_details = data.get("upi_details", {}) if data else {}
        receiver_details = upi_details.get("receiver", {}) if upi_details else {}
        
        structured_data = {
            "user_id": user_id,
            "email_id": email_id,
            "transaction_type": self._safe_get(data, "transaction_type"),
            "amount": self._safe_get(data, "amount"),
            "currency": self._safe_get(data, "currency", "INR"),
            "transaction_date": self._safe_get(data, "transaction_date"),
            "due_date": self._safe_get(data, "due_date"),
            "service_period_start": self._safe_get(data, "service_period_start"),
            "service_period_end": self._safe_get(data, "service_period_end"),
            "merchant_canonical": self._safe_get(data, "merchant_canonical"),
            "merchant_original": self._safe_get(data, "merchant_name"),
            "merchant_patterns": self._safe_get(data, "merchant_patterns", []),
            "service_category": self._safe_get(data, "service_category"),
            "service_name": self._safe_get(data, "service_name"),
            "payment_method": self._safe_get(data, "payment_method"),
            "payment_status": self._safe_get(data, "payment_status"),
            "transaction_reference": self._safe_get(data, "transaction_reference"),
            "invoice_number": self._safe_get(data, "invoice_number"),
            "order_id": self._safe_get(data, "order_id"),
            "receipt_number": self._safe_get(data, "receipt_number"),
            "bank_name": bank_details.get("bank_name") if bank_details else None,
            "account_number": bank_details.get("account_number") if bank_details else None,
            "upi_id": receiver_details.get("upi_id") if receiver_details else None,
            "is_subscription": self._safe_get(data, "is_subscription", False),
            "subscription_frequency": self._safe_get(data, "subscription_frequency"),
            "next_renewal_date": self._safe_get(data, "next_renewal_date"),
            "is_automatic_payment": self._safe_get(data, "is_automatic_payment", False),
            "total_amount": self._safe_get(data, "total_amount", self._safe_get(data, "amount")),
            "base_amount": self._safe_get(data, "base_amount"),
            "tax_amount": self._safe_get(data, "tax_amount"),
            "discount_amount": self._safe_get(data, "discount_amount"),
            "late_fee_amount": self._safe_get(data, "late_fee_amount"),
            "processing_fee": self._safe_get(data, "processing_fee"),
            "cashback_amount": self._safe_get(data, "cashback_amount"),
            "billing_period_start": self._safe_get(data, "billing_period_start"),
            "billing_period_end": self._safe_get(data, "billing_period_end"),
            "bank_details": bank_details,
            "upi_details": upi_details,
            "card_details": self._safe_get(data, "card_details", {}),
            "subscription_details": self._safe_get(data, "subscription_details", {}),
            "primary_category": "finance",
            "secondary_category": self._safe_get(data, "service_category"),
            "tertiary_category": self._safe_get(data, "merchant_category"),
            "confidence_score": self._safe_get(data, "confidence_score", 0.8),
            "extraction_confidence": self._safe_get(data, "extraction_confidence", 0.95),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        return structured_data

# Global worker instance
email_worker = EmailWorker()

async def queue_email_processing(user_id: str, email_ids: List[str]):
    """Queue emails for background processing."""
    try:
        logger.info(f"Queueing {len(email_ids)} emails for processing")
        
        # Process in batches directly without using email_queue collection
        # to avoid duplicate key errors with the unique index
        batch_size = settings.email_batch_size
        for i in range(0, len(email_ids), batch_size):
            batch = email_ids[i:i + batch_size]
            
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