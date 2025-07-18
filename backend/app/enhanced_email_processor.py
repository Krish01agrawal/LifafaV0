"""
Enhanced Email Processor
========================

Comprehensive email processing system that implements the enhanced database architecture
with detailed categorization, extraction, and storage for all email types.
"""

import asyncio
import json
import logging
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# Database
from .db import (
    financial_transactions_collection, categorized_emails_collection, 
    email_logs_collection, emails_collection, subscriptions_collection,
    travel_bookings_collection, job_communications_collection,
    promotional_emails_collection, email_queue_collection,
    extraction_failures_collection, query_logs_collection,
    user_analytics_collection, chats_collection, users_collection,
    user_sessions_collection
)

# Models
from .models.financial import (
    User, UserSession, EmailLog, Email, CategorizedEmail, FinancialTransaction,
    Subscription, TravelBooking, JobCommunication, PromotionalEmail,
    EmailQueue, ExtractionFailure, QueryLog, UserAnalytics, Chat,
    TransactionType, PaymentMethod, PaymentStatus, ServiceCategory,
    EmailCategory, SyncStatus, CategorizationStatus, QueueStatus, Priority
)

# Services
from .services.llm_service import LLMService
from .advanced_financial_extractor import AdvancedFinancialExtractor
from .intelligent_batch_categorizer import IntelligentBatchCategorizer

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result of email processing"""
    email_id: str
    user_id: str
    success: bool
    category: Optional[str] = None
    subcategory: Optional[str] = None
    confidence: float = 0.0
    extracted_data: Optional[Dict[str, Any]] = None
    processing_time_ms: int = 0
    error: Optional[str] = None
    stored_collections: List[str] = None

class EnhancedEmailProcessor:
    """Enhanced email processor with comprehensive categorization and storage"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.financial_extractor = AdvancedFinancialExtractor()
        self.batch_categorizer = IntelligentBatchCategorizer()
        
        # Enhanced merchant patterns
        self.merchant_patterns = {
            # Food Delivery
            "blinkit": {
                "canonical_name": "Blinkit",
                "category": "food_delivery",
                "subcategory": "grocery_delivery",
                "patterns": ["blinkit", "blinkitjkb"],
                "is_subscription": False,
                "confidence": 0.95
            },
            "grofers": {
                "canonical_name": "Grofers",
                "category": "food_delivery", 
                "subcategory": "grocery_delivery",
                "patterns": ["grofers", "grofersindia"],
                "is_subscription": False,
                "confidence": 0.95
            },
            "swiggy": {
                "canonical_name": "Swiggy",
                "category": "food_delivery",
                "subcategory": "food_delivery",
                "patterns": ["swiggy"],
                "is_subscription": False,
                "confidence": 0.95
            },
            "zomato": {
                "canonical_name": "Zomato", 
                "category": "food_delivery",
                "subcategory": "food_delivery",
                "patterns": ["zomato"],
                "is_subscription": False,
                "confidence": 0.95
            },
            
            # Streaming Services
            "netflix": {
                "canonical_name": "Netflix",
                "category": "streaming_services",
                "subcategory": "video_streaming",
                "patterns": ["netflix", "netflixupi"],
                "is_subscription": True,
                "confidence": 0.98
            },
            "prime": {
                "canonical_name": "Amazon Prime",
                "category": "streaming_services",
                "subcategory": "video_streaming",
                "patterns": ["prime", "amazon prime"],
                "is_subscription": True,
                "confidence": 0.98
            },
            "hotstar": {
                "canonical_name": "Disney+ Hotstar",
                "category": "streaming_services",
                "subcategory": "video_streaming",
                "patterns": ["hotstar", "disney"],
                "is_subscription": True,
                "confidence": 0.98
            },
            "spotify": {
                "canonical_name": "Spotify",
                "category": "streaming_services",
                "subcategory": "music_streaming",
                "patterns": ["spotify"],
                "is_subscription": True,
                "confidence": 0.98
            },
            
            # E-commerce
            "amazon": {
                "canonical_name": "Amazon",
                "category": "ecommerce",
                "subcategory": "online_shopping",
                "patterns": ["amazon"],
                "is_subscription": False,
                "confidence": 0.95
            },
            "flipkart": {
                "canonical_name": "Flipkart",
                "category": "ecommerce",
                "subcategory": "online_shopping",
                "patterns": ["flipkart"],
                "is_subscription": False,
                "confidence": 0.95
            },
            "myntra": {
                "canonical_name": "Myntra",
                "category": "ecommerce",
                "subcategory": "fashion_shopping",
                "patterns": ["myntra"],
                "is_subscription": False,
                "confidence": 0.95
            },
            
            # Financial Services
            "cred": {
                "canonical_name": "CRED",
                "category": "financial_services",
                "subcategory": "credit_card_bills",
                "patterns": ["cred", "cred.club"],
                "is_subscription": False,
                "confidence": 0.95
            },
            "paytm": {
                "canonical_name": "Paytm",
                "category": "financial_services",
                "subcategory": "digital_wallet",
                "patterns": ["paytm"],
                "is_subscription": False,
                "confidence": 0.95
            },
            
            # Banks
            "hdfc": {
                "canonical_name": "HDFC Bank",
                "category": "banking",
                "subcategory": "bank_alerts",
                "patterns": ["hdfc", "hdfcbank"],
                "is_subscription": False,
                "confidence": 0.98
            },
            "idfc": {
                "canonical_name": "IDFC First Bank",
                "category": "banking",
                "subcategory": "bank_alerts",
                "patterns": ["idfc", "idfcfirstbank"],
                "is_subscription": False,
                "confidence": 0.98
            },
            "icici": {
                "canonical_name": "ICICI Bank",
                "category": "banking",
                "subcategory": "bank_alerts",
                "patterns": ["icici", "icicibank"],
                "is_subscription": False,
                "confidence": 0.98
            },
            "sbi": {
                "canonical_name": "State Bank of India",
                "category": "banking",
                "subcategory": "bank_alerts",
                "patterns": ["sbi", "state bank"],
                "is_subscription": False,
                "confidence": 0.98
            }
        }
        
        # Bank sender patterns
        self.bank_senders = {
            "alerts@hdfcbank.net": "HDFC Bank",
            "transaction.alerts@idfcfirstbank.com": "IDFC First Bank",
            "alerts@icicibank.com": "ICICI Bank",
            "alerts@sbi.co.in": "State Bank of India"
        }
    
    async def process_email_comprehensive(self, email_data: Dict[str, Any], user_id: str) -> ProcessingResult:
        """Process email with comprehensive categorization and storage"""
        start_time = datetime.now()
        email_id = email_data.get('id') or email_data.get('email_id')
        
        try:
            logger.info(f"🔄 Processing email {email_id} with enhanced processor")
            
            # 1. Store in email_logs collection
            await self._store_email_log(email_data, user_id)
            
            # 2. Categorize email
            categorization_result = await self._categorize_email(email_data, user_id)
            
            # 3. Store in categorized_emails collection
            await self._store_categorized_email(email_data, user_id, categorization_result)
            
            # 4. Extract detailed data based on category
            extracted_data = None
            stored_collections = ["email_logs", "categorized_emails"]
            
            if categorization_result.get('primary_category') in ['finance', 'subscription', 'travel', 'job', 'promotion']:
                extracted_data = await self._extract_detailed_data(email_data, user_id, categorization_result)
                
                # 5. Store in specialized collections
                if extracted_data:
                    await self._store_specialized_data(email_data, user_id, categorization_result, extracted_data)
                    stored_collections.extend(extracted_data.get('stored_collections', []))
            
            # 6. Update user analytics
            await self._update_user_analytics(user_id, categorization_result, extracted_data)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ProcessingResult(
                email_id=email_id,
                user_id=user_id,
                success=True,
                category=categorization_result.get('primary_category'),
                subcategory=categorization_result.get('subcategory'),
                confidence=categorization_result.get('confidence', 0.0),
                extracted_data=extracted_data,
                processing_time_ms=int(processing_time),
                stored_collections=stored_collections
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"❌ Error processing email {email_id}: {e}")
            
            # Store failure
            await self._store_extraction_failure(email_id, user_id, str(e))
            
            return ProcessingResult(
                email_id=email_id,
                user_id=user_id,
                success=False,
                processing_time_ms=int(processing_time),
                error=str(e),
                stored_collections=["email_logs", "extraction_failures"]
            )
    
    async def _store_email_log(self, email_data: Dict[str, Any], user_id: str):
        """Store email in email_logs collection"""
        try:
            email_log = EmailLog(
                id=email_data.get('id'),
                email_id=email_data.get('email_id'),
                user_id=user_id,
                gmail_id=email_data.get('gmail_id'),
                thread_id=email_data.get('thread_id'),
                subject=email_data.get('subject', ''),
                from_=email_data.get('from', ''),
                to=email_data.get('to', ''),
                cc=email_data.get('cc', []),
                bcc=email_data.get('bcc', []),
                snippet=email_data.get('snippet', ''),
                body=email_data.get('body'),
                body_plain=email_data.get('body_plain'),
                body_html=email_data.get('body_html'),
                received_date=email_data.get('received_date') or email_data.get('date'),
                sent_date=email_data.get('sent_date'),
                labels=email_data.get('labels', []),
                is_read=email_data.get('is_read', False),
                is_starred=email_data.get('is_starred', False),
                is_important=email_data.get('is_important', False),
                is_spam=email_data.get('is_spam', False),
                is_trash=email_data.get('is_trash', False),
                size_estimate=email_data.get('size_estimate'),
                history_id=email_data.get('history_id'),
                raw_data=email_data.get('raw_data', {}),
                attachments=email_data.get('attachments', []),
                classification_status="pending",
                email_category=None,
                importance_score=email_data.get('importance_score', 5.0),
                financial=email_data.get('financial', False),
                sender_domain=email_data.get('sender_domain'),
                extraction_attempts=0
            )
            
            # Generate hashes
            email_log.generate_hashes()
            
            # Store in database
            await email_logs_collection.update_one(
                {'user_id': user_id, 'gmail_id': email_log.gmail_id},
                {'$set': email_log.dict()},
                upsert=True
            )
            
            logger.info(f"✅ Stored email log for {email_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing email log: {e}")
            raise
    
    async def _categorize_email(self, email_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Categorize email using LLM and pattern matching"""
        try:
            subject = email_data.get('subject', '')
            snippet = email_data.get('snippet', '')
            sender = email_data.get('from', '')
            
            # Check merchant patterns first
            for merchant_name, pattern in self.merchant_patterns.items():
                for pattern_text in pattern['patterns']:
                    if pattern_text.lower() in subject.lower() or pattern_text.lower() in snippet.lower():
                        return {
                            'primary_category': pattern['category'],
                            'secondary_category': pattern['subcategory'],
                            'subcategory': pattern['subcategory'],
                            'merchant_detected': pattern['canonical_name'],
                            'merchant_confidence': pattern['confidence'],
                            'confidence': pattern['confidence'],
                            'transaction_likely': True,
                            'is_subscription': pattern['is_subscription']
                        }
            
            # Check bank patterns
            for bank_sender, bank_name in self.bank_senders.items():
                if bank_sender.lower() in sender.lower():
                    return {
                        'primary_category': 'banking',
                        'secondary_category': 'bank_alerts',
                        'subcategory': 'bank_alerts',
                        'merchant_detected': bank_name,
                        'merchant_confidence': 0.95,
                        'confidence': 0.95,
                        'transaction_likely': True,
                        'is_subscription': False
                    }
            
            # Use LLM for categorization
            category = await self.llm_service.classify_email(subject, snippet)
            
            return {
                'primary_category': category,
                'secondary_category': None,
                'subcategory': None,
                'merchant_detected': None,
                'merchant_confidence': 0.5,
                'confidence': 0.7,
                'transaction_likely': category in ['finance', 'subscription', 'travel', 'job', 'promotion'],
                'is_subscription': category == 'subscription'
            }
            
        except Exception as e:
            logger.error(f"❌ Error categorizing email: {e}")
            return {
                'primary_category': 'other',
                'secondary_category': None,
                'subcategory': None,
                'merchant_detected': None,
                'merchant_confidence': 0.0,
                'confidence': 0.0,
                'transaction_likely': False,
                'is_subscription': False
            }
    
    async def _store_categorized_email(self, email_data: Dict[str, Any], user_id: str, categorization_result: Dict[str, Any]):
        """Store categorized email"""
        try:
            email_id = email_data.get('id') or email_data.get('email_id')
            
            categorized_email = CategorizedEmail(
                user_id=user_id,
                email_id=email_id,
                primary_category=categorization_result.get('primary_category', 'other'),
                secondary_category=categorization_result.get('secondary_category'),
                tertiary_category=categorization_result.get('tertiary_category'),
                subcategory=categorization_result.get('subcategory'),
                confidence=categorization_result.get('confidence', 0.0),
                key_indicators=self._generate_key_indicators(email_data, categorization_result),
                merchant_detected=categorization_result.get('merchant_detected'),
                merchant_confidence=categorization_result.get('merchant_confidence'),
                transaction_likely=categorization_result.get('transaction_likely', False),
                priority=self._calculate_priority(email_data, categorization_result),
                importance_score=email_data.get('importance_score', 5.0),
                urgency_level=self._calculate_urgency_level(email_data),
                requires_action=False,
                original_email=email_data,
                categorized=True,
                categorized_at=datetime.now(),
                financial_data_extracted=False,
                ai_model_used="gpt-4o"
            )
            
            await categorized_emails_collection.update_one(
                {'user_id': user_id, 'email_id': email_id},
                {'$set': categorized_email.dict()},
                upsert=True
            )
            
            logger.info(f"✅ Stored categorized email for {email_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing categorized email: {e}")
            raise
    
    async def _extract_detailed_data(self, email_data: Dict[str, Any], user_id: str, categorization_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract detailed data based on category"""
        try:
            category = categorization_result.get('primary_category')
            email_id = email_data.get('id') or email_data.get('email_id')
            
            if category == 'finance':
                return await self._extract_financial_data(email_data, user_id)
            elif category == 'subscription':
                return await self._extract_subscription_data(email_data, user_id)
            elif category == 'travel':
                return await self._extract_travel_data(email_data, user_id)
            elif category == 'job':
                return await self._extract_job_data(email_data, user_id)
            elif category == 'promotion':
                return await self._extract_promotional_data(email_data, user_id)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting detailed data: {e}")
            return None
    
    async def _extract_financial_data(self, email_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Extract financial transaction data"""
        try:
            # Use the advanced financial extractor
            extracted_data = await self.financial_extractor.extract_single_transaction(
                email_data, email_data, user_id
            )
            
            if extracted_data:
                return {
                    'type': 'financial_transaction',
                    'data': extracted_data,
                    'stored_collections': ['financial_transactions']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting financial data: {e}")
            return None
    
    async def _extract_subscription_data(self, email_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Extract subscription data"""
        try:
            # Use LLM service to extract subscription data
            subject = email_data.get('subject', '')
            snippet = email_data.get('snippet', '')
            
            extracted_data = await self.llm_service.extract_subscription_data(subject, snippet)
            
            if extracted_data:
                return {
                    'type': 'subscription',
                    'data': extracted_data,
                    'stored_collections': ['subscriptions']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting subscription data: {e}")
            return None
    
    async def _extract_travel_data(self, email_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Extract travel booking data"""
        try:
            subject = email_data.get('subject', '')
            snippet = email_data.get('snippet', '')
            
            extracted_data = await self.llm_service.extract_travel_data(subject, snippet)
            
            if extracted_data:
                return {
                    'type': 'travel_booking',
                    'data': extracted_data,
                    'stored_collections': ['travel_bookings']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting travel data: {e}")
            return None
    
    async def _extract_job_data(self, email_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Extract job communication data"""
        try:
            subject = email_data.get('subject', '')
            snippet = email_data.get('snippet', '')
            
            extracted_data = await self.llm_service.extract_job_data(subject, snippet)
            
            if extracted_data:
                return {
                    'type': 'job_communication',
                    'data': extracted_data,
                    'stored_collections': ['job_communications']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting job data: {e}")
            return None
    
    async def _extract_promotional_data(self, email_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Extract promotional email data"""
        try:
            subject = email_data.get('subject', '')
            snippet = email_data.get('snippet', '')
            
            extracted_data = await self.llm_service.extract_promotional_data(subject, snippet)
            
            if extracted_data:
                return {
                    'type': 'promotional_email',
                    'data': extracted_data,
                    'stored_collections': ['promotional_emails']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting promotional data: {e}")
            return None
    
    async def _store_specialized_data(self, email_data: Dict[str, Any], user_id: str, categorization_result: Dict[str, Any], extracted_data: Dict[str, Any]):
        """Store data in specialized collections"""
        try:
            email_id = email_data.get('id') or email_data.get('email_id')
            data_type = extracted_data.get('type')
            data = extracted_data.get('data', {})
            
            if data_type == 'financial_transaction':
                await self._store_financial_transaction(email_data, user_id, data)
            elif data_type == 'subscription':
                await self._store_subscription(email_data, user_id, data)
            elif data_type == 'travel_booking':
                await self._store_travel_booking(email_data, user_id, data)
            elif data_type == 'job_communication':
                await self._store_job_communication(email_data, user_id, data)
            elif data_type == 'promotional_email':
                await self._store_promotional_email(email_data, user_id, data)
            
            # Update categorized email to mark as extracted
            await categorized_emails_collection.update_one(
                {'user_id': user_id, 'email_id': email_id},
                {
                    '$set': {
                        'financial_data_extracted': True,
                        'extracted_at': datetime.now()
                    }
                }
            )
            
            logger.info(f"✅ Stored specialized data for {email_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing specialized data: {e}")
            raise
    
    async def _store_financial_transaction(self, email_data: Dict[str, Any], user_id: str, data: Dict[str, Any]):
        """Store financial transaction"""
        try:
            email_id = email_data.get('id') or email_data.get('email_id')
            
            transaction = FinancialTransaction(
                id=email_id,
                email_id=email_id,
                user_id=user_id,
                date=email_data.get('received_date') or email_data.get('date'),
                amount=data.get('amount', 0.0),
                currency=data.get('currency', 'INR'),
                transaction_type=data.get('transaction_type', TransactionType.PAYMENT),
                transaction_subtype=data.get('transaction_subtype'),
                merchant=data.get('merchant_canonical', ''),
                merchant_canonical=data.get('merchant_canonical', ''),
                merchant_original=data.get('merchant_original'),
                merchant_patterns=data.get('merchant_patterns', []),
                description=data.get('description', ''),
                detailed_description=data.get('detailed_description'),
                payment_method=data.get('payment_method', PaymentMethod.UNKNOWN),
                payment_submethod=data.get('payment_submethod'),
                account_info=data.get('account_info'),
                transaction_id=data.get('transaction_id'),
                transaction_reference=data.get('transaction_reference'),
                invoice_number=data.get('invoice_number'),
                order_id=data.get('order_id'),
                receipt_number=data.get('receipt_number'),
                sender=email_data.get('from', ''),
                subject=email_data.get('subject', ''),
                snippet=email_data.get('snippet', ''),
                email_body_hash=data.get('email_body_hash'),
                email_received_date=email_data.get('received_date') or email_data.get('date'),
                service_category=data.get('service_category', ServiceCategory.OTHER),
                service_subcategory=data.get('service_subcategory'),
                service_name=data.get('service_name'),
                service_provider=data.get('service_provider'),
                payment_status=data.get('payment_status', PaymentStatus.COMPLETED),
                payment_flow=data.get('payment_flow', 'outgoing'),
                is_automatic_payment=data.get('is_automatic_payment', False),
                is_recurring=data.get('is_recurring', False),
                requires_action=data.get('requires_action', False),
                total_amount=data.get('total_amount', data.get('amount', 0.0)),
                base_amount=data.get('base_amount'),
                tax_amount=data.get('tax_amount'),
                discount_amount=data.get('discount_amount'),
                late_fee_amount=data.get('late_fee_amount'),
                processing_fee=data.get('processing_fee'),
                cashback_amount=data.get('cashback_amount'),
                convenience_fee=data.get('convenience_fee'),
                delivery_fee=data.get('delivery_fee'),
                tip_amount=data.get('tip_amount'),
                transaction_date=data.get('transaction_date'),
                due_date=data.get('due_date'),
                service_period_start=data.get('service_period_start'),
                service_period_end=data.get('service_period_end'),
                billing_period_start=data.get('billing_period_start'),
                billing_period_end=data.get('billing_period_end'),
                clearance_date=data.get('clearance_date'),
                important_invoice_date=data.get('important_invoice_date'),
                bank_details=data.get('bank_details', {}),
                upi_details=data.get('upi_details', {}),
                card_details=data.get('card_details', {}),
                is_subscription=data.get('is_subscription', False),
                subscription_product=data.get('subscription_product'),
                subscription_details=data.get('subscription_details', {}),
                location=data.get('location', {}),
                primary_category=data.get('primary_category', 'finance'),
                secondary_category=data.get('secondary_category'),
                tertiary_category=data.get('tertiary_category'),
                tags=data.get('tags', []),
                confidence_score=data.get('confidence_score', 0.8),
                extraction_confidence=data.get('extraction_confidence', 0.95),
                data_completeness=data.get('data_completeness', 0.90),
                ai_model_used=data.get('ai_model_used'),
                extraction_method=data.get('extraction_method', 'ai_extraction'),
                extracted_at=datetime.now()
            )
            
            await financial_transactions_collection.update_one(
                {'user_id': user_id, 'email_id': email_id},
                {'$set': transaction.dict()},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"❌ Error storing financial transaction: {e}")
            raise
    
    async def _store_subscription(self, email_data: Dict[str, Any], user_id: str, data: Dict[str, Any]):
        """Store subscription data"""
        try:
            email_id = email_data.get('id') or email_data.get('email_id')
            
            subscription = Subscription(
                user_id=user_id,
                email_id=email_id,
                service_name=data.get('service_name', ''),
                service_canonical=data.get('service_canonical', ''),
                service_category=data.get('service_category', ''),
                service_subcategory=data.get('service_subcategory', ''),
                subscription_type=data.get('subscription_type', ''),
                subscription_tier=data.get('subscription_tier', ''),
                amount=data.get('amount', 0.0),
                currency=data.get('currency', 'INR'),
                billing_frequency=data.get('billing_frequency', 'monthly'),
                billing_cycle=data.get('billing_cycle', 'monthly'),
                next_billing_date=data.get('next_billing_date'),
                last_billing_date=data.get('last_billing_date'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                cancellation_date=data.get('cancellation_date'),
                is_automatic_payment=data.get('is_automatic_payment', True),
                payment_method=data.get('payment_method', PaymentMethod.UNKNOWN),
                status=data.get('status', 'active'),
                auto_renewal=data.get('auto_renewal', True),
                trial_period=data.get('trial_period', False),
                trial_end_date=data.get('trial_end_date'),
                merchant_canonical=data.get('merchant_canonical', ''),
                merchant_original=data.get('merchant_original'),
                upi_id=data.get('upi_id'),
                confidence_score=data.get('confidence_score', 0.98),
                detection_reasons=data.get('detection_reasons', []),
                features=data.get('features', [])
            )
            
            await subscriptions_collection.update_one(
                {'user_id': user_id, 'email_id': email_id},
                {'$set': subscription.dict()},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"❌ Error storing subscription: {e}")
            raise
    
    async def _store_travel_booking(self, email_data: Dict[str, Any], user_id: str, data: Dict[str, Any]):
        """Store travel booking data"""
        try:
            email_id = email_data.get('id') or email_data.get('email_id')
            
            travel_booking = TravelBooking(
                user_id=user_id,
                email_id=email_id,
                booking_type=data.get('booking_type', ''),
                service_provider=data.get('service_provider', ''),
                provider_canonical=data.get('provider_canonical', ''),
                booking_reference=data.get('booking_reference', ''),
                pnr_number=data.get('pnr_number'),
                confirmation_number=data.get('confirmation_number'),
                travel_date=data.get('travel_date'),
                return_date=data.get('return_date'),
                booking_date=data.get('booking_date'),
                from_location=data.get('from_location', {}),
                to_location=data.get('to_location', {}),
                passenger_count=data.get('passenger_count', 1),
                passenger_details=data.get('passenger_details', []),
                total_amount=data.get('total_amount', 0.0),
                currency=data.get('currency', 'INR'),
                payment_method=data.get('payment_method', PaymentMethod.UNKNOWN),
                payment_status=data.get('payment_status', PaymentStatus.COMPLETED),
                booking_status=data.get('booking_status', 'confirmed'),
                cancellation_policy=data.get('cancellation_policy'),
                refund_policy=data.get('refund_policy'),
                check_in_time=data.get('check_in_time'),
                check_out_time=data.get('check_out_time'),
                flight_details=data.get('flight_details', {}),
                hotel_details=data.get('hotel_details', {})
            )
            
            await travel_bookings_collection.update_one(
                {'user_id': user_id, 'email_id': email_id},
                {'$set': travel_booking.dict()},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"❌ Error storing travel booking: {e}")
            raise
    
    async def _store_job_communication(self, email_data: Dict[str, Any], user_id: str, data: Dict[str, Any]):
        """Store job communication data"""
        try:
            email_id = email_data.get('id') or email_data.get('email_id')
            
            job_communication = JobCommunication(
                user_id=user_id,
                email_id=email_id,
                communication_type=data.get('communication_type', ''),
                company_name=data.get('company_name', ''),
                company_canonical=data.get('company_canonical', ''),
                position_title=data.get('position_title', ''),
                position_level=data.get('position_level'),
                department=data.get('department'),
                application_status=data.get('application_status', ''),
                interview_stage=data.get('interview_stage'),
                interview_date=data.get('interview_date'),
                interview_type=data.get('interview_type'),
                interview_duration=data.get('interview_duration'),
                salary_offered=data.get('salary_offered'),
                salary_currency=data.get('salary_currency', 'INR'),
                salary_type=data.get('salary_type'),
                location=data.get('location'),
                work_type=data.get('work_type'),
                urgency_level=data.get('urgency_level'),
                requires_response=data.get('requires_response', False),
                response_deadline=data.get('response_deadline'),
                application_id=data.get('application_id'),
                job_id=data.get('job_id'),
                recruiter_name=data.get('recruiter_name'),
                recruiter_email=data.get('recruiter_email'),
                benefits=data.get('benefits', [])
            )
            
            await job_communications_collection.update_one(
                {'user_id': user_id, 'email_id': email_id},
                {'$set': job_communication.dict()},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"❌ Error storing job communication: {e}")
            raise
    
    async def _store_promotional_email(self, email_data: Dict[str, Any], user_id: str, data: Dict[str, Any]):
        """Store promotional email data"""
        try:
            email_id = email_data.get('id') or email_data.get('email_id')
            
            promotional_email = PromotionalEmail(
                user_id=user_id,
                email_id=email_id,
                promotion_type=data.get('promotion_type', ''),
                discount_amount=data.get('discount_amount'),
                discount_percentage=data.get('discount_percentage'),
                original_price=data.get('original_price'),
                discounted_price=data.get('discounted_price'),
                currency=data.get('currency', 'INR'),
                merchant_canonical=data.get('merchant_canonical', ''),
                merchant_name=data.get('merchant_name', ''),
                merchant_category=data.get('merchant_category', ''),
                offer_category=data.get('offer_category', ''),
                promotion_code=data.get('promotion_code'),
                valid_from=data.get('valid_from'),
                valid_until=data.get('valid_until'),
                minimum_purchase=data.get('minimum_purchase'),
                maximum_discount=data.get('maximum_discount'),
                terms_conditions=data.get('terms_conditions'),
                is_expired=data.get('is_expired', False),
                is_used=data.get('is_used', False),
                usage_limit=data.get('usage_limit'),
                usage_count=data.get('usage_count', 0),
                offer_highlights=data.get('offer_highlights', []),
                target_audience=data.get('target_audience'),
                exclusions=data.get('exclusions', []),
                delivery_info=data.get('delivery_info'),
                payment_options=data.get('payment_options', []),
                cashback_details=data.get('cashback_details'),
                referral_details=data.get('referral_details'),
                extraction_confidence=data.get('extraction_confidence', 0.94)
            )
            
            await promotional_emails_collection.update_one(
                {'user_id': user_id, 'email_id': email_id},
                {'$set': promotional_email.dict()},
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"❌ Error storing promotional email: {e}")
            raise
    
    async def _store_extraction_failure(self, email_id: str, user_id: str, error_message: str):
        """Store extraction failure"""
        try:
            failure = ExtractionFailure(
                email_id=email_id,
                user_id=user_id,
                failure_type="processing",
                failure_stage="extraction",
                error_message=error_message,
                error_code="EXTRACTION_FAILED",
                email_data={},
                attempts=1,
                max_attempts=3,
                is_resolved=False,
                ai_model_used="gpt-4o",
                processing_time_ms=0
            )
            
            await extraction_failures_collection.insert_one(failure.dict())
            
        except Exception as e:
            logger.error(f"❌ Error storing extraction failure: {e}")
    
    async def _update_user_analytics(self, user_id: str, categorization_result: Dict[str, Any], extracted_data: Optional[Dict[str, Any]]):
        """Update user analytics"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get existing analytics or create new
            existing_analytics = await user_analytics_collection.find_one({
                'user_id': user_id,
                'date': today
            })
            
            if existing_analytics:
                # Update existing analytics
                update_data = {
                    'emails_categorized': existing_analytics.get('emails_categorized', 0) + 1
                }
                
                if extracted_data:
                    data_type = extracted_data.get('type')
                    if data_type == 'financial_transaction':
                        update_data['financial_transactions'] = existing_analytics.get('financial_transactions', 0) + 1
                    elif data_type == 'subscription':
                        update_data['subscriptions'] = existing_analytics.get('subscriptions', 0) + 1
                    elif data_type == 'travel_booking':
                        update_data['travel_bookings'] = existing_analytics.get('travel_bookings', 0) + 1
                    elif data_type == 'job_communication':
                        update_data['job_communications'] = existing_analytics.get('job_communications', 0) + 1
                    elif data_type == 'promotional_email':
                        update_data['promotional_emails'] = existing_analytics.get('promotional_emails', 0) + 1
                
                await user_analytics_collection.update_one(
                    {'user_id': user_id, 'date': today},
                    {'$set': update_data}
                )
            else:
                # Create new analytics entry
                analytics = UserAnalytics(
                    user_id=user_id,
                    date=today,
                    emails_categorized=1,
                    emails_extracted=1 if extracted_data else 0,
                    financial_transactions=1 if extracted_data and extracted_data.get('type') == 'financial_transaction' else 0,
                    subscriptions=1 if extracted_data and extracted_data.get('type') == 'subscription' else 0,
                    travel_bookings=1 if extracted_data and extracted_data.get('type') == 'travel_booking' else 0,
                    job_communications=1 if extracted_data and extracted_data.get('type') == 'job_communication' else 0,
                    promotional_emails=1 if extracted_data and extracted_data.get('type') == 'promotional_email' else 0
                )
                
                await user_analytics_collection.insert_one(analytics.dict())
            
        except Exception as e:
            logger.error(f"❌ Error updating user analytics: {e}")
    
    def _generate_key_indicators(self, email_data: Dict[str, Any], categorization_result: Dict[str, Any]) -> List[str]:
        """Generate key indicators for categorization"""
        indicators = []
        subject = email_data.get('subject', '').lower()
        snippet = email_data.get('snippet', '').lower()
        sender = email_data.get('from', '').lower()
        
        # Add category-specific indicators
        category = categorization_result.get('primary_category')
        if category == 'food_delivery':
            indicators.extend(['food delivery', 'grocery', 'order confirmation'])
        elif category == 'streaming_services':
            indicators.extend(['subscription', 'streaming', 'entertainment'])
        elif category == 'banking':
            indicators.extend(['bank', 'transaction', 'alert'])
        elif category == 'upi_transactions':
            indicators.extend(['upi', 'transaction', 'debit'])
        
        # Add merchant-specific indicators
        if categorization_result.get('merchant_detected'):
            indicators.append(f"merchant: {categorization_result['merchant_detected']}")
        
        return indicators[:5]  # Limit to 5 indicators
    
    def _calculate_priority(self, email_data: Dict[str, Any], categorization_result: Dict[str, Any]) -> Priority:
        """Calculate email priority"""
        subject = email_data.get('subject', '').lower()
        
        # High priority keywords
        high_priority = ['alert', 'urgent', 'important', 'critical', 'failed', 'error']
        for keyword in high_priority:
            if keyword in subject:
                return Priority.HIGH
        
        # Medium priority for financial emails
        if categorization_result.get('primary_category') in ['banking', 'finance', 'subscription']:
            return Priority.MEDIUM
        
        return Priority.LOW
    
    def _calculate_urgency_level(self, email_data: Dict[str, Any]) -> Optional[str]:
        """Calculate urgency level"""
        subject = email_data.get('subject', '').lower()
        
        if any(word in subject for word in ['urgent', 'critical', 'immediate']):
            return 'high'
        elif any(word in subject for word in ['important', 'alert', 'notice']):
            return 'medium'
        else:
            return 'low'

# Global instance
enhanced_processor = EnhancedEmailProcessor() 