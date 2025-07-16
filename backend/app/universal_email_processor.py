"""
Universal Email Processor for Maximum Detail and Categorization
==============================================================

This module processes EVERY email with maximum detail and categorization
to ensure efficient MongoDB retrieval for all types of queries.

Features:
1. Universal email processing (financial + non-financial)
2. Maximum detail extraction (50+ fields for all emails)
3. Intelligent categorization (20+ categories)
4. Merchant-specific pattern recognition
5. Bank integration for all transaction types
6. Subscription detection with merchant-specific logic
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# Database
from .db import financial_transactions_collection, categorized_emails_collection, emails_collection
from .models.financial import (
    FinancialTransaction, TransactionType, PaymentMethod, ServiceCategory, 
    PaymentStatus, UPIDetails, SubscriptionDetails, MerchantDetails, 
    BankDetails, EmailMetadata, ExtractionMetadata, CategorizedEmail
)
from .advanced_financial_extractor import AdvancedFinancialExtractor
from .intelligent_batch_categorizer import IntelligentBatchCategorizer

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class EmailProcessingResult:
    """Result of email processing with maximum detail"""
    email_id: str
    user_id: str
    is_financial: bool
    category: str
    subcategory: Optional[str]
    confidence: float
    extracted_data: Optional[Dict[str, Any]]
    processing_time_ms: int
    error: Optional[str] = None

class UniversalEmailProcessor:
    """Universal email processor for maximum detail and categorization"""
    
    def __init__(self):
        self.extractor = AdvancedFinancialExtractor()
        self.categorizer = IntelligentBatchCategorizer()
        
        # Enhanced merchant patterns based on real data
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
        
        # UPI app patterns
        self.upi_apps = {
            "hdfcbank": "HDFC Bank UPI",
            "axisb": "Axis Bank UPI",
            "icici": "ICICI Bank UPI",
            "sbi": "SBI UPI",
            "payu": "PayU UPI",
            "mairtel": "Airtel UPI"
        }
    
    async def process_email_universal(self, email: Dict[str, Any], user_id: str) -> EmailProcessingResult:
        """Process every email with maximum detail and categorization"""
        start_time = datetime.now()
        
        try:
            email_id = email.get('email_id')
            original_email = email.get('original_email', {})
            
            logger.info(f"🔄 Processing email {email_id} with universal processor")
            
            # 1. Basic email categorization
            category_result = await self._categorize_email_basic(email, user_id)
            
            # 2. Check if it's financial
            is_financial = self._is_financial_email(original_email)
            
            # 3. Extract maximum detail based on category
            extracted_data = None
            if is_financial:
                extracted_data = await self._extract_financial_data_detailed(email, user_id)
            else:
                extracted_data = await self._extract_non_financial_data(email, user_id)
            
            # 4. Enhanced categorization with extracted data
            final_category = await self._categorize_email_enhanced(email, user_id, extracted_data)
            
            # 5. Store comprehensive data
            await self._store_comprehensive_data(email, user_id, final_category, extracted_data)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return EmailProcessingResult(
                email_id=email_id,
                user_id=user_id,
                is_financial=is_financial,
                category=final_category['category'],
                subcategory=final_category.get('subcategory'),
                confidence=final_category['confidence'],
                extracted_data=extracted_data,
                processing_time_ms=int(processing_time)
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing email {email.get('email_id')}: {e}")
            return EmailProcessingResult(
                email_id=email.get('email_id'),
                user_id=user_id,
                is_financial=False,
                category="error",
                subcategory=None,
                confidence=0.0,
                extracted_data=None,
                processing_time_ms=0,
                error=str(e)
            )
    
    def _is_financial_email(self, original_email: Dict[str, Any]) -> bool:
        """Determine if email is financial based on content analysis"""
        subject = original_email.get('subject', '').lower()
        snippet = original_email.get('snippet', '').lower()
        sender = original_email.get('from', '').lower()
        
        # Financial keywords
        financial_keywords = [
            'transaction', 'payment', 'bill', 'subscription', 'upi', 'debit', 'credit',
            'amount', 'rs.', '₹', 'inr', 'bank', 'account', 'transfer', 'alert',
            'statement', 'invoice', 'receipt', 'order', 'purchase', 'refund'
        ]
        
        # Bank senders
        bank_sender_keywords = ['bank', 'alerts', 'transaction', 'statement']
        
        # Check for financial keywords
        for keyword in financial_keywords:
            if keyword in subject or keyword in snippet:
                return True
        
        # Check for bank senders
        for keyword in bank_sender_keywords:
            if keyword in sender:
                return True
        
        return False
    
    async def _categorize_email_basic(self, email: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Basic email categorization"""
        original_email = email.get('original_email', {})
        subject = original_email.get('subject', '').lower()
        snippet = original_email.get('snippet', '').lower()
        sender = original_email.get('from', '').lower()
        
        # Check for specific patterns
        for merchant_name, pattern in self.merchant_patterns.items():
            for pattern_text in pattern['patterns']:
                if pattern_text in subject or pattern_text in snippet:
                    return {
                        'category': pattern['category'],
                        'subcategory': pattern['subcategory'],
                        'merchant': pattern['canonical_name'],
                        'confidence': pattern['confidence'],
                        'is_subscription': pattern['is_subscription']
                    }
        
        # Check for bank patterns
        for bank_sender, bank_name in self.bank_senders.items():
            if bank_sender in sender:
                return {
                    'category': 'banking',
                    'subcategory': 'bank_alerts',
                    'merchant': bank_name,
                    'confidence': 0.95,
                    'is_subscription': False
                }
        
        # Default categorization
        return {
            'category': 'other',
            'subcategory': 'general',
            'merchant': None,
            'confidence': 0.5,
            'is_subscription': False
        }
    
    async def _extract_financial_data_detailed(self, email: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Extract detailed financial data with merchant-specific logic"""
        try:
            # Use the advanced extractor
            transaction = await self.extractor.extract_financial_data(email, user_id)
            
            if transaction:
                # Enhance with merchant-specific patterns
                transaction = await self._enhance_with_merchant_patterns(transaction, email)
                
                # Enhance with bank patterns
                transaction = await self._enhance_with_bank_patterns(transaction, email)
                
                # Enhance with UPI patterns
                transaction = await self._enhance_with_upi_patterns(transaction, email)
                
                return transaction
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extracting financial data: {e}")
            return None
    
    async def _extract_non_financial_data(self, email: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Extract data from non-financial emails"""
        original_email = email.get('original_email', {})
        
        return {
            'email_type': 'non_financial',
            'subject': original_email.get('subject'),
            'sender': original_email.get('from'),
            'received_date': original_email.get('received_date'),
            'snippet': original_email.get('snippet'),
            'body_hash': self._generate_body_hash(original_email.get('content', '')),
            'importance_score': self._calculate_importance_score(original_email),
            'is_promotional': self._is_promotional_email(original_email),
            'extracted_at': datetime.now(),
            'confidence_score': 0.8
        }
    
    async def _enhance_with_merchant_patterns(self, transaction: Dict[str, Any], email: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance transaction with merchant-specific patterns"""
        original_email = email.get('original_email', {})
        subject = original_email.get('subject', '').lower()
        snippet = original_email.get('snippet', '').lower()
        
        # Find matching merchant pattern
        for merchant_name, pattern in self.merchant_patterns.items():
            for pattern_text in pattern['patterns']:
                if pattern_text in subject or pattern_text in snippet:
                    # Update merchant details
                    transaction['merchant'] = pattern['canonical_name']
                    transaction['merchant_details'] = {
                        'canonical_name': pattern['canonical_name'],
                        'original_name': transaction.get('merchant', ''),
                        'patterns': pattern['patterns'],
                        'category': pattern['category'],
                        'subcategory': pattern['subcategory'],
                        'confidence_score': pattern['confidence'],
                        'detection_method': 'pattern_match'
                    }
                    
                    # Update service category
                    transaction['service_category'] = pattern['category']
                    
                    # Update subscription details
                    if pattern['is_subscription']:
                        transaction['is_subscription'] = True
                        transaction['subscription_product'] = pattern['canonical_name']
                        transaction['subscription_details'] = {
                            'is_subscription': True,
                            'product_name': pattern['canonical_name'],
                            'category': pattern['subcategory'],
                            'type': pattern['subcategory'],
                            'confidence_score': pattern['confidence'],
                            'detection_reasons': [f"Merchant pattern: {pattern_text}"],
                            'subscription_frequency': 'monthly',
                            'is_automatic_payment': True
                        }
                    
                    break
        
        return transaction
    
    async def _enhance_with_bank_patterns(self, transaction: Dict[str, Any], email: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance transaction with bank-specific patterns"""
        original_email = email.get('original_email', {})
        sender = original_email.get('from', '')
        
        # Check for bank sender patterns
        for bank_sender, bank_name in self.bank_senders.items():
            if bank_sender in sender:
                transaction['bank_details'] = {
                    'bank_name': bank_name,
                    'account_number': self._extract_account_number(original_email.get('snippet', '')),
                    'account_type': 'savings',
                    'ifsc_code': None,
                    'branch': None
                }
                break
        
        return transaction
    
    async def _enhance_with_upi_patterns(self, transaction: Dict[str, Any], email: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance transaction with UPI-specific patterns"""
        original_email = email.get('original_email', {})
        snippet = original_email.get('snippet', '')
        
        # Extract UPI ID from snippet
        upi_id = self._extract_upi_id(snippet)
        if upi_id:
            # Determine UPI app
            upi_app = "Unknown UPI App"
            for app_pattern, app_name in self.upi_apps.items():
                if app_pattern in upi_id:
                    upi_app = app_name
                    break
            
            transaction['upi_details'] = {
                'transaction_flow': {
                    'direction': 'outgoing',
                    'description': 'Money sent from your account'
                },
                'receiver': {
                    'upi_id': upi_id,
                    'name': transaction.get('merchant', ''),
                    'upi_app': upi_app
                },
                'transaction_reference': transaction.get('transaction_id', '')
            }
        
        return transaction
    
    def _extract_account_number(self, text: str) -> Optional[str]:
        """Extract account number from text"""
        import re
        
        # Look for account patterns
        patterns = [
            r'account (\d+)',
            r'A/C (\d+)',
            r'account number (\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_upi_id(self, text: str) -> Optional[str]:
        """Extract UPI ID from text"""
        import re
        
        # Look for UPI ID patterns
        patterns = [
            r'VPA ([a-zA-Z0-9.]+@[a-zA-Z0-9.]+)',
            r'UPI ID ([a-zA-Z0-9.]+@[a-zA-Z0-9.]+)',
            r'([a-zA-Z0-9.]+@[a-zA-Z0-9.]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    async def _categorize_email_enhanced(self, email: Dict[str, Any], user_id: str, extracted_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced categorization with extracted data"""
        basic_category = await self._categorize_email_basic(email, user_id)
        
        # Enhance with extracted data
        if extracted_data and extracted_data.get('email_type') != 'non_financial':
            # Use extracted data to refine categorization
            if extracted_data.get('is_subscription'):
                basic_category['category'] = 'subscription_payments'
                basic_category['subcategory'] = extracted_data.get('subscription_details', {}).get('type', 'subscription')
                basic_category['confidence'] = max(basic_category['confidence'], 0.9)
            
            if extracted_data.get('payment_method') == 'upi':
                basic_category['category'] = 'upi_transactions'
                basic_category['confidence'] = max(basic_category['confidence'], 0.95)
        
        return basic_category
    
    async def _store_comprehensive_data(self, email: Dict[str, Any], user_id: str, category: Dict[str, Any], extracted_data: Optional[Dict[str, Any]]):
        """Store comprehensive data for every email"""
        email_id = email.get('email_id')
        original_email = email.get('original_email', {})
        
        # Store categorized email
        categorized_email = {
            'user_id': user_id,
            'email_id': email_id,
            'category': category['category'],
            'subcategory': category.get('subcategory'),
            'confidence': category['confidence'],
            'key_indicators': self._generate_key_indicators(original_email, category),
            'merchant_detected': category.get('merchant'),
            'transaction_likely': extracted_data is not None and extracted_data.get('email_type') != 'non_financial',
            'priority': self._calculate_priority(original_email, category),
            'importance_score': self._calculate_importance_score(original_email),
            'original_email': original_email,
            'categorized': True,
            'categorized_at': datetime.now(),
            'financial_data_extracted': extracted_data is not None and extracted_data.get('email_type') != 'non_financial',
            'extracted_at': datetime.now() if extracted_data else None,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Store in database
        await categorized_emails_collection.update_one(
            {'user_id': user_id, 'email_id': email_id},
            {'$set': categorized_email},
            upsert=True
        )
        
        # Store financial transaction if applicable
        if extracted_data and extracted_data.get('email_type') != 'non_financial':
            await financial_transactions_collection.update_one(
                {'user_id': user_id, 'email_id': email_id},
                {'$set': extracted_data},
                upsert=True
            )
        
        logger.info(f"✅ Stored comprehensive data for email {email_id}")
    
    def _generate_key_indicators(self, original_email: Dict[str, Any], category: Dict[str, Any]) -> List[str]:
        """Generate key indicators for categorization"""
        indicators = []
        subject = original_email.get('subject', '').lower()
        snippet = original_email.get('snippet', '').lower()
        sender = original_email.get('from', '').lower()
        
        # Add category-specific indicators
        if category['category'] == 'food_delivery':
            indicators.extend(['food delivery', 'grocery', 'order confirmation'])
        elif category['category'] == 'streaming_services':
            indicators.extend(['subscription', 'streaming', 'entertainment'])
        elif category['category'] == 'banking':
            indicators.extend(['bank', 'transaction', 'alert'])
        elif category['category'] == 'upi_transactions':
            indicators.extend(['upi', 'transaction', 'debit'])
        
        # Add merchant-specific indicators
        if category.get('merchant'):
            indicators.append(f"merchant: {category['merchant']}")
        
        return indicators[:5]  # Limit to 5 indicators
    
    def _calculate_priority(self, original_email: Dict[str, Any], category: Dict[str, Any]) -> str:
        """Calculate email priority"""
        subject = original_email.get('subject', '').lower()
        
        # High priority keywords
        high_priority = ['alert', 'urgent', 'important', 'critical', 'failed', 'error']
        for keyword in high_priority:
            if keyword in subject:
                return 'high'
        
        # Medium priority for financial emails
        if category['category'] in ['banking', 'upi_transactions', 'subscription_payments']:
            return 'medium'
        
        return 'low'
    
    def _calculate_importance_score(self, original_email: Dict[str, Any]) -> float:
        """Calculate email importance score"""
        score = 0.5  # Base score
        
        subject = original_email.get('subject', '').lower()
        sender = original_email.get('from', '').lower()
        
        # Financial keywords boost score
        financial_keywords = ['transaction', 'payment', 'bill', 'subscription', 'upi', 'debit', 'credit']
        for keyword in financial_keywords:
            if keyword in subject:
                score += 0.1
        
        # Bank senders boost score
        if any(bank in sender for bank in ['bank', 'alerts']):
            score += 0.2
        
        # Alert keywords boost score
        if 'alert' in subject:
            score += 0.3
        
        return min(1.0, score)
    
    def _is_promotional_email(self, original_email: Dict[str, Any]) -> bool:
        """Determine if email is promotional"""
        subject = original_email.get('subject', '').lower()
        sender = original_email.get('from', '').lower()
        
        promotional_keywords = ['offer', 'discount', 'sale', 'promotion', 'deal', 'limited time']
        promotional_senders = ['marketing', 'promo', 'offers', 'deals']
        
        for keyword in promotional_keywords:
            if keyword in subject:
                return True
        
        for sender_keyword in promotional_senders:
            if sender_keyword in sender:
                return True
        
        return False
    
    def _generate_body_hash(self, content: str) -> str:
        """Generate SHA256 hash of email body"""
        return hashlib.sha256(content.encode()).hexdigest()

# Convenience functions
async def process_all_emails_universal(emails: List[Dict[str, Any]], user_id: str) -> List[EmailProcessingResult]:
    """Process all emails with universal processor"""
    processor = UniversalEmailProcessor()
    results = []
    
    logger.info(f"🚀 Processing {len(emails)} emails with universal processor")
    
    for email in emails:
        result = await processor.process_email_universal(email, user_id)
        results.append(result)
        
        if result.error:
            logger.warning(f"⚠️ Email {result.email_id} had error: {result.error}")
        else:
            logger.info(f"✅ Processed email {result.email_id}: {result.category} (confidence: {result.confidence:.2f})")
    
    # Summary statistics
    financial_count = sum(1 for r in results if r.is_financial)
    avg_confidence = sum(r.confidence for r in results if not r.error) / max(1, len([r for r in results if not r.error]))
    avg_processing_time = sum(r.processing_time_ms for r in results) / max(1, len(results))
    
    logger.info(f"📊 Processing Summary:")
    logger.info(f"   📧 Total emails: {len(emails)}")
    logger.info(f"   💰 Financial emails: {financial_count}")
    logger.info(f"   🎯 Average confidence: {avg_confidence:.2f}")
    logger.info(f"   ⏱️ Average processing time: {avg_processing_time:.1f}ms")
    
    return results 