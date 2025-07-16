#!/usr/bin/env python3
"""
Universal Email Processing Demo
==============================

This demo showcases how the universal email processor handles EVERY email
with maximum detail and categorization based on real data patterns.

Features Demonstrated:
1. Universal email processing (financial + non-financial)
2. Merchant-specific pattern recognition
3. Bank integration for all transaction types
4. Subscription detection with merchant-specific logic
5. Maximum detail extraction (50+ fields)
6. Intelligent categorization (20+ categories)
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our universal processor
from app.universal_email_processor import UniversalEmailProcessor, process_all_emails_universal

class UniversalProcessingDemo:
    """Demo class for universal email processing"""
    
    def __init__(self):
        self.processor = UniversalEmailProcessor()
        self.user_id = "105557939073988392946"
    
    async def run_universal_demo(self):
        """Run the complete universal processing demo"""
        logger.info("🚀 Starting Universal Email Processing Demo")
        logger.info("=" * 80)
        
        # 1. Process real transaction data
        await self.demo_real_transaction_processing()
        
        # 2. Process mixed email types
        await self.demo_mixed_email_processing()
        
        # 3. Demonstrate merchant pattern recognition
        await self.demo_merchant_pattern_recognition()
        
        # 4. Demonstrate bank integration
        await self.demo_bank_integration()
        
        # 5. Demonstrate subscription detection
        await self.demo_subscription_detection()
        
        # 6. Demonstrate comprehensive data storage
        await self.demo_comprehensive_storage()
        
        logger.info("✅ Universal Processing Demo Completed Successfully!")
    
    async def demo_real_transaction_processing(self):
        """Demonstrate processing of real transaction data"""
        logger.info("\n💰 1. REAL TRANSACTION PROCESSING")
        logger.info("-" * 50)
        
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
        
        results = await process_all_emails_universal(real_transactions, self.user_id)
        
        # Show detailed results
        for result in results:
            if result.error:
                logger.error(f"❌ {result.email_id}: {result.error}")
            else:
                logger.info(f"✅ {result.email_id}:")
                logger.info(f"   🏷️ Category: {result.category} ({result.subcategory})")
                logger.info(f"   🎯 Confidence: {result.confidence:.2f}")
                logger.info(f"   💰 Financial: {result.is_financial}")
                logger.info(f"   ⏱️ Processing time: {result.processing_time_ms}ms")
                
                if result.extracted_data and result.extracted_data.get('email_type') != 'non_financial':
                    transaction = result.extracted_data
                    logger.info(f"   💳 Amount: ₹{transaction.get('amount', 0)}")
                    logger.info(f"   🏪 Merchant: {transaction.get('merchant', 'Unknown')}")
                    logger.info(f"   💳 Payment: {transaction.get('payment_method', 'Unknown')}")
                    
                    if transaction.get('upi_details'):
                        upi = transaction['upi_details']
                        logger.info(f"   🔗 UPI: {upi['receiver']['upi_id']} via {upi['receiver']['upi_app']}")
                    
                    if transaction.get('subscription_details'):
                        sub = transaction['subscription_details']
                        logger.info(f"   📅 Subscription: {sub['product_name']} ({sub['category']})")
        
        return results
    
    async def demo_mixed_email_processing(self):
        """Demonstrate processing of mixed email types"""
        logger.info("\n📧 2. MIXED EMAIL PROCESSING")
        logger.info("-" * 50)
        
        # Mixed email types (financial + non-financial)
        mixed_emails = [
            # Financial emails
            {
                "email_id": "financial_1",
                "original_email": {
                    "subject": "Netflix Monthly Subscription Renewed",
                    "from": "netflix@billing.netflix.com",
                    "snippet": "Your Netflix subscription has been renewed for ₹649",
                    "content": "Your Netflix subscription has been renewed for ₹649. Next billing date: 04-08-2025",
                    "received_date": "2025-07-04T10:50:40+05:30"
                }
            },
            {
                "email_id": "financial_2",
                "original_email": {
                    "subject": "Amazon Order Confirmation",
                    "from": "orders@amazon.in",
                    "snippet": "Your order #12345 has been confirmed for ₹1250",
                    "content": "Your order #12345 has been confirmed for ₹1250. Delivery expected in 2-3 days.",
                    "received_date": "2025-07-05T14:30:00+05:30"
                }
            },
            # Non-financial emails
            {
                "email_id": "non_financial_1",
                "original_email": {
                    "subject": "Welcome to our newsletter",
                    "from": "newsletter@company.com",
                    "snippet": "Thank you for subscribing to our newsletter",
                    "content": "Thank you for subscribing to our newsletter. You'll receive updates about our products and services.",
                    "received_date": "2025-07-06T09:00:00+05:30"
                }
            },
            {
                "email_id": "non_financial_2",
                "original_email": {
                    "subject": "Special offer - 50% off on all items",
                    "from": "marketing@store.com",
                    "snippet": "Limited time offer - 50% off on all items",
                    "content": "Limited time offer - 50% off on all items. Valid until 31st July 2025.",
                    "received_date": "2025-07-07T11:00:00+05:30"
                }
            }
        ]
        
        logger.info(f"📧 Processing {len(mixed_emails)} mixed email types...")
        
        results = await process_all_emails_universal(mixed_emails, self.user_id)
        
        # Show categorization results
        financial_count = sum(1 for r in results if r.is_financial)
        non_financial_count = len(results) - financial_count
        
        logger.info(f"📊 Categorization Results:")
        logger.info(f"   💰 Financial emails: {financial_count}")
        logger.info(f"   📧 Non-financial emails: {non_financial_count}")
        
        for result in results:
            logger.info(f"   📧 {result.email_id}: {result.category} (financial: {result.is_financial})")
        
        return results
    
    async def demo_merchant_pattern_recognition(self):
        """Demonstrate merchant-specific pattern recognition"""
        logger.info("\n🏪 3. MERCHANT PATTERN RECOGNITION")
        logger.info("-" * 50)
        
        # Test different merchant patterns
        merchant_test_emails = [
            {
                "email_id": "blinkit_test",
                "original_email": {
                    "subject": "Blinkit Order Delivered",
                    "from": "orders@blinkit.com",
                    "snippet": "Your Blinkit order has been delivered",
                    "content": "Your Blinkit order has been delivered successfully.",
                    "received_date": "2025-07-07T12:00:00+05:30"
                }
            },
            {
                "email_id": "netflix_test",
                "original_email": {
                    "subject": "Netflix Payment Successful",
                    "from": "billing@netflix.com",
                    "snippet": "Your Netflix payment of ₹649 has been processed",
                    "content": "Your Netflix payment of ₹649 has been processed successfully.",
                    "received_date": "2025-07-04T10:50:40+05:30"
                }
            },
            {
                "email_id": "amazon_test",
                "original_email": {
                    "subject": "Amazon Order Shipped",
                    "from": "shipment-tracking@amazon.in",
                    "snippet": "Your Amazon order has been shipped",
                    "content": "Your Amazon order has been shipped and is on its way.",
                    "received_date": "2025-07-05T15:00:00+05:30"
                }
            },
            {
                "email_id": "cred_test",
                "original_email": {
                    "subject": "CRED Payment Reminder",
                    "from": "reminders@cred.club",
                    "snippet": "Your credit card bill is due soon",
                    "content": "Your credit card bill is due soon. Pay with CRED for rewards.",
                    "received_date": "2025-07-06T10:00:00+05:30"
                }
            }
        ]
        
        logger.info(f"🏪 Testing merchant pattern recognition for {len(merchant_test_emails)} emails...")
        
        for email in merchant_test_emails:
            result = await self.processor.process_email_universal(email, self.user_id)
            
            logger.info(f"✅ {email['email_id']}:")
            logger.info(f"   🏪 Detected Merchant: {result.extracted_data.get('merchant_details', {}).get('canonical_name', 'None') if result.extracted_data else 'None'}")
            logger.info(f"   🏷️ Category: {result.category}")
            logger.info(f"   📂 Subcategory: {result.subcategory}")
            logger.info(f"   🎯 Confidence: {result.confidence:.2f}")
            
            if result.extracted_data and result.extracted_data.get('merchant_details'):
                merchant = result.extracted_data['merchant_details']
                logger.info(f"   🔍 Patterns: {merchant.get('patterns', [])}")
                logger.info(f"   📊 Detection Method: {merchant.get('detection_method', 'Unknown')}")
    
    async def demo_bank_integration(self):
        """Demonstrate bank integration for all transaction types"""
        logger.info("\n🏦 4. BANK INTEGRATION")
        logger.info("-" * 50)
        
        # Test different bank patterns
        bank_test_emails = [
            {
                "email_id": "hdfc_test",
                "original_email": {
                    "subject": "HDFC Bank Statement",
                    "from": "statements@hdfcbank.net",
                    "snippet": "Your monthly statement is ready for download",
                    "content": "Your monthly statement for account ****8121 is ready for download.",
                    "received_date": "2025-07-01T09:00:00+05:30"
                }
            },
            {
                "email_id": "idfc_test",
                "original_email": {
                    "subject": "IDFC First Bank Transaction Alert",
                    "from": "transaction.alerts@idfcfirstbank.com",
                    "snippet": "Your account has been credited with INR 50000.00",
                    "content": "Your account XXXXXXX5745 has been credited with INR 50000.00.",
                    "received_date": "2025-07-02T11:00:00+05:30"
                }
            },
            {
                "email_id": "icici_test",
                "original_email": {
                    "subject": "ICICI Bank UPI Transaction",
                    "from": "alerts@icicibank.com",
                    "snippet": "Rs.1500.00 has been debited via UPI",
                    "content": "Rs.1500.00 has been debited from your account via UPI transaction.",
                    "received_date": "2025-07-03T14:30:00+05:30"
                }
            }
        ]
        
        logger.info(f"🏦 Testing bank integration for {len(bank_test_emails)} emails...")
        
        for email in bank_test_emails:
            result = await self.processor.process_email_universal(email, self.user_id)
            
            logger.info(f"✅ {email['email_id']}:")
            logger.info(f"   🏦 Detected Bank: {result.extracted_data.get('bank_details', {}).get('bank_name', 'None') if result.extracted_data else 'None'}")
            logger.info(f"   🏷️ Category: {result.category}")
            logger.info(f"   📂 Subcategory: {result.subcategory}")
            logger.info(f"   🎯 Confidence: {result.confidence:.2f}")
            
            if result.extracted_data and result.extracted_data.get('bank_details'):
                bank = result.extracted_data['bank_details']
                logger.info(f"   📊 Account Number: {bank.get('account_number', 'Masked')}")
                logger.info(f"   🏦 Account Type: {bank.get('account_type', 'Unknown')}")
    
    async def demo_subscription_detection(self):
        """Demonstrate subscription detection with merchant-specific logic"""
        logger.info("\n📅 5. SUBSCRIPTION DETECTION")
        logger.info("-" * 50)
        
        # Test subscription detection
        subscription_test_emails = [
            {
                "email_id": "netflix_subscription",
                "original_email": {
                    "subject": "Netflix Monthly Payment",
                    "from": "billing@netflix.com",
                    "snippet": "Your Netflix subscription payment of ₹649 has been processed",
                    "content": "Your Netflix subscription payment of ₹649 has been processed successfully. Next billing date: 04-08-2025",
                    "received_date": "2025-07-04T10:50:40+05:30"
                }
            },
            {
                "email_id": "spotify_subscription",
                "original_email": {
                    "subject": "Spotify Premium Renewal",
                    "from": "billing@spotify.com",
                    "snippet": "Your Spotify Premium subscription has been renewed",
                    "content": "Your Spotify Premium subscription has been renewed for ₹119. Next billing date: 15-08-2025",
                    "received_date": "2025-07-15T12:00:00+05:30"
                }
            },
            {
                "email_id": "blinkit_order",  # Should NOT be detected as subscription
                "original_email": {
                    "subject": "Blinkit Order Confirmation",
                    "from": "orders@blinkit.com",
                    "snippet": "Your Blinkit order for ₹270 has been confirmed",
                    "content": "Your Blinkit order for ₹270 has been confirmed. Delivery expected in 10 minutes.",
                    "received_date": "2025-07-07T11:23:49+05:30"
                }
            }
        ]
        
        logger.info(f"📅 Testing subscription detection for {len(subscription_test_emails)} emails...")
        
        for email in subscription_test_emails:
            result = await self.processor.process_email_universal(email, self.user_id)
            
            logger.info(f"✅ {email['email_id']}:")
            logger.info(f"   📅 Is Subscription: {result.extracted_data.get('is_subscription', False) if result.extracted_data else False}")
            logger.info(f"   🏷️ Category: {result.category}")
            logger.info(f"   🎯 Confidence: {result.confidence:.2f}")
            
            if result.extracted_data and result.extracted_data.get('subscription_details'):
                sub = result.extracted_data['subscription_details']
                logger.info(f"   📦 Product: {sub.get('product_name', 'Unknown')}")
                logger.info(f"   📂 Category: {sub.get('category', 'Unknown')}")
                logger.info(f"   🔄 Frequency: {sub.get('subscription_frequency', 'Unknown')}")
                logger.info(f"   🎯 Detection Reasons: {sub.get('detection_reasons', [])}")
    
    async def demo_comprehensive_storage(self):
        """Demonstrate comprehensive data storage for every email"""
        logger.info("\n💾 6. COMPREHENSIVE DATA STORAGE")
        logger.info("-" * 50)
        
        # Create a comprehensive example
        comprehensive_email = {
            "email_id": "comprehensive_example",
            "original_email": {
                "subject": "❗  You have done a UPI txn. Check details!",
                "from": "HDFC Bank InstaAlerts <alerts@hdfcbank.net>",
                "snippet": "Dear Customer, Rs.649.00 has been debited from account 8121 to VPA netflixupi.payu@hdfcbank NETFLIX COM on 04-07-25.",
                "content": "Dear Customer, Rs.649.00 has been debited from account 8121 to VPA netflixupi.payu@hdfcbank NETFLIX COM on 04-07-25. Your UPI transaction reference number is 100901864757. If you did not authorize this transaction, please contact us immediately.",
                "received_date": "2025-07-04T10:50:40+05:30"
            }
        }
        
        logger.info("💾 Processing comprehensive email with maximum detail...")
        
        result = await self.processor.process_email_universal(comprehensive_email, self.user_id)
        
        if result.extracted_data and result.extracted_data.get('email_type') != 'non_financial':
            transaction = result.extracted_data
            
            logger.info("📊 Comprehensive Data Extracted:")
            logger.info(f"   💰 Amount: ₹{transaction.get('amount', 0)}")
            logger.info(f"   🏪 Merchant: {transaction.get('merchant', 'Unknown')}")
            logger.info(f"   💳 Payment Method: {transaction.get('payment_method', 'Unknown')}")
            logger.info(f"   🏷️ Transaction Type: {transaction.get('transaction_type', 'Unknown')}")
            logger.info(f"   🎯 Confidence: {transaction.get('confidence_score', 0):.2f}")
            
            # Merchant details
            if transaction.get('merchant_details'):
                merchant = transaction['merchant_details']
                logger.info(f"   🏪 Merchant Details:")
                logger.info(f"      - Canonical Name: {merchant.get('canonical_name')}")
                logger.info(f"      - Category: {merchant.get('category')}")
                logger.info(f"      - Subcategory: {merchant.get('subcategory')}")
                logger.info(f"      - Patterns: {merchant.get('patterns')}")
                logger.info(f"      - Confidence: {merchant.get('confidence_score'):.2f}")
            
            # UPI details
            if transaction.get('upi_details'):
                upi = transaction['upi_details']
                logger.info(f"   💳 UPI Details:")
                logger.info(f"      - UPI ID: {upi['receiver']['upi_id']}")
                logger.info(f"      - UPI App: {upi['receiver']['upi_app']}")
                logger.info(f"      - Transaction Reference: {upi.get('transaction_reference')}")
            
            # Bank details
            if transaction.get('bank_details'):
                bank = transaction['bank_details']
                logger.info(f"   🏦 Bank Details:")
                logger.info(f"      - Bank Name: {bank.get('bank_name')}")
                logger.info(f"      - Account Number: {bank.get('account_number', 'Masked')}")
                logger.info(f"      - Account Type: {bank.get('account_type')}")
            
            # Subscription details
            if transaction.get('subscription_details'):
                sub = transaction['subscription_details']
                logger.info(f"   📅 Subscription Details:")
                logger.info(f"      - Product: {sub.get('product_name')}")
                logger.info(f"      - Category: {sub.get('category')}")
                logger.info(f"      - Type: {sub.get('type')}")
                logger.info(f"      - Frequency: {sub.get('subscription_frequency')}")
                logger.info(f"      - Detection Reasons: {sub.get('detection_reasons')}")
            
            # Email metadata
            if transaction.get('email_metadata'):
                email_meta = transaction['email_metadata']
                logger.info(f"   📧 Email Metadata:")
                logger.info(f"      - Subject: {email_meta.get('subject')}")
                logger.info(f"      - Sender: {email_meta.get('sender')}")
                logger.info(f"      - Importance Score: {email_meta.get('importance_score'):.2f}")
                logger.info(f"      - Is Financial: {email_meta.get('is_financial_email')}")
                logger.info(f"      - Is Promotional: {email_meta.get('is_promotional')}")
            
            # Extraction metadata
            if transaction.get('extraction_metadata'):
                extract_meta = transaction['extraction_metadata']
                logger.info(f"   🔍 Extraction Metadata:")
                logger.info(f"      - Method: {extract_meta.get('extraction_method')}")
                logger.info(f"      - Version: {extract_meta.get('extraction_version')}")
                logger.info(f"      - Model: {extract_meta.get('model_used')}")
                logger.info(f"      - Data Completeness: {extract_meta.get('data_completeness'):.2f}")
        
        logger.info(f"⏱️ Total processing time: {result.processing_time_ms}ms")
        logger.info(f"🎯 Final confidence: {result.confidence:.2f}")

async def main():
    """Main demo function"""
    demo = UniversalProcessingDemo()
    await demo.run_universal_demo()

if __name__ == "__main__":
    asyncio.run(main()) 