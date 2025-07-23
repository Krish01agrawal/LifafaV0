"""
SMS Data Processing Service
===========================

This module handles SMS data processing and financial transaction extraction from SMS messages.
It follows the same pattern as the Gmail service but is optimized for SMS data structures.

Key Features:
- SMS data ingestion and storage
- Financial transaction extraction from SMS
- SMS categorization and filtering
- Integration with existing financial extraction pipeline
- Support for multiple SMS formats (bank SMS, UPI notifications, etc.)
"""

import asyncio
import logging
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

from app.db import db_manager
from app.config.settings import settings

logger = logging.getLogger(__name__)

class SMSProvider(Enum):
    """SMS providers/sources"""
    ANDROID_SMS = "android_sms"
    IOS_SMS = "ios_sms"
    BANK_SMS = "bank_sms"
    UPI_SMS = "upi_sms"
    MANUAL_UPLOAD = "manual_upload"
    API_INTEGRATION = "api_integration"

class SMSType(Enum):
    """SMS message types"""
    TRANSACTION = "transaction"
    BALANCE = "balance"
    OTP = "otp"
    PROMOTIONAL = "promotional"
    BANK_ALERT = "bank_alert"
    UPI_NOTIFICATION = "upi_notification"
    BILL_REMINDER = "bill_reminder"
    SUBSCRIPTION = "subscription"
    GENERAL = "general"

