"""
Advanced Financial Data Extraction System
=========================================

This module implements comprehensive financial transaction extraction from categorized emails
using OpenAI API with detailed schema extraction for maximum financial intelligence.

Key Features:
- Extracts 50+ financial fields per transaction
- Handles all transaction types (payments, bills, subscriptions, investments)
- Merchant canonicalization and pattern recognition
- Confidence scoring and validation
- Batch processing for efficiency
- MongoDB integration with optimized schemas

Financial Schema:
- Core transaction data (amount, date, merchant, type)
- Payment details (method, bank, card info)
- Service information (billing period, subscription details)
- Metadata (confidence, extraction quality, references)
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import re
from decimal import Decimal
import hashlib

# OpenAI
import openai
from openai import AsyncOpenAI

# Database
from .db import categorized_emails_collection, financial_transactions_collection
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

class TransactionType(Enum):
    """Transaction types"""
    PAYMENT = "payment"
    BILL = "bill"
    SUBSCRIPTION = "subscription"
    INCOME = "income"
    REFUND = "refund"
    FEE = "fee"
    TRANSFER = "transfer"
    INVESTMENT = "investment"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"

class PaymentMethod(Enum):
    """Payment methods"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    EMI = "emi"
    AUTO_DEBIT = "auto_debit"

class ServiceCategory(Enum):
    """Service categories"""
    TELECOM = "telecom"
    UTILITIES = "utilities"
    OTT = "ott"
    BANKING = "banking"
    ECOMMERCE = "ecommerce"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    TRANSPORT = "transport"
    FOOD = "food"
    ENTERTAINMENT = "entertainment"
    INVESTMENT = "investment"
    INSURANCE = "insurance"
    GOVERNMENT = "government"
    RETAIL = "retail"

