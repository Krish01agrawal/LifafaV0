#!/usr/bin/env python3
"""
Simple Universal Email Processing Demo
=====================================

This demo showcases the universal email processor's capabilities
with direct pattern matching and categorization.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleUniversalProcessor:
    """Simple universal processor for demonstration"""
    
    def __init__(self):
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
    
    def process_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Process email with maximum detail and categorization"""
        original_email = email.get('original_email', {})
        subject = original_email.get('subject', '').lower()
        snippet = original_email.get('snippet', '').lower()
        sender = original_email.get('from', '').lower()
        
        # 1. Check if it's financial
        is_financial = self._is_financial_email(original_email)
        
        # 2. Basic categorization
        category_result = self._categorize_email_basic(original_email)
        
        # 3. Extract financial data if applicable
        extracted_data = None
        if is_financial:
            extracted_data = self._extract_financial_data(original_email)
        
        # 4. Enhance with patterns
        if extracted_data:
            extracted_data = self._enhance_with_merchant_patterns(extracted_data, original_email)
            extracted_data = self._enhance_with_bank_patterns(extracted_data, original_email)
            extracted_data = self._enhance_with_upi_patterns(extracted_data, original_email)
        
        return {
            'email_id': email.get('email_id'),
            'is_financial': is_financial,
            'category': category_result['category'],
            'subcategory': category_result.get('subcategory'),
            'merchant': category_result.get('merchant'),
            'confidence': category_result['confidence'],
            'is_subscription': category_result.get('is_subscription', False),
            'extracted_data': extracted_data,
            'processing_time_ms': 50  # Simulated
        }
    
    def _is_financial_email(self, original_email: Dict[str, Any]) -> bool:
        """Determine if email is financial"""
        subject = original_email.get('subject', '').lower()
        snippet = original_email.get('snippet', '').lower()
        sender = original_email.get('from', '').lower()
        
        financial_keywords = [
            'transaction', 'payment', 'bill', 'subscription', 'upi', 'debit', 'credit',
            'amount', 'rs.', '₹', 'inr', 'bank', 'account', 'transfer', 'alert'
        ]
        
        for keyword in financial_keywords:
            if keyword in subject or keyword in snippet:
                return True
        
        return any(bank in sender for bank in ['bank', 'alerts'])
    
    def _categorize_email_basic(self, original_email: Dict[str, Any]) -> Dict[str, Any]:
        """Basic email categorization"""
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
        
        return {
            'category': 'other',
            'subcategory': 'general',
            'merchant': None,
            'confidence': 0.5,
            'is_subscription': False
        }
    
    def _extract_financial_data(self, original_email: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial data from email"""
        import re
        
        subject = original_email.get('subject', '')
        snippet = original_email.get('snippet', '')
        sender = original_email.get('from', '')
        
        # Extract amount
        amount_match = re.search(r'Rs\.(\d+(?:\.\d{2})?)', snippet)
        amount = float(amount_match.group(1)) if amount_match else 0.0
        
        # Extract transaction ID
        txn_match = re.search(r'(\d{12})', snippet)
        transaction_id = txn_match.group(1) if txn_match else None
        
        # Determine transaction type
        transaction_type = "debit" if "debited" in snippet.lower() else "credit"
        
        # Determine payment method
        payment_method = "upi" if "upi" in snippet.lower() else "unknown"
        
        return {
            'amount': amount,
            'currency': 'INR',
            'transaction_type': transaction_type,
            'payment_method': payment_method,
            'transaction_id': transaction_id,
            'sender': sender,
            'subject': subject,
            'snippet': snippet,
            'extracted_at': datetime.now(),
            'confidence_score': 0.8
        }
    
    def _enhance_with_merchant_patterns(self, transaction: Dict[str, Any], original_email: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance transaction with merchant-specific patterns"""
        subject = original_email.get('subject', '').lower()
        snippet = original_email.get('snippet', '').lower()
        
        for merchant_name, pattern in self.merchant_patterns.items():
            for pattern_text in pattern['patterns']:
                if pattern_text in subject or pattern_text in snippet:
                    transaction['merchant'] = pattern['canonical_name']
                    transaction['merchant_details'] = {
                        'canonical_name': pattern['canonical_name'],
                        'category': pattern['category'],
                        'subcategory': pattern['subcategory'],
                        'patterns': pattern['patterns'],
                        'confidence_score': pattern['confidence'],
                        'detection_method': 'pattern_match'
                    }
                    
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
                            'subscription_frequency': 'monthly'
                        }
                    break
        
        return transaction
    
    def _enhance_with_bank_patterns(self, transaction: Dict[str, Any], original_email: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance transaction with bank-specific patterns"""
        sender = original_email.get('from', '')
        snippet = original_email.get('snippet', '')
        
        for bank_sender, bank_name in self.bank_senders.items():
            if bank_sender in sender:
                transaction['bank_details'] = {
                    'bank_name': bank_name,
                    'account_number': self._extract_account_number(snippet),
                    'account_type': 'savings'
                }
                break
        
        return transaction
    
    def _enhance_with_upi_patterns(self, transaction: Dict[str, Any], original_email: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance transaction with UPI-specific patterns"""
        snippet = original_email.get('snippet', '')
        
        upi_id = self._extract_upi_id(snippet)
        if upi_id:
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
    
    def _extract_account_number(self, text: str) -> str:
        """Extract account number from text"""
        import re
        patterns = [r'account (\d+)', r'A/C (\d+)', r'account number (\d+)']
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_upi_id(self, text: str) -> str:
        """Extract UPI ID from text"""
        import re
        patterns = [r'VPA ([a-zA-Z0-9.]+@[a-zA-Z0-9.]+)', r'UPI ID ([a-zA-Z0-9.]+@[a-zA-Z0-9.]+)']
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None

def run_demo():
    """Run the simple universal processing demo"""
    logger.info("🚀 Starting Simple Universal Email Processing Demo")
    logger.info("=" * 80)
    
    processor = SimpleUniversalProcessor()
    
    # Real transaction data based on user's examples
    real_transactions = [
        {
            "email_id": "686b854a27516062c45aa594",
            "original_email": {
                "subject": "❗  You have done a UPI txn. Check details!",
                "from": "HDFC Bank InstaAlerts <alerts@hdfcbank.net>",
                "snippet": "Dear Customer, Rs.270.00 has been debited from account 8121 to VPA blinkitjkb.rzp@mairtel Blinkit on 07-07-25. Your UPI transaction reference number is 107676449492.",
                "content": "Dear Customer, Rs.270.00 has been debited from account 8121 to VPA blinkitjkb.rzp@mairtel Blinkit on 07-07-25. Your UPI transaction reference number is 107676449492. If you did not authorize this transaction, please contact us immediately.",
                "received_date": "2025-07-07T11:23:49+05:30"
            }
        },
        {
            "email_id": "686b854a27516062c45aa66f",
            "original_email": {
                "subject": "❗  You have done a UPI txn. Check details!",
                "from": "HDFC Bank InstaAlerts <alerts@hdfcbank.net>",
                "snippet": "Dear Customer, Rs.1746.00 has been debited from account 8121 to VPA grofersindia.rzp@hdfcbank GROFERS INDIA PRIVATE LIMITED on 04-07-25.",
                "content": "Dear Customer, Rs.1746.00 has been debited from account 8121 to VPA grofersindia.rzp@hdfcbank GROFERS INDIA PRIVATE LIMITED on 04-07-25. Your UPI transaction reference number is 107526964775.",
                "received_date": "2025-07-04T11:57:49+00:00"
            }
        },
        {
            "email_id": "686b854a27516062c45aa690",
            "original_email": {
                "subject": "❗  You have done a UPI txn. Check details!",
                "from": "HDFC Bank InstaAlerts <alerts@hdfcbank.net>",
                "snippet": "Dear Customer, Rs.649.00 has been debited from account 8121 to VPA netflixupi.payu@hdfcbank NETFLIX COM on 04-07-25.",
                "content": "Dear Customer, Rs.649.00 has been debited from account 8121 to VPA netflixupi.payu@hdfcbank NETFLIX COM on 04-07-25. Your UPI transaction reference number is 100901864757.",
                "received_date": "2025-07-04T10:50:40+05:30"
            }
        },
        {
            "email_id": "686b854a27516062c45aa694",
            "original_email": {
                "subject": "Transaction alert from IDFC FIRST Bank",
                "from": "IDFC First Bank <transaction.alerts@idfcfirstbank.com>",
                "snippet": "Greetings from IDFC FIRST Bank. Dear Mr. Mohammad Danish, Your A/C XXXXXXX5745 has been credited with INR 1,00000.00 on 04/07/2025 10:22.",
                "content": "Greetings from IDFC FIRST Bank. Dear Mr. Mohammad Danish, Greetings from IDFC FIRST Bank. Your A/C XXXXXXX5745 has been credited with INR 1,00000.00 on 04/07/2025 10:22. New balance is INR 2,00422.00CR",
                "received_date": "2025-07-04T10:22:09+05:30"
            }
        },
        {
            "email_id": "686b854b27516062c45aa712",
            "original_email": {
                "subject": "❗  You have done a UPI txn. Check details!",
                "from": "HDFC Bank InstaAlerts <alerts@hdfcbank.net>",
                "snippet": "Dear Customer, Rs.5182.00 has been debited from account 8121 to VPA cred.club@axisb CRED Club on 03-07-25.",
                "content": "Dear Customer, Rs.5182.00 has been debited from account 8121 to VPA cred.club@axisb CRED Club on 03-07-25. Your UPI transaction reference number is 555008180755.",
                "received_date": "2025-07-03T11:36:42+05:30"
            }
        }
    ]
    
    logger.info(f"📧 Processing {len(real_transactions)} real transaction emails...")
    logger.info("-" * 50)
    
    results = []
    for email in real_transactions:
        result = processor.process_email(email)
        results.append(result)
        
        logger.info(f"✅ {result['email_id']}:")
        logger.info(f"   🏷️ Category: {result['category']} ({result['subcategory']})")
        logger.info(f"   🎯 Confidence: {result['confidence']:.2f}")
        logger.info(f"   💰 Financial: {result['is_financial']}")
        logger.info(f"   ⏱️ Processing time: {result['processing_time_ms']}ms")
        
        if result['extracted_data']:
            transaction = result['extracted_data']
            logger.info(f"   💳 Amount: ₹{transaction.get('amount', 0)}")
            logger.info(f"   🏪 Merchant: {transaction.get('merchant', 'Unknown')}")
            logger.info(f"   💳 Payment: {transaction.get('payment_method', 'Unknown')}")
            
            if transaction.get('upi_details'):
                upi = transaction['upi_details']
                logger.info(f"   🔗 UPI: {upi['receiver']['upi_id']} via {upi['receiver']['upi_app']}")
            
            if transaction.get('subscription_details'):
                sub = transaction['subscription_details']
                logger.info(f"   📅 Subscription: {sub['product_name']} ({sub['category']})")
        
        logger.info("")
    
    # Summary statistics
    financial_count = sum(1 for r in results if r['is_financial'])
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    
    logger.info("📊 Processing Summary:")
    logger.info(f"   📧 Total emails: {len(real_transactions)}")
    logger.info(f"   💰 Financial emails: {financial_count}")
    logger.info(f"   🎯 Average confidence: {avg_confidence:.2f}")
    
    # Show detailed categorization breakdown
    logger.info("\n🏷️ Categorization Breakdown:")
    categories = {}
    for result in results:
        cat = result['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for category, count in categories.items():
        logger.info(f"   📂 {category}: {count} emails")
    
    # Show merchant detection
    logger.info("\n🏪 Merchant Detection:")
    merchants = {}
    for result in results:
        if result['merchant']:
            merchants[result['merchant']] = merchants.get(result['merchant'], 0) + 1
    
    for merchant, count in merchants.items():
        logger.info(f"   🏪 {merchant}: {count} transactions")
    
    # Show subscription detection
    logger.info("\n📅 Subscription Detection:")
    subscription_count = sum(1 for r in results if r.get('is_subscription'))
    logger.info(f"   📅 Subscriptions detected: {subscription_count}")
    
    for result in results:
        if result.get('is_subscription') and result['extracted_data']:
            sub = result['extracted_data'].get('subscription_details', {})
            logger.info(f"   📦 {sub.get('product_name', 'Unknown')}: {sub.get('category', 'Unknown')}")
    
    logger.info("\n✅ Simple Universal Processing Demo Completed Successfully!")

if __name__ == "__main__":
    run_demo() 