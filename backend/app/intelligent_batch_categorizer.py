"""
Intelligent Batch Email Categorization System
============================================

This module implements efficient batch processing for categorizing 10,000+ emails
using the Agno framework with optimized LLM usage and smart batching strategies.

Key Features:
- Batch processing in configurable chunks (50-100 emails per batch)
- Smart categorization using Agno agents
- Efficient LLM usage with context optimization
- Parallel processing for maximum throughput
- Detailed category extraction with confidence scores
- MongoDB integration for persistent storage

Categories:
- Financial (payments, bills, subscriptions, investments)
- Travel (flights, hotels, transport, bookings)
- Job-related (applications, interviews, offers)
- Promotional (offers, discounts, marketing)
- Subscriptions (premium services, recurring payments)
- Shopping (e-commerce, retail, purchases)
- Healthcare (medical, insurance, appointments)
- Education (courses, certifications, learning)
- Entertainment (movies, events, gaming)
- Utilities (electricity, water, gas, internet)
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# OpenAI
import openai
from openai import AsyncOpenAI

# Database
from .db import email_logs_collection, categorized_emails_collection
from .config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
api_key = settings.openai_api_key or settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY', '')
if not api_key:
    logger.warning("⚠️ OpenAI API key not found. Some features may not work.")
    client = None
else:
    client = AsyncOpenAI(api_key=api_key)

class EmailCategory(Enum):
    """Comprehensive email categories"""
    FINANCIAL = "financial"
    TRAVEL = "travel"
    JOB_RELATED = "job_related"
    PROMOTIONAL = "promotional"
    SUBSCRIPTIONS = "subscriptions"
    SHOPPING = "shopping"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    SOCIAL = "social"
    GOVERNMENT = "government"
    INSURANCE = "insurance"
    INVESTMENT = "investment"
    GENERAL = "general"

@dataclass
class BatchCategorizationResult:
    """Result of batch categorization"""
    total_emails: int
    processed_emails: int
    categorized_emails: int
    categories_found: Dict[str, int]
    processing_time: float
    success: bool
    error_message: Optional[str] = None

class IntelligentBatchCategorizer:
    """Main batch categorization system"""
    
    def __init__(self, batch_size: int = 75, max_concurrent_batches: int = 3):
        self.batch_size = batch_size
        self.max_concurrent_batches = max_concurrent_batches
        
    async def categorize_emails_batch(self, user_id: str, limit: Optional[int] = None) -> BatchCategorizationResult:
        """
        Main function to categorize all emails for a user in efficient batches
        """
        start_time = time.time()
        
        try:
            logger.info(f"🚀 Starting batch categorization for user {user_id}")
            
            # Get uncategorized emails from MongoDB
            uncategorized_emails = await self._get_uncategorized_emails(user_id, limit)
            total_emails = len(uncategorized_emails)
            
            if total_emails == 0:
                logger.info(f"✅ No uncategorized emails found for user {user_id}")
                return BatchCategorizationResult(
                    total_emails=0,
                    processed_emails=0,
                    categorized_emails=0,
                    categories_found={},
                    processing_time=0.0,
                    success=True
                )
            
            logger.info(f"📊 Found {total_emails} uncategorized emails to process")
            
            # Create batches
            batches = self._create_batches(uncategorized_emails, self.batch_size)
            logger.info(f"📦 Created {len(batches)} batches of size {self.batch_size}")
            
            # Process batches with concurrency control
            categorized_emails = []
            processed_count = 0
            categories_count = {}
            
            # Use semaphore to limit concurrent batches
            semaphore = asyncio.Semaphore(self.max_concurrent_batches)
            
            async def process_batch_with_semaphore(batch_idx, batch):
                async with semaphore:
                    return await self._process_single_batch(batch_idx, batch, user_id)
            
            # Process all batches concurrently
            batch_tasks = [
                process_batch_with_semaphore(idx, batch) 
                for idx, batch in enumerate(batches)
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Collect results
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"❌ Batch processing error: {result}")
                    continue
                    
                if result and result.get('success', False):
                    batch_categorized = result.get('categorized_emails', [])
                    categorized_emails.extend(batch_categorized)
                    processed_count += result.get('processed_count', 0)
                    
                    # Update category counts
                    for category, count in result.get('categories_count', {}).items():
                        categories_count[category] = categories_count.get(category, 0) + count
            
            # Store categorized emails in MongoDB
            if categorized_emails:
                await self._store_categorized_emails(categorized_emails)
                logger.info(f"💾 Stored {len(categorized_emails)} categorized emails")
            
            processing_time = time.time() - start_time
            
            logger.info(f"✅ Batch categorization completed:")
            logger.info(f"   📊 Total emails: {total_emails}")
            logger.info(f"   ✅ Processed: {processed_count}")
            logger.info(f"   📂 Categorized: {len(categorized_emails)}")
            logger.info(f"   ⏱️ Processing time: {processing_time:.2f}s")
            logger.info(f"   📈 Categories found: {categories_count}")
            
            return BatchCategorizationResult(
                total_emails=total_emails,
                processed_emails=processed_count,
                categorized_emails=len(categorized_emails),
                categories_found=categories_count,
                processing_time=processing_time,
                success=True
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Batch categorization failed: {e}")
            return BatchCategorizationResult(
                total_emails=0,
                processed_emails=0,
                categorized_emails=0,
                categories_found={},
                processing_time=processing_time,
                success=False,
                error_message=str(e)
            )

    async def _get_uncategorized_emails(self, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get uncategorized emails from MongoDB"""
        try:
            # Find emails that haven't been categorized yet
            query = {
                "user_id": user_id,
                "categorized": {"$ne": True}
            }
            
            if limit:
                cursor = email_logs_collection.find(query).limit(limit)
            else:
                cursor = email_logs_collection.find(query)
            
            emails = await cursor.to_list(length=None)
            logger.info(f"📧 Retrieved {len(emails)} uncategorized emails for user {user_id}")
            return emails
            
        except Exception as e:
            logger.error(f"❌ Error retrieving uncategorized emails: {e}")
            return []

    def _create_batches(self, emails: List[Dict], batch_size: int) -> List[List[Dict]]:
        """Create batches of emails for processing"""
        return [emails[i:i + batch_size] for i in range(0, len(emails), batch_size)]

    async def _process_single_batch(self, batch_idx: int, batch: List[Dict], user_id: str) -> Dict:
        """Process a single batch of emails using OpenAI"""
        try:
            logger.info(f"🔄 Processing batch {batch_idx + 1} with {len(batch)} emails")
            
            # Create prompt for the batch
            prompt = self._create_batch_prompt(batch)
            
            # Call OpenAI API
            if not client:
                logger.error("❌ OpenAI client not initialized. Cannot process batch.")
                return {
                    'success': False,
                    'error': 'OpenAI API key not configured',
                    'categorized_emails': [],
                    'processed_count': 0,
                    'categories_count': {}
                }
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert email categorization agent. Your task is to analyze email subjects and content
                        to classify them into specific categories with high accuracy and confidence.
                        
                        CATEGORIES TO USE:
                        1. financial - Bills, payments, bank statements, credit cards, loans, taxes
                        2. travel - Flights, hotels, trains, buses, travel bookings, itineraries
                        3. job_related - Job applications, interviews, career opportunities, professional networking
                        4. promotional - Marketing emails, offers, discounts, sales, advertisements
                        5. subscriptions - Recurring services, premium memberships, software subscriptions
                        6. shopping - E-commerce, retail purchases, order confirmations, delivery updates
                        7. healthcare - Medical appointments, insurance, health services, pharmacy
                        8. education - Courses, certifications, learning platforms, academic institutions
                        9. entertainment - Movies, events, gaming, streaming services, tickets
                        10. utilities - Electricity, water, gas, internet, telecom bills
                        11. social - Social media, dating apps, community platforms, messaging
                        12. government - Tax, legal, official documents, civic services
                        13. insurance - Life, health, vehicle, property insurance
                        14. investment - Stocks, mutual funds, SIPs, trading, portfolio updates
                        15. general - Everything else that doesn't fit above categories
                        
                        RESPONSE FORMAT:
                        For each email, respond with JSON object:
                        {
                            "email_id": "email_unique_id",
                            "category": "category_name",
                            "confidence": 0.95,
                            "subcategory": "specific_subcategory",
                            "key_indicators": ["indicator1", "indicator2"],
                            "merchant_detected": "merchant_name_if_applicable",
                            "transaction_likely": true/false,
                            "priority": "high|medium|low"
                        }
                        
                        PROCESSING RULES:
                        - Analyze subject line and email content
                        - Look for merchant names, transaction indicators, service providers
                        - Assign confidence score (0.0 to 1.0)
                        - Identify if email likely contains transaction data
                        - Categorize based on primary purpose, not sender domain
                        - For financial emails, detect merchant/service provider names
                        - Use 'general' only when no other category fits
                        
                        RESPOND WITH VALID JSON ARRAY containing one object per email."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            # Parse the response
            response_content = response.choices[0].message.content
            categorized_emails = self._parse_categorization_response(response_content, batch, user_id)
            
            # Count categories
            categories_count = {}
            for email in categorized_emails:
                category = email.get('category', 'unknown')
                categories_count[category] = categories_count.get(category, 0) + 1
            
            logger.info(f"✅ Batch {batch_idx + 1} processed successfully: {len(categorized_emails)} categorized")
            
            return {
                'success': True,
                'categorized_emails': categorized_emails,
                'processed_count': len(batch),
                'categories_count': categories_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing batch {batch_idx + 1}: {e}")
            return {
                'success': False,
                'error': str(e),
                'categorized_emails': [],
                'processed_count': 0,
                'categories_count': {}
            }

    def _create_batch_prompt(self, batch: List[Dict]) -> str:
        """Create a prompt for batch processing"""
        prompt = "Please categorize the following emails:\n\n"
        
        for email in batch:
            email_id = email.get('id', email.get('_id', 'unknown'))
            subject = email.get('subject', 'No subject')
            sender = email.get('from', 'Unknown sender')
            content_preview = email.get('content', '')[:200] + "..." if len(email.get('content', '')) > 200 else email.get('content', '')
            
            prompt += f"EMAIL ID: {email_id}\n"
            prompt += f"FROM: {sender}\n"
            prompt += f"SUBJECT: {subject}\n"
            prompt += f"CONTENT: {content_preview}\n"
            prompt += "---\n"
        
        prompt += "\nPlease respond with a JSON array containing categorization results for each email."
        return prompt

    def _parse_categorization_response(self, response: str, batch: List[Dict], user_id: str) -> List[Dict]:
        """Parse the OpenAI response and create categorized email objects"""
        try:
            # Extract JSON from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON array found in response")
                return []
            
            json_str = response[json_start:json_end]
            categorization_results = json.loads(json_str)
            
            categorized_emails = []
            
            for result in categorization_results:
                email_id = result.get('email_id')
                
                # Find the original email in the batch
                original_email = next((email for email in batch if str(email.get('id', email.get('_id'))) == str(email_id)), None)
                
                if original_email:
                    categorized_email = {
                        'user_id': user_id,
                        'email_id': email_id,
                        'original_email': original_email,
                        'category': result.get('category', 'general'),
                        'confidence': result.get('confidence', 0.5),
                        'subcategory': result.get('subcategory', ''),
                        'key_indicators': result.get('key_indicators', []),
                        'merchant_detected': result.get('merchant_detected', ''),
                        'transaction_likely': result.get('transaction_likely', False),
                        'priority': result.get('priority', 'medium'),
                        'categorized_at': datetime.utcnow(),
                        'categorized': True
                    }
                    categorized_emails.append(categorized_email)
            
            return categorized_emails
            
        except Exception as e:
            logger.error(f"❌ Error parsing categorization response: {e}")
            return []

    async def _store_categorized_emails(self, categorized_emails: List[Dict]) -> None:
        """Store categorized emails in MongoDB"""
        try:
            if categorized_emails:
                # Insert into categorized_emails collection
                await categorized_emails_collection.insert_many(categorized_emails)
                
                # Update original emails to mark as categorized
                email_ids = [email['email_id'] for email in categorized_emails]
                await email_logs_collection.update_many(
                    {"id": {"$in": email_ids}},
                    {"$set": {"categorized": True, "categorized_at": datetime.utcnow()}}
                )
                
                logger.info(f"💾 Successfully stored {len(categorized_emails)} categorized emails")
                
        except Exception as e:
            logger.error(f"❌ Error storing categorized emails: {e}")

# Convenience functions
async def start_batch_categorization(user_id: str, limit: Optional[int] = None) -> BatchCategorizationResult:
    """Start batch categorization for a user"""
    categorizer = IntelligentBatchCategorizer()
    return await categorizer.categorize_emails_batch(user_id, limit)

async def get_categorization_status(user_id: str) -> Dict[str, Any]:
    """Get categorization status for a user"""
    try:
        # Use classification_status to determine progress instead of deprecated 'categorized' flag
        total_emails = await email_logs_collection.count_documents({"user_id": user_id})

        categorized_emails = await email_logs_collection.count_documents({
            "user_id": user_id,
            "classification_status": {"$in": ["classified", "extracted"]}
        })
        # Fallback to old flag to preserve compatibility for legacy data
        if categorized_emails == 0:
            categorized_emails = await email_logs_collection.count_documents({
                "user_id": user_id,
                "categorized": True
            })
        
        return {
            "user_id": user_id,
            "total_emails": total_emails,
            "categorized_emails": categorized_emails,
            "uncategorized_emails": total_emails - categorized_emails,
            "categorization_percentage": (categorized_emails / total_emails * 100) if total_emails > 0 else 0
        }
    except Exception as e:
        logger.error(f"❌ Error getting categorization status: {e}")
        return {"error": str(e)} 