@dataclass
class SMSMessage:
    """SMS message data structure"""
    # Core SMS data
    sms_id: str
    user_id: str
    provider: str
    sms_type: str
    
    # Message content
    sender_number: str
    sender_name: str
    message_body: str
    received_date: datetime
    
    # Metadata
    is_read: bool = False
    is_archived: bool = False
    is_financial: bool = False
    
    # Processing metadata
    processed_at: Optional[datetime] = None
    extraction_confidence: float = 0.0
    financial_data_extracted: bool = False
    
    # Timestamps
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class SMSPatternMatcher:
    """Pattern matching for different types of SMS messages"""
    
    def __init__(self):
        # Bank transaction patterns
        self.bank_patterns = {
            'debit': [
                r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:has been|is)\s*(?:debited|deducted)',
                r'Debited\s*Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'Amount\s*Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:debited|deducted)',
                r'(\d+(?:,\d+)*(?:\.\d{2})?)\s*Rs\.?\s*(?:debited|deducted)'
            ],
            'credit': [
                r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:has been|is)\s*(?:credited|received)',
                r'Credited\s*Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'Amount\s*Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:credited|received)',
                r'(\d+(?:,\d+)*(?:\.\d{2})?)\s*Rs\.?\s*(?:credited|received)'
            ]
        }
        
        # UPI patterns
        self.upi_patterns = {
            'payment_sent': [
                r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*sent\s*to\s*([A-Za-z0-9@.]+)',
                r'(\d+(?:,\d+)*(?:\.\d{2})?)\s*Rs\.?\s*sent\s*to\s*([A-Za-z0-9@.]+)',
                r'UPI\s*payment\s*of\s*Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*to\s*([A-Za-z0-9@.]+)'
            ],
            'payment_received': [
                r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*received\s*from\s*([A-Za-z0-9@.]+)',
                r'(\d+(?:,\d+)*(?:\.\d{2})?)\s*Rs\.?\s*received\s*from\s*([A-Za-z0-9@.]+)',
                r'UPI\s*payment\s*of\s*Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*from\s*([A-Za-z0-9@.]+)'
            ]
        }
        
        # Bank names and patterns
        self.bank_patterns_map = {
            'HDFC': ['HDFC', 'HDFC Bank', 'HDFCBANK'],
            'SBI': ['SBI', 'State Bank', 'STATE BANK'],
            'ICICI': ['ICICI', 'ICICI Bank'],
            'Axis': ['AXIS', 'Axis Bank'],
            'Kotak': ['KOTAK', 'Kotak Bank'],
            'Yes Bank': ['YES', 'Yes Bank'],
            'IDFC': ['IDFC', 'IDFC Bank'],
            'RBL': ['RBL', 'RBL Bank'],
            'Federal': ['FEDERAL', 'Federal Bank'],
            'PNB': ['PNB', 'Punjab National Bank'],
            'Canara': ['CANARA', 'Canara Bank'],
            'Bank of Baroda': ['BOB', 'Bank of Baroda'],
            'Union Bank': ['UNION', 'Union Bank'],
            'Bank of India': ['BOI', 'Bank of India']
        }
        
        # Merchant patterns
        self.merchant_patterns = {
            'netflix': ['netflix', 'NETFLIX'],
            'amazon': ['amazon', 'AMZN', 'AMAZON'],
            'flipkart': ['flipkart', 'FLIPKART'],
            'swiggy': ['swiggy', 'SWIGGY'],
            'zomato': ['zomato', 'ZOMATO'],
            'uber': ['uber', 'UBER'],
            'ola': ['ola', 'OLA'],
            'paytm': ['paytm', 'PAYTM'],
            'phonepe': ['phonepe', 'PHONEPE'],
            'google': ['google', 'GOOGLE'],
            'microsoft': ['microsoft', 'MSFT'],
            'adobe': ['adobe', 'ADOBE'],
            'spotify': ['spotify', 'SPOTIFY'],
            'youtube': ['youtube', 'YOUTUBE'],
            'disney': ['disney', 'DISNEY', 'HOTSTAR'],
            'prime': ['prime', 'PRIME', 'AMAZON PRIME']
        }
    
    def classify_sms_type(self, message_body: str, sender_number: str) -> str:
        """Classify SMS type based on content and sender"""
        message_lower = message_body.lower()
        
        # Check for OTP
        if any(pattern in message_lower for pattern in ['otp', 'one time password', 'verification code']):
            return SMSType.OTP.value
        
        # Check for balance
        if any(pattern in message_lower for pattern in ['balance', 'bal', 'available balance']):
            return SMSType.BALANCE.value
        
        # Check for UPI
        if any(pattern in message_lower for pattern in ['upi', 'unified payment interface']):
            return SMSType.UPI_NOTIFICATION.value
        
        # Check for bank alerts
        if any(pattern in message_lower for pattern in ['bank', 'account', 'card', 'credit', 'debit']):
            return SMSType.BANK_ALERT.value
        
        # Check for bill reminders
        if any(pattern in message_lower for pattern in ['bill', 'due', 'payment due', 'reminder']):
            return SMSType.BILL_REMINDER.value
        
        # Check for transactions
        if any(pattern in message_lower for pattern in ['rs.', 'debited', 'credited', 'sent', 'received']):
            return SMSType.TRANSACTION.value
        
        # Check for promotional
        if any(pattern in message_lower for pattern in ['offer', 'discount', 'sale', 'limited time']):
            return SMSType.PROMOTIONAL.value
        
        return SMSType.GENERAL.value
    
    def is_financial_sms(self, message_body: str, sender_number: str) -> bool:
        """Check if SMS contains financial information"""
        message_lower = message_body.lower()
        
        # Check for amount patterns
        amount_patterns = [
            r'rs\.?\s*\d+(?:,\d+)*(?:\.\d{2})?',
            r'\d+(?:,\d+)*(?:\.\d{2})?\s*rs\.?',
            r'rs\.?\s*\d+',
            r'\d+\s*rs\.?'
        ]
        
        for pattern in amount_patterns:
            if re.search(pattern, message_lower):
                return True
        
        # Check for transaction keywords
        transaction_keywords = [
            'debited', 'credited', 'sent', 'received', 'payment', 'transaction',
            'balance', 'account', 'card', 'upi', 'transfer', 'withdrawal', 'deposit'
        ]
        
        return any(keyword in message_lower for keyword in transaction_keywords)
    
    def extract_bank_name(self, message_body: str, sender_number: str) -> Optional[str]:
        """Extract bank name from SMS"""
        message_upper = message_body.upper()
        
        for bank_name, patterns in self.bank_patterns_map.items():
            for pattern in patterns:
                if pattern in message_upper:
                    return bank_name
        
        return None
    
    def extract_amount(self, message_body: str) -> Optional[float]:
        """Extract amount from SMS with enhanced patterns"""
        # Enhanced amount patterns for various formats
        amount_patterns = [
            r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'(\d+(?:,\d+)*(?:\.\d{2})?)\s*rs\.?',
            r'rs\.?\s*(\d+)',
            r'(\d+)\s*rs\.?',
            r'amount\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'(\d+(?:,\d+)*(?:\.\d{2})?)\s*amount',
            r'debited\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'credited\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'sent\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'received\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, message_body, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        return None
    
    def extract_account_number(self, message_body: str) -> Optional[str]:
        """Extract account number from SMS"""
        # Account number patterns
        account_patterns = [
            r'account\s*(?:no\.?|number)?\s*([a-zA-Z0-9]{4,20})',
            r'from\s*your\s*account\s*([a-zA-Z0-9]{4,20})',
            r'to\s*your\s*account\s*([a-zA-Z0-9]{4,20})',
            r'account\s*([a-zA-Z0-9]{4,20})',
            r'xx(\d{4,12})',  # Masked account numbers like XX1234
            r'(\d{4,12})',    # Direct account numbers
            r'card\s*ending\s*(\d{4})',  # Card last 4 digits
            r'card\s*(\d{4})'  # Card number patterns
        ]
        
        for pattern in account_patterns:
            match = re.search(pattern, message_body, re.IGNORECASE)
            if match:
                account_num = match.group(1)
                # Validate account number format
                if len(account_num) >= 4 and account_num.isalnum():
                    return account_num
        
        return None
    
    def extract_transaction_type(self, message_body: str) -> str:
        """Extract transaction type from SMS"""
        message_lower = message_body.lower()
        
        # Debit patterns
        debit_keywords = [
            'debited', 'deducted', 'sent', 'paid', 'withdrawn', 'charged',
            'debit', 'payment', 'purchase', 'spent', 'expense'
        ]
        
        # Credit patterns
        credit_keywords = [
            'credited', 'received', 'deposited', 'added', 'refunded',
            'credit', 'refund', 'cashback', 'reward', 'bonus'
        ]
        
        # Refund patterns
        refund_keywords = [
            'refund', 'refunded', 'reversed', 'cancelled', 'returned',
            'chargeback', 'dispute', 'reversal'
        ]
        
        # Check for refund first (most specific)
        if any(keyword in message_lower for keyword in refund_keywords):
            return 'refund'
        
        # Check for credit
        if any(keyword in message_lower for keyword in credit_keywords):
            return 'credit'
        
        # Check for debit
        if any(keyword in message_lower for keyword in debit_keywords):
            return 'debit'
        
        return 'unknown'
    
    def extract_transaction_reference(self, message_body: str) -> Optional[str]:
        """Extract transaction reference/ID from SMS"""
        # Transaction reference patterns
        ref_patterns = [
            r'transaction\s*(?:id|ref|reference)?\s*:?\s*([a-zA-Z0-9]{8,20})',
            r'ref\s*:?\s*([a-zA-Z0-9]{8,20})',
            r'reference\s*:?\s*([a-zA-Z0-9]{8,20})',
            r'upi\s*ref\s*:?\s*([a-zA-Z0-9]{8,20})',
            r'upi\s*reference\s*:?\s*([a-zA-Z0-9]{8,20})',
            r'id\s*:?\s*([a-zA-Z0-9]{8,20})',
            r'txn\s*id\s*:?\s*([a-zA-Z0-9]{8,20})',
            r'transaction\s*([a-zA-Z0-9]{8,20})'
        ]
        
        for pattern in ref_patterns:
            match = re.search(pattern, message_body, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def extract_balance(self, message_body: str) -> Optional[float]:
        """Extract available balance from SMS"""
        # Balance patterns
        balance_patterns = [
            r'available\s*balance\s*:?\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'balance\s*:?\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'bal\s*:?\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'available\s*bal\s*:?\s*rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*available',
            r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)\s*balance'
        ]
        
        for pattern in balance_patterns:
            match = re.search(pattern, message_body, re.IGNORECASE)
            if match:
                balance_str = match.group(1).replace(',', '')
                try:
                    return float(balance_str)
                except ValueError:
                    continue
        
        return None
    
    def extract_merchant_name(self, message_body: str) -> Optional[str]:
        """Extract merchant name from SMS with enhanced patterns"""
        message_lower = message_body.lower()
        
        # Enhanced merchant patterns
        merchant_patterns = {
            'netflix': ['netflix', 'NETFLIX'],
            'amazon': ['amazon', 'AMZN', 'AMAZON'],
            'flipkart': ['flipkart', 'FLIPKART'],
            'swiggy': ['swiggy', 'SWIGGY'],
            'zomato': ['zomato', 'ZOMATO'],
            'uber': ['uber', 'UBER'],
            'ola': ['ola', 'OLA'],
            'paytm': ['paytm', 'PAYTM'],
            'phonepe': ['phonepe', 'PHONEPE'],
            'google': ['google', 'GOOGLE'],
            'microsoft': ['microsoft', 'MSFT'],
            'adobe': ['adobe', 'ADOBE'],
            'spotify': ['spotify', 'SPOTIFY'],
            'youtube': ['youtube', 'YOUTUBE'],
            'disney': ['disney', 'DISNEY', 'HOTSTAR'],
            'prime': ['prime', 'PRIME', 'AMAZON PRIME'],
            'apple': ['apple', 'APPLE', 'ITUNES'],
            'github': ['github', 'GITHUB'],
            'vercel': ['vercel', 'VERCEL'],
            'netlify': ['netlify', 'NETLIFY'],
            'railway': ['railway', 'RAILWAY'],
            'render': ['render', 'RENDER'],
            'openai': ['openai', 'OPENAI'],
            'anthropic': ['anthropic', 'ANTHROPIC'],
            'groq': ['groq', 'GROQ'],
            'cohere': ['cohere', 'COHERE'],
            'huggingface': ['huggingface', 'HUGGINGFACE'],
            'canva': ['canva', 'CANVA'],
            'figma': ['figma', 'FIGMA'],
            'notion': ['notion', 'NOTION'],
            'trello': ['trello', 'TRELLO'],
            'asana': ['asana', 'ASANA'],
            'slack': ['slack', 'SLACK'],
            'zoom': ['zoom', 'ZOOM'],
            'dropbox': ['dropbox', 'DROPBOX'],
            'mem0': ['mem0', 'MEM0'],
            'framer': ['framer', 'FRAMER'],
            'webflow': ['webflow', 'WEBFLOW'],
            'ahrefs': ['ahrefs', 'AHREFS'],
            'semrush': ['semrush', 'SEMRUSH'],
            'clevertap': ['clevertap', 'CLEVERTAP', 'clevartap'],
            'gitlab': ['gitlab', 'GITLAB']
        }
        
        # Check for merchant patterns
        for merchant, patterns in merchant_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return merchant.title()
        
        # Check for "merchant:" pattern
        merchant_match = re.search(r'merchant\s*:?\s*([a-zA-Z0-9\s]+)', message_body, re.IGNORECASE)
        if merchant_match:
            merchant_name = merchant_match.group(1).strip()
            if merchant_name and len(merchant_name) > 2:
                return merchant_name.title()
        
        return None
    
    def extract_transaction_date(self, message_body: str, received_date: str) -> Optional[str]:
        """Extract transaction date from SMS"""
        # Date patterns in SMS
        date_patterns = [
            r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
            r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
            r'on\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})',
            r'date\s*:?\s*(\d{1,2})[-/](\d{1,2})[-/](\d{4})',
            r'(\d{1,2})[-/](\d{1,2})[-/](\d{2})',  # DD/MM/YY or DD-MM-YY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, message_body)
            if match:
                try:
                    if len(match.group(3)) == 4:  # Full year
                        day, month, year = match.groups()
                    else:  # Short year
                        day, month, year = match.groups()
                        year = '20' + year
                    
                    # Validate date
                    from datetime import datetime
                    date_obj = datetime(int(year), int(month), int(day))
                    return date_obj.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    continue
        
        # If no date found in message, use received date
        try:
            from datetime import datetime
            received_dt = datetime.fromisoformat(received_date.replace('Z', '+00:00'))
            return received_dt.strftime('%Y-%m-%d')
        except:
            return None
    
    def extract_merchant_name(self, message_body: str) -> Optional[str]:
        """Extract merchant name from SMS"""
        message_lower = message_body.lower()
        
        for merchant, patterns in self.merchant_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return merchant.title()
        
        return None

class SMSProcessor:
    """Main SMS processing class"""
    
    def __init__(self):
        self.pattern_matcher = SMSPatternMatcher()
        self.stats = {
            'total_processed': 0,
            'financial_sms': 0,
            'transactions_extracted': 0,
            'errors': 0
        }
    
    async def process_sms_batch(self, user_id: str, sms_messages: List[Dict]) -> Dict[str, Any]:
        """Process a batch of SMS messages"""
        try:
            logger.info(f"📱 Processing {len(sms_messages)} SMS messages for user {user_id}")
            
            processed_sms = []
            financial_sms = []
            
            for sms_data in sms_messages:
                try:
                    # Create SMS message object
                    sms = SMSMessage(
                        sms_id=sms_data.get('id', f"sms_{datetime.now().timestamp()}"),
                        user_id=user_id,
                        provider=sms_data.get('provider', SMSProvider.ANDROID_SMS.value),
                        sms_type=self.pattern_matcher.classify_sms_type(
                            sms_data.get('message_body', ''),
                            sms_data.get('sender_number', '')
                        ),
                        sender_number=sms_data.get('sender_number', ''),
                        sender_name=sms_data.get('sender_name', ''),
                        message_body=sms_data.get('message_body', ''),
                        received_date=datetime.fromisoformat(sms_data.get('received_date', datetime.now().isoformat())),
                        is_financial=self.pattern_matcher.is_financial_sms(
                            sms_data.get('message_body', ''),
                            sms_data.get('sender_number', '')
                        )
                    )
                    
                    processed_sms.append(asdict(sms))
                    
                    if sms.is_financial:
                        financial_sms.append(asdict(sms))
                        self.stats['financial_sms'] += 1
                    
                    self.stats['total_processed'] += 1
                    
                except Exception as e:
                    logger.error(f"❌ Error processing SMS: {e}")
                    self.stats['errors'] += 1
                    continue
            
            # Store processed SMS
            if processed_sms:
                await self._store_sms_messages(user_id, processed_sms)
            
            # Extract financial transactions from financial SMS
            if financial_sms:
                transactions = await self._extract_financial_transactions(user_id, financial_sms)
                self.stats['transactions_extracted'] = len(transactions)
            
            logger.info(f"✅ SMS processing completed: {self.stats}")
            return {
                'success': True,
                'stats': self.stats,
                'processed_sms': len(processed_sms),
                'financial_sms': len(financial_sms),
                'transactions_extracted': self.stats['transactions_extracted']
            }
            
        except Exception as e:
            logger.error(f"❌ Error in SMS batch processing: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }
    
    async def _store_sms_messages(self, user_id: str, sms_messages: List[Dict]) -> None:
        """Store SMS messages in database"""
        try:
            database = db_manager.get_database_for_user(user_id)
            collection = database['sms_data']
            
            # Insert SMS messages
            await collection.insert_many(sms_messages)
            logger.info(f"📱 Stored {len(sms_messages)} SMS messages for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing SMS messages: {e}")
            raise
    
    async def _extract_financial_transactions(self, user_id: str, financial_sms: List[Dict]) -> List[Dict]:
        """Extract financial transactions from SMS messages"""
        transactions = []
        
        for sms in financial_sms:
            try:
                transaction = self._extract_single_transaction(sms)
                if transaction:
                    transaction['user_id'] = user_id
                    transaction['sms_id'] = sms['sms_id']
                    transactions.append(transaction)
                    
            except Exception as e:
                logger.error(f"❌ Error extracting transaction from SMS: {e}")
                continue
        
        # Store transactions
        if transactions:
            await self._store_financial_transactions(transactions)
        
        return transactions
    
    def _extract_single_transaction(self, sms: Dict) -> Optional[Dict]:
        """Extract comprehensive transaction data from SMS"""
        message_body = sms['message_body']
        sender_number = sms['sender_number']
        sender_name = sms.get('sender_name', '')
        received_date = sms.get('received_date', '')
        
        # Extract all financial information
        amount = self.pattern_matcher.extract_amount(message_body)
        bank_name = self.pattern_matcher.extract_bank_name(message_body, sender_number)
        merchant_name = self.pattern_matcher.extract_merchant_name(message_body)
        account_number = self.pattern_matcher.extract_account_number(message_body)
        transaction_type = self.pattern_matcher.extract_transaction_type(message_body)
        transaction_reference = self.pattern_matcher.extract_transaction_reference(message_body)
        balance = self.pattern_matcher.extract_balance(message_body)
        transaction_date = self.pattern_matcher.extract_transaction_date(message_body, received_date)
        
        if not amount:
            return None
        
        # Determine payment method based on sender and content
        payment_method = self._determine_payment_method(message_body, sender_number, sender_name)
        
        # Determine service category
        service_category = self._determine_service_category(message_body, merchant_name, sender_name)
        
        # Calculate extraction confidence based on data completeness
        extraction_confidence = self._calculate_extraction_confidence(
            amount, account_number, transaction_type, bank_name, merchant_name
        )
        
        # Create comprehensive transaction object
        transaction = {
            'transaction_id': f"sms_{sms['sms_id']}_{datetime.now().timestamp()}",
            'sms_id': sms['sms_id'],
            
            # Core transaction data
            'transaction_type': transaction_type,
            'amount': amount,
            'currency': 'INR',
            'transaction_date': transaction_date or (received_date.isoformat() if isinstance(received_date, datetime) else received_date),
            
            # Account and bank information
            'account_number': account_number or 'Unknown',
            'bank_name': bank_name or 'Unknown',
            'card_number': self._extract_card_number(message_body),
            'card_type': self._extract_card_type(message_body),
            
            # Merchant information
            'merchant_canonical': merchant_name or sender_name or 'Unknown',
            'merchant_original': sender_number,
            'service_category': service_category,
            'service_name': merchant_name or sender_name or 'SMS Transaction',
            
            # Payment details
            'payment_method': payment_method,
            'payment_status': 'completed',
            'upi_id': self._extract_upi_id(message_body),
            
            # Transaction references
            'transaction_reference': transaction_reference,
            'invoice_number': self._extract_invoice_number(message_body),
            'order_id': self._extract_order_id(message_body),
            'receipt_number': transaction_reference,
            
            # Balance information
            'available_balance': balance,
            
            # Additional metadata
            'extraction_confidence': extraction_confidence,
            'data_completeness': self._calculate_data_completeness(
                amount, account_number, transaction_type, bank_name, merchant_name, transaction_reference
            ),
            'source': 'sms',
            'sms_message': message_body,  # Store original message for reference
            'extracted_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'user_id': sms.get('user_id')
        }
        
        return transaction
    
    def _determine_payment_method(self, message_body: str, sender_number: str, sender_name: str) -> str:
        """Determine payment method from SMS content"""
        message_lower = message_body.lower()
        sender_lower = sender_name.lower()
        
        # UPI patterns
        if any(pattern in message_lower for pattern in ['upi', 'unified payment']):
            return 'UPI'
        
        # Card patterns
        if any(pattern in message_lower for pattern in ['card', 'credit card', 'debit card']):
            if 'credit' in message_lower:
                return 'credit_card'
            elif 'debit' in message_lower:
                return 'debit_card'
            else:
                return 'card'
        
        # Net banking
        if any(pattern in message_lower for pattern in ['net banking', 'netbanking', 'internet banking']):
            return 'net_banking'
        
        # Bank transfer
        if any(pattern in message_lower for pattern in ['transfer', 'neft', 'imps', 'rtgs']):
            return 'bank_transfer'
        
        # Auto debit
        if any(pattern in message_lower for pattern in ['auto debit', 'automatic', 'standing instruction']):
            return 'auto_debit'
        
        # Default based on sender
        if 'upi' in sender_lower:
            return 'UPI'
        elif 'bank' in sender_lower:
            return 'bank_transfer'
        else:
            return 'SMS'
    
    def _determine_service_category(self, message_body: str, merchant_name: str, sender_name: str) -> str:
        """Determine service category from SMS content"""
        message_lower = message_body.lower()
        
        # Subscription services
        subscription_keywords = ['netflix', 'spotify', 'adobe', 'microsoft', 'google', 'apple', 'youtube', 'prime', 'disney']
        if any(keyword in message_lower for keyword in subscription_keywords):
            return 'subscription'
        
        # Food delivery
        if any(keyword in message_lower for keyword in ['swiggy', 'zomato', 'food', 'delivery']):
            return 'food'
        
        # Transport
        if any(keyword in message_lower for keyword in ['uber', 'ola', 'transport', 'ride']):
            return 'transport'
        
        # E-commerce
        if any(keyword in message_lower for keyword in ['amazon', 'flipkart', 'purchase', 'order']):
            return 'ecommerce'
        
        # Banking
        if any(keyword in message_lower for keyword in ['bank', 'account', 'transfer', 'withdrawal']):
            return 'banking'
        
        # Utilities
        if any(keyword in message_lower for keyword in ['electricity', 'gas', 'water', 'utility']):
            return 'utilities'
        
        # Telecom
        if any(keyword in message_lower for keyword in ['mobile', 'phone', 'recharge', 'bill']):
            return 'telecom'
        
        return 'SMS Transaction'
    
    def _extract_card_number(self, message_body: str) -> Optional[str]:
        """Extract card number (last 4 digits) from SMS"""
        card_patterns = [
            r'card\s*ending\s*(\d{4})',
            r'card\s*(\d{4})',
            r'ending\s*(\d{4})',
            r'(\d{4})\s*ending'
        ]
        
        for pattern in card_patterns:
            match = re.search(pattern, message_body, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_card_type(self, message_body: str) -> Optional[str]:
        """Extract card type from SMS"""
        message_lower = message_body.lower()
        
        if 'credit' in message_lower:
            return 'credit_card'
        elif 'debit' in message_lower:
            return 'debit_card'
        elif 'visa' in message_lower:
            return 'visa'
        elif 'mastercard' in message_lower or 'master' in message_lower:
            return 'mastercard'
        elif 'rupay' in message_lower:
            return 'rupay'
        
        return None
    
    def _extract_upi_id(self, message_body: str) -> Optional[str]:
        """Extract UPI ID from SMS"""
        upi_patterns = [
            r'to\s*([a-zA-Z0-9@.]+)',
            r'from\s*([a-zA-Z0-9@.]+)',
            r'upi\s*id\s*:?\s*([a-zA-Z0-9@.]+)',
            r'([a-zA-Z0-9@.]+@[a-zA-Z]+)'
        ]
        
        for pattern in upi_patterns:
            match = re.search(pattern, message_body, re.IGNORECASE)
            if match:
                upi_id = match.group(1)
                if '@' in upi_id and len(upi_id) > 5:
                    return upi_id
        
        return None
    
    def _extract_invoice_number(self, message_body: str) -> Optional[str]:
        """Extract invoice number from SMS"""
        invoice_patterns = [
            r'invoice\s*(?:no\.?|number)?\s*:?\s*([a-zA-Z0-9]{6,20})',
            r'inv\s*:?\s*([a-zA-Z0-9]{6,20})',
            r'invoice\s*([a-zA-Z0-9]{6,20})'
        ]
        
        for pattern in invoice_patterns:
            match = re.search(pattern, message_body, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_order_id(self, message_body: str) -> Optional[str]:
        """Extract order ID from SMS"""
        order_patterns = [
            r'order\s*(?:id|no\.?|number)?\s*:?\s*([a-zA-Z0-9]{6,20})',
            r'order\s*([a-zA-Z0-9]{6,20})',
            r'order\s*#\s*([a-zA-Z0-9]{6,20})'
        ]
        
        for pattern in order_patterns:
            match = re.search(pattern, message_body, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _calculate_extraction_confidence(self, amount: float, account_number: str, 
                                       transaction_type: str, bank_name: str, merchant_name: str) -> float:
        """Calculate extraction confidence based on data completeness"""
        confidence = 0.5  # Base confidence
        
        if amount:
            confidence += 0.2
        if account_number and account_number != 'Unknown':
            confidence += 0.15
        if transaction_type and transaction_type != 'unknown':
            confidence += 0.1
        if bank_name and bank_name != 'Unknown':
            confidence += 0.1
        if merchant_name and merchant_name != 'Unknown':
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _calculate_data_completeness(self, amount: float, account_number: str, 
                                   transaction_type: str, bank_name: str, merchant_name: str, 
                                   transaction_reference: str) -> float:
        """Calculate data completeness score"""
        total_fields = 6
        completed_fields = 0
        
        if amount:
            completed_fields += 1
        if account_number and account_number != 'Unknown':
            completed_fields += 1
        if transaction_type and transaction_type != 'unknown':
            completed_fields += 1
        if bank_name and bank_name != 'Unknown':
            completed_fields += 1
        if merchant_name and merchant_name != 'Unknown':
            completed_fields += 1
        if transaction_reference:
            completed_fields += 1
        
        return completed_fields / total_fields
    
    async def _store_financial_transactions(self, transactions: List[Dict]) -> None:
        """Store financial transactions in database"""
        try:
            # Use the first transaction's user_id to determine database
            user_id = transactions[0]['user_id']
            database = db_manager.get_database_for_user(user_id)
            collection = database['financial_transactions']
            
            # Insert transactions
            await collection.insert_many(transactions)
            logger.info(f"💰 Stored {len(transactions)} financial transactions from SMS")
            
        except Exception as e:
            logger.error(f"❌ Error storing financial transactions: {e}")
            raise

# Global SMS processor instance
sms_processor = SMSProcessor()

# API functions
async def process_sms_data(user_id: str, sms_messages: List[Dict]) -> Dict[str, Any]:
    """Process SMS data for a user"""
    return await sms_processor.process_sms_batch(user_id, sms_messages)

async def get_sms_data(user_id: str, limit: int = 1000) -> List[Dict]:
    """Get SMS data for a user"""
    try:
        database = db_manager.get_database_for_user(user_id)
        collection = database['sms_data']
        
        cursor = collection.find({'user_id': user_id}).sort('received_date', -1).limit(limit)
        sms_messages = await cursor.to_list(length=limit)
        
        return sms_messages
        
    except Exception as e:
        logger.error(f"❌ Error getting SMS data: {e}")
        return []

async def get_financial_sms(user_id: str, limit: int = 500) -> List[Dict]:
    """Get financial SMS messages for a user"""
    try:
        database = db_manager.get_database_for_user(user_id)
        collection = database['sms_data']
        
        cursor = collection.find({
            'user_id': user_id,
            'is_financial': True
        }).sort('received_date', -1).limit(limit)
        
        financial_sms = await cursor.to_list(length=limit)
        return financial_sms
        
    except Exception as e:
        logger.error(f"❌ Error getting financial SMS: {e}")
        return []

async def get_sms_stats(user_id: str) -> Dict[str, Any]:
    """Get SMS statistics for a user"""
    try:
        database = db_manager.get_database_for_user(user_id)
        collection = database['sms_data']
        
        total_sms = await collection.count_documents({'user_id': user_id})
        financial_sms = await collection.count_documents({
            'user_id': user_id,
            'is_financial': True
        })
        
        return {
            'total_sms': total_sms,
            'financial_sms': financial_sms,
            'financial_percentage': (financial_sms / total_sms * 100) if total_sms > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting SMS stats: {e}")
        return {'total_sms': 0, 'financial_sms': 0, 'financial_percentage': 0} 