@dataclass
class FinancialTransaction:
    """Comprehensive financial transaction data structure"""
    # Core transaction data
    transaction_id: str
    user_id: str
    email_id: str
    transaction_type: str
    amount: float
    currency: str
    transaction_date: Optional[str] = None
    
    # Merchant information
    merchant_canonical: str = ""
    merchant_original: str = ""
    merchant_patterns: List[str] = None
    service_category: str = ""
    service_name: str = ""
    
    # Payment details
    payment_method: str = ""
    payment_status: str = ""
    bank_name: str = ""
    account_number: str = ""
    card_number: str = ""
    card_type: str = ""
    upi_id: str = ""
    
    # Transaction references
    transaction_reference: str = ""
    invoice_number: str = ""
    order_id: str = ""
    receipt_number: str = ""
    
    # Billing and service details
    due_date: Optional[str] = None
    service_period_start: Optional[str] = None
    service_period_end: Optional[str] = None
    billing_period_start: Optional[str] = None
    billing_period_end: Optional[str] = None
    
    # Subscription details
    is_subscription: bool = False
    subscription_frequency: str = ""
    next_renewal_date: Optional[str] = None
    is_automatic_payment: bool = False
    
    # Financial breakdown
    total_amount: float = 0.0
    base_amount: float = 0.0
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    late_fee_amount: float = 0.0
    processing_fee: float = 0.0
    cashback_amount: float = 0.0
    
    # Metadata
    email_subject: str = ""
    email_received_date: Optional[str] = None
    important_invoice_date: Optional[str] = None
    clearance_date: Optional[str] = None
    full_text_context: str = ""
    email_summary: str = ""
    
    # Quality metrics
    extraction_confidence: float = 0.0
    data_completeness: float = 0.0
    requires_action: bool = False
    
    # Timestamps
    extracted_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.merchant_patterns is None:
            self.merchant_patterns = []
        if self.extracted_at is None:
            self.extracted_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class AdvancedFinancialExtractor:
    """Advanced financial data extraction system"""
    
    def __init__(self, batch_size: int = 50):
        self.batch_size = batch_size
        self.setup_merchant_patterns()
    
    def setup_merchant_patterns(self):
        """Setup merchant name patterns for canonicalization"""
        self.merchant_patterns = {
            # Telecom
            "airtel": ["airtel", "bharti airtel", "airtel payments bank"],
            "jio": ["jio", "reliance jio", "jio payments bank"],
            "vodafone": ["vodafone", "vodafone idea", "vi"],
            "bsnl": ["bsnl", "bharat sanchar nigam"],
            
            # Banking
            "hdfc": ["hdfc", "hdfc bank", "hdfc credit card"],
            "icici": ["icici", "icici bank", "icici credit card"],
            "sbi": ["sbi", "state bank of india", "sbi credit card"],
            "axis": ["axis", "axis bank", "axis credit card"],
            "kotak": ["kotak", "kotak mahindra bank"],
            "yes": ["yes", "yes bank"],
            
            # E-commerce
            "amazon": ["amazon", "amazon.in", "amazon prime"],
            "flipkart": ["flipkart", "flipkart.com"],
            "myntra": ["myntra", "myntra.com"],
            "swiggy": ["swiggy", "swiggy.com"],
            "zomato": ["zomato", "zomato.com"],
            
            # OTT Services
            "netflix": ["netflix", "netflix.com"],
            "prime": ["prime", "amazon prime", "prime video"],
            "hotstar": ["hotstar", "disney+ hotstar"],
            "sonyliv": ["sonyliv", "sony liv"],
            
            # Utilities
            "tata": ["tata", "tata power", "tata motors"],
            "adani": ["adani", "adani electricity"],
            "brihanmumbai": ["brihanmumbai", "brihanmumbai electric supply"],
            
            # Investment
            "zerodha": ["zerodha", "zerodha.com"],
            "groww": ["groww", "groww.in"],
            "upstox": ["upstox", "upstox.com"],
            "angel": ["angel", "angel broking"],
            
            # Insurance
            "lic": ["lic", "life insurance corporation"],
            "hdfc_life": ["hdfc life", "hdfc life insurance"],
            "icici_lombard": ["icici lombard", "icici lombard general insurance"],
        }
    
    async def extract_financial_data(self, user_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Main function to extract financial data from categorized emails
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"🚀 Starting financial data extraction for user {user_id}")
            
            # Get financial emails from categorized collection
            financial_emails = await self._get_financial_emails(user_id, limit)
            total_emails = len(financial_emails)
            
            if total_emails == 0:
                logger.info(f"✅ No financial emails found for user {user_id}")
                return {
                    "success": True,
                    "total_emails": 0,
                    "processed_emails": 0,
                    "extracted_transactions": 0,
                    "processing_time": 0.0,
                    "transaction_types": {},
                    "merchants": {}
                }
            
            logger.info(f"📊 Found {total_emails} financial emails to process")
            
            # Create batches
            batches = self._create_batches(financial_emails, self.batch_size)
            logger.info(f"📦 Created {len(batches)} batches of size {self.batch_size}")
            
            # Process batches
            all_transactions = []
            processed_count = 0
            
            for batch_idx, batch in enumerate(batches):
                logger.info(f"🔄 Processing batch {batch_idx + 1}/{len(batches)}")
                batch_transactions = await self._process_financial_batch(batch, user_id)
                all_transactions.extend(batch_transactions)
                processed_count += len(batch)
            
            # Store transactions in MongoDB
            if all_transactions:
                await self._store_financial_transactions(all_transactions)
                logger.info(f"💾 Stored {len(all_transactions)} financial transactions")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Generate statistics
            transaction_types = self._get_transaction_type_breakdown(all_transactions)
            merchants = self._get_merchant_breakdown(all_transactions)
            
            logger.info(f"✅ Financial extraction completed:")
            logger.info(f"   📊 Total emails: {total_emails}")
            logger.info(f"   ✅ Processed: {processed_count}")
            logger.info(f"   💰 Extracted transactions: {len(all_transactions)}")
            logger.info(f"   ⏱️ Processing time: {processing_time:.2f}s")
            logger.info(f"   📈 Transaction types: {transaction_types}")
            
            return {
                "success": True,
                "total_emails": total_emails,
                "processed_emails": processed_count,
                "extracted_transactions": len(all_transactions),
                "processing_time": processing_time,
                "transaction_types": transaction_types,
                "merchants": merchants
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Financial extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_emails": 0,
                "processed_emails": 0,
                "extracted_transactions": 0,
                "processing_time": processing_time,
                "transaction_types": {},
                "merchants": {}
            }

    async def _get_financial_emails(self, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get financial emails from categorized collection"""
        try:
            query = {
                "user_id": user_id,
                "category": {"$in": ["financial", "utilities", "subscriptions", "insurance", "investment"]},
                "financial_data_extracted": {"$ne": True}
            }
            
            if limit:
                cursor = categorized_emails_collection.find(query).limit(limit)
            else:
                cursor = categorized_emails_collection.find(query)
            
            emails = await cursor.to_list(length=None)
            logger.info(f"📧 Retrieved {len(emails)} financial emails for user {user_id}")
            return emails
            
        except Exception as e:
            logger.error(f"❌ Error retrieving financial emails: {e}")
            return []

    def _create_batches(self, emails: List[Dict], batch_size: int) -> List[List[Dict]]:
        """Create batches of emails for processing"""
        return [emails[i:i + batch_size] for i in range(0, len(emails), batch_size)]

    async def _process_financial_batch(self, batch: List[Dict], user_id: str) -> List[Dict]:
        """Process a batch of financial emails"""
        try:
            # Get full email content for better extraction
            email_ids = [email.get('email_id') for email in batch]
            full_emails = await self._get_full_email_content(email_ids)
            
            transactions = []
            for email in batch:
                email_id = email.get('email_id')
                full_email = full_emails.get(email_id, {})
                
                transaction = await self._extract_single_transaction(email, full_email, user_id)
                if transaction:
                    transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            logger.error(f"❌ Error processing financial batch: {e}")
            return []

    async def _get_full_email_content(self, email_ids: List[str]) -> Dict[str, Dict]:
        """Get full email content from email_logs collection"""
        try:
            cursor = email_logs_collection.find({"id": {"$in": email_ids}})
            emails = await cursor.to_list(length=None)
            
            return {email.get('id'): email for email in emails}
            
        except Exception as e:
            logger.error(f"❌ Error getting full email content: {e}")
            return {}

    async def _extract_single_transaction(self, email: Dict, full_email: Dict, user_id: str) -> Optional[Dict]:
        """Extract financial transaction from a single email"""
        try:
            # Create extraction prompt
            prompt = self._create_extraction_prompt(email, full_email)
            
            # Call OpenAI API
            if not client:
                logger.error("❌ OpenAI client not initialized. Cannot extract transaction.")
                return None
            
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert financial transaction extraction agent. Your task is to analyze financial emails
                        and extract comprehensive structured transaction data with maximum accuracy and detail.
                        
                        EXTRACTION REQUIREMENTS:
                        
                        1. CORE TRANSACTION DATA:
                           - transaction_type: payment|bill|subscription|income|refund|fee|transfer|investment
                           - amount: Extract exact numerical amount (convert to float)
                           - currency: INR, USD, EUR, etc.
                           - transaction_date: YYYY-MM-DD format
                           - merchant_canonical: Standardized merchant name
                           - service_category: telecom|utilities|ott|banking|ecommerce|education|healthcare|transport|food|entertainment|investment|insurance
                        
                        2. PAYMENT DETAILS:
                           - payment_method: credit_card|debit_card|upi|net_banking|wallet|bank_transfer
                           - payment_status: completed|pending|failed|partial|disputed|cancelled
                           - bank_name: Bank name if available
                           - card_type: visa|mastercard|amex|rupay
                           - upi_id: UPI ID if available
                        
                        3. TRANSACTION REFERENCES:
                           - transaction_reference: Unique transaction reference
                           - invoice_number: Invoice number
                           - order_id: Order ID if applicable
                           - receipt_number: Receipt number
                        
                        4. BILLING DETAILS:
                           - due_date: Payment due date
                           - service_period_start: Service period start
                           - service_period_end: Service period end
                           - billing_period_start: Billing period start
                           - billing_period_end: Billing period end
                        
                        5. SUBSCRIPTION DETAILS:
                           - is_subscription: true/false
                           - subscription_frequency: monthly|quarterly|yearly
                           - next_renewal_date: Next renewal date
                           - is_automatic_payment: true/false
                        
                        6. FINANCIAL BREAKDOWN:
                           - total_amount: Total amount
                           - base_amount: Base amount before taxes
                           - tax_amount: Tax amount
                           - discount_amount: Discount amount
                           - late_fee_amount: Late fee if any
                           - processing_fee: Processing fee
                           - cashback_amount: Cashback amount
                        
                        7. QUALITY METRICS:
                           - extraction_confidence: 0.0 to 1.0
                           - data_completeness: 0.0 to 1.0
                           - requires_action: true/false
                        
                        RESPONSE FORMAT:
                        Return a comprehensive JSON object with all extracted fields. Use null for missing values.
                        Ensure all amounts are numerical values, not strings.
                        
                        REQUIRED FIELDS:
                        {
                            "transaction_type": "payment|bill|subscription|income|refund|fee|transfer|investment|debit|credit",
                            "amount": 599.00,
                            "currency": "INR",
                            "transaction_date": "YYYY-MM-DD",
                            "merchant_canonical": "Standardized merchant name",
                            "merchant_original": "Original merchant name from email",
                            "merchant_patterns": ["pattern1", "pattern2"],
                            "service_category": "telecom|utilities|ott|banking|ecommerce|education|healthcare|transport|food|entertainment|investment|insurance|cloud_storage|financial_services",
                            "service_subcategory": "specific subcategory",
                            "payment_method": "upi|credit_card|debit_card|net_banking|wallet|bank_transfer|cash|emi|auto_debit|unknown",
                            "payment_status": "completed|pending|failed|partial|disputed|cancelled",
                            "transaction_reference": "Transaction ID or reference",
                            "invoice_number": "Invoice number if available",
                            "order_id": "Order ID if available",
                            "receipt_number": "Receipt number if available",
                            "bank_name": "Bank name if available",
                            "account_number": "Account number if available",
                            "upi_id": "UPI ID if UPI payment",
                            "upi_app": "UPI app name if available",
                            "is_subscription": true/false,
                            "subscription_product": "Product name if subscription",
                            "subscription_category": "Category if subscription",
                            "subscription_type": "Type if subscription",
                            "subscription_confidence": 0.7,
                            "subscription_reasons": ["reason1", "reason2"],
                            "subscription_frequency": "monthly|yearly|quarterly",
                            "next_renewal_date": "YYYY-MM-DD",
                            "is_automatic_payment": true/false,
                            "total_amount": 599.00,
                            "base_amount": 500.00,
                            "tax_amount": 99.00,
                            "discount_amount": 0.00,
                            "late_fee_amount": 0.00,
                            "processing_fee": 0.00,
                            "cashback_amount": 0.00,
                            "convenience_fee": 0.00,
                            "due_date": "YYYY-MM-DD",
                            "service_period_start": "YYYY-MM-DD",
                            "service_period_end": "YYYY-MM-DD",
                            "billing_period_start": "YYYY-MM-DD",
                            "billing_period_end": "YYYY-MM-DD",
                            "description": "Transaction description",
                            "amount_original": "₹599.00",
                            "date_original": "15th March 2024",
                            "email_body_hash": "SHA256 hash",
                            "email_summary": "Brief email summary",
                            "extraction_confidence": 0.95,
                            "data_completeness": 0.90,
                            "requires_action": false,
                            "merchant_confidence": 0.8
                        }"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse response
            response_content = response.choices[0].message.content
            transaction = self._parse_extraction_response(response_content, email, user_id)
            
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Error extracting transaction from email {email.get('email_id')}: {e}")
            return None

    def _create_extraction_prompt(self, email: Dict, full_email: Dict) -> str:
        """Create extraction prompt for financial email"""
        email_id = email.get('email_id', 'unknown')
        subject = email.get('original_email', {}).get('subject', 'No subject')
        sender = email.get('original_email', {}).get('from', 'Unknown sender')
        
        # Get full content from original email
        content = full_email.get('content', '')
        if not content:
            content = email.get('original_email', {}).get('content', '')
        
        prompt = f"""
        Please extract comprehensive financial transaction data from this email:
        
        EMAIL ID: {email_id}
        FROM: {sender}
        SUBJECT: {subject}
        CONTENT: {content[:2000]}...
        
        Extract all available financial information and return as a JSON object.
        """
        
        return prompt

    def _parse_extraction_response(self, response: str, email: Dict, user_id: str) -> Optional[Dict]:
        """Parse the extraction response and create comprehensive transaction object"""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON object found in response")
                return None
            
            json_str = response[json_start:json_end]
            extraction_data = json.loads(json_str)
            
            # Generate transaction ID
            transaction_id = self._generate_transaction_id(user_id, email.get('email_id'))
            
            # Extract UPI details if available
            upi_details = None
            if extraction_data.get('payment_method') == 'upi':
                upi_details = {
                    'transaction_flow': {
                        'direction': 'outgoing',
                        'description': 'Money sent from your account'
                    },
                    'receiver': {
                        'upi_id': extraction_data.get('upi_id', ''),
                        'name': extraction_data.get('merchant_canonical', ''),
                        'upi_app': extraction_data.get('upi_app', 'Unknown UPI App')
                    },
                    'transaction_reference': extraction_data.get('transaction_reference', '')
                }
            
            # Extract subscription details
            subscription_details = None
            if extraction_data.get('is_subscription', False):
                subscription_details = {
                    'is_subscription': True,
                    'product_name': extraction_data.get('subscription_product', ''),
                    'category': extraction_data.get('subscription_category', ''),
                    'type': extraction_data.get('subscription_type', ''),
                    'confidence_score': extraction_data.get('subscription_confidence', 0.7),
                    'detection_reasons': extraction_data.get('subscription_reasons', []),
                    'subscription_frequency': extraction_data.get('subscription_frequency', ''),
                    'next_renewal_date': extraction_data.get('next_renewal_date'),
                    'is_automatic_payment': extraction_data.get('is_automatic_payment', False)
                }
            
            # Extract bank details
            bank_details = None
            if extraction_data.get('bank_name'):
                bank_details = {
                    'bank_name': extraction_data.get('bank_name'),
                    'account_number': extraction_data.get('account_number'),
                    'account_type': extraction_data.get('account_type'),
                    'ifsc_code': extraction_data.get('ifsc_code'),
                    'branch': extraction_data.get('branch')
                }
            
            # Extract merchant details
            merchant_details = {
                'canonical_name': self._canonicalize_merchant(extraction_data.get('merchant_canonical', '')),
                'original_name': extraction_data.get('merchant_original', ''),
                'patterns': extraction_data.get('merchant_patterns', []),
                'category': extraction_data.get('service_category', ''),
                'subcategory': extraction_data.get('service_subcategory', ''),
                'confidence_score': extraction_data.get('merchant_confidence', 0.8),
                'detection_method': 'ai_extraction'
            }
            
            # Extract financial breakdown
            financial_breakdown = {
                'total_amount': float(extraction_data.get('total_amount', 0)),
                'base_amount': float(extraction_data.get('base_amount', 0)),
                'tax_amount': float(extraction_data.get('tax_amount', 0)),
                'discount_amount': float(extraction_data.get('discount_amount', 0)),
                'late_fee_amount': float(extraction_data.get('late_fee_amount', 0)),
                'processing_fee': float(extraction_data.get('processing_fee', 0)),
                'cashback_amount': float(extraction_data.get('cashback_amount', 0)),
                'convenience_fee': float(extraction_data.get('convenience_fee', 0))
            }
            
            # Extract email metadata
            email_metadata = {
                'subject': email.get('original_email', {}).get('subject', ''),
                'sender': email.get('original_email', {}).get('from', ''),
                'received_date': email.get('original_email', {}).get('received_date'),
                'snippet': email.get('original_email', {}).get('snippet', ''),
                'body_hash': extraction_data.get('email_body_hash'),
                'importance_score': email.get('importance_score', 0.0),
                'is_financial_email': True,
                'is_promotional': False
            }
            
            # Extract extraction metadata
            extraction_metadata = {
                'extracted_at': datetime.now(),
                'extraction_method': 'ai_extraction',
                'confidence_score': float(extraction_data.get('extraction_confidence', 0.5)),
                'data_completeness': float(extraction_data.get('data_completeness', 0.5)),
                'extraction_version': '2.0',
                'model_used': 'gpt-4o',
                'processing_time_ms': None
            }
            
            # Create comprehensive transaction object
            transaction = {
                'id': transaction_id,
                'email_id': email.get('email_id'),
                'user_id': user_id,
                'amount': float(extraction_data.get('amount', 0)),
                'currency': extraction_data.get('currency', 'INR'),
                'transaction_type': extraction_data.get('transaction_type', 'payment'),
                'transaction_date': extraction_data.get('transaction_date'),
                'merchant': extraction_data.get('merchant_canonical', ''),
                'merchant_details': merchant_details,
                'service_category': extraction_data.get('service_category', ''),
                'service_name': extraction_data.get('service_name', ''),
                'payment_method': extraction_data.get('payment_method', 'unknown'),
                'payment_status': extraction_data.get('payment_status', 'completed'),
                'transaction_id': extraction_data.get('transaction_reference', ''),
                'invoice_number': extraction_data.get('invoice_number', ''),
                'order_id': extraction_data.get('order_id', ''),
                'receipt_number': extraction_data.get('receipt_number', ''),
                'bank_details': bank_details,
                'upi_details': upi_details,
                'card_details': {},
                'subscription_details': subscription_details,
                'is_subscription': extraction_data.get('is_subscription', False),
                'subscription_product': extraction_data.get('subscription_product'),
                'financial_breakdown': financial_breakdown,
                'due_date': extraction_data.get('due_date'),
                'service_period_start': extraction_data.get('service_period_start'),
                'service_period_end': extraction_data.get('service_period_end'),
                'billing_period_start': extraction_data.get('billing_period_start'),
                'billing_period_end': extraction_data.get('billing_period_end'),
                'email_metadata': email_metadata,
                'description': extraction_data.get('description', ''),
                'snippet': email.get('original_email', {}).get('snippet', ''),
                'sender': email.get('original_email', {}).get('from', ''),
                'subject': email.get('original_email', {}).get('subject', ''),
                'extraction_metadata': extraction_metadata,
                'extracted_at': datetime.now(),
                'confidence_score': float(extraction_data.get('extraction_confidence', 0.5)),
                'amount_original': extraction_data.get('amount_original'),
                'date_original': extraction_data.get('date_original'),
                'full_text_context': email.get('original_email', {}).get('content', ''),
                'email_summary': extraction_data.get('email_summary', ''),
                'requires_action': extraction_data.get('requires_action', False),
                'is_automatic_payment': extraction_data.get('is_automatic_payment', False),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Error parsing extraction response: {e}")
            return None

    def _generate_transaction_id(self, user_id: str, email_id: str) -> str:
        """Generate unique transaction ID"""
        unique_string = f"{user_id}_{email_id}_{datetime.now().timestamp()}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def _canonicalize_merchant(self, merchant_name: str) -> str:
        """Canonicalize merchant name using patterns"""
        if not merchant_name:
            return ""
        
        merchant_lower = merchant_name.lower()
        
        for canonical, patterns in self.merchant_patterns.items():
            if any(pattern in merchant_lower for pattern in patterns):
                return canonical
        
        return merchant_name.lower()

    async def _store_financial_transactions(self, transactions: List[Dict]) -> None:
        """Store financial transactions in MongoDB"""
        try:
            if transactions:
                # Insert transactions
                await financial_transactions_collection.insert_many(transactions)
                
                # Update categorized emails to mark as processed
                email_ids = [t['email_id'] for t in transactions]
                await categorized_emails_collection.update_many(
                    {"email_id": {"$in": email_ids}},
                    {"$set": {"financial_data_extracted": True, "extracted_at": datetime.now()}}
                )
                
                logger.info(f"💾 Successfully stored {len(transactions)} financial transactions")
                
        except Exception as e:
            logger.error(f"❌ Error storing financial transactions: {e}")

    def _get_transaction_type_breakdown(self, transactions: List[Dict]) -> Dict[str, int]:
        """Get breakdown of transaction types"""
        breakdown = {}
        for transaction in transactions:
            t_type = transaction.get('transaction_type', 'unknown')
            breakdown[t_type] = breakdown.get(t_type, 0) + 1
        return breakdown

    def _get_merchant_breakdown(self, transactions: List[Dict]) -> Dict[str, int]:
        """Get breakdown of merchants"""
        breakdown = {}
        for transaction in transactions:
            merchant = transaction.get('merchant_canonical', 'unknown')
            breakdown[merchant] = breakdown.get(merchant, 0) + 1
        return breakdown

# Convenience functions
async def start_financial_extraction(user_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """Start financial extraction for a user"""
    extractor = AdvancedFinancialExtractor()
    return await extractor.extract_financial_data(user_id, limit)

async def get_financial_extraction_status(user_id: str) -> Dict[str, Any]:
    """Get financial extraction status for a user"""
    try:
        total_financial_emails = await categorized_emails_collection.count_documents({
            "user_id": user_id,
            "category": {"$in": ["financial", "utilities", "subscriptions", "insurance", "investment"]}
        })
        
        extracted_emails = await categorized_emails_collection.count_documents({
            "user_id": user_id,
            "category": {"$in": ["financial", "utilities", "subscriptions", "insurance", "investment"]},
            "financial_data_extracted": True
        })
        
        total_transactions = await financial_transactions_collection.count_documents({"user_id": user_id})
        
        return {
            "user_id": user_id,
            "total_financial_emails": total_financial_emails,
            "extracted_emails": extracted_emails,
            "total_transactions": total_transactions,
            "extraction_percentage": (extracted_emails / total_financial_emails * 100) if total_financial_emails > 0 else 0
        }
    except Exception as e:
        logger.error(f"❌ Error getting financial extraction status: {e}")
        return {"error": str(e)} 