#!/usr/bin/env python3
"""
Enhanced Email Processing Demo
Tests the improved extraction system with detailed data
"""

import asyncio
import json
from datetime import datetime
from app.services.llm_service import llm_service
from app.services.database_service import DatabaseService

async def test_enhanced_extraction():
    """Test enhanced extraction with detailed sample data."""
    
    print("🚀 Testing Enhanced Email Extraction System")
    print("=" * 60)
    
    # Sample emails with detailed data
    sample_emails = [
        {
            "subject": "❗  You have done a UPI txn. Check details!",
            "body": """Dear Customer, Rs.270.00 has been debited from account 8121 to VPA blinkitjkb.rzp@mairtel Blinkit on 07-07-25. Your UPI transaction reference number is 107676449492. If you did not authorize this transaction, please contact us immediately."""
        },
        {
            "subject": "Netflix - Your subscription has been renewed",
            "body": """Hi there,

Your Netflix subscription has been renewed for another month.

Plan: Premium Plan
Amount: ₹649.00
Next billing date: August 4, 2025
Payment method: UPI (netflixupi.payu@hdfcbank)

Your subscription includes:
• 4K Ultra HD streaming
• Watch on 4 devices simultaneously
• Unlimited downloads

Thank you for being a Netflix member!"""
        },
        {
            "subject": "Amazon - 50% OFF on Electronics! Limited Time Offer",
            "body": """Exclusive Offer for You!

Get 50% OFF on selected electronics including smartphones, laptops, and headphones.

Original Price: ₹50,000
Discounted Price: ₹25,000
Savings: ₹25,000

Use Code: ELECTRONICS50
Valid until: July 20, 2025
Minimum purchase: ₹1,000

Terms & Conditions:
• Valid on selected items only
• Cannot be combined with other offers
• Free delivery on orders above ₹499

Shop now: amazon.in/electronics-offer"""
        },
        {
            "subject": "Vodafone - Your bill is ready",
            "body": """Dear Customer,

Your Vodafone postpaid bill for March 2025 is ready.

Bill Details:
• Plan: Vodafone Red Postpaid
• Amount: ₹599.00
• Due Date: March 20, 2025
• Billing Period: March 1-31, 2025

Breakdown:
• Plan charges: ₹499.00
• Data charges: ₹50.00
• SMS charges: ₹25.00
• Taxes: ₹25.00

Payment Methods:
• UPI: vodafone.rzp@hdfcbank
• Net Banking
• Credit/Debit Card

Pay now to avoid late fees."""
        }
    ]
    
    # Test classification
    print("\n📧 Testing Enhanced Email Classification (20+ Categories)")
    print("-" * 50)
    
    for i, email in enumerate(sample_emails, 1):
        category = await llm_service.classify_email(email["subject"], email["body"])
        print(f"Email {i}: {category}")
        print(f"  Subject: {email['subject'][:50]}...")
    
    # Test financial extraction
    print("\n💰 Testing Enhanced Financial Data Extraction")
    print("-" * 50)
    
    financial_email = sample_emails[0]  # UPI transaction
    financial_data = await llm_service.extract_financial_data(
        financial_email["subject"], 
        financial_email["body"]
    )
    
    print("Financial Data Extracted:")
    print(json.dumps(financial_data, indent=2, default=str))
    
    # Test subscription extraction
    print("\n📺 Testing Enhanced Subscription Data Extraction")
    print("-" * 50)
    
    subscription_email = sample_emails[1]  # Netflix
    subscription_data = await llm_service.extract_subscription_data(
        subscription_email["subject"], 
        subscription_email["body"]
    )
    
    print("Subscription Data Extracted:")
    print(json.dumps(subscription_data, indent=2, default=str))
    
    # Test promotional extraction
    print("\n🎁 Testing Enhanced Promotional Data Extraction")
    print("-" * 50)
    
    promo_email = sample_emails[2]  # Amazon offer
    promo_data = await llm_service.extract_promotional_data(
        promo_email["subject"], 
        promo_email["body"]
    )
    
    print("Promotional Data Extracted:")
    print(json.dumps(promo_data, indent=2, default=str))
    
    # Test database storage
    print("\n💾 Testing Database Storage")
    print("-" * 50)
    
    db = DatabaseService.get_database()
    
    # Store test data
    test_user_id = "test_user_123"
    
    # Store financial transaction
    financial_doc = {
        "user_id": test_user_id,
        "email_id": "test_email_1",
        "created_at": datetime.utcnow(),
        **financial_data
    }
    
    result = await db.financial_transactions.insert_one(financial_doc)
    print(f"✅ Financial transaction stored: {result.inserted_id}")
    
    # Store subscription
    subscription_doc = {
        "user_id": test_user_id,
        "email_id": "test_email_2",
        "created_at": datetime.utcnow(),
        **subscription_data
    }
    
    result = await db.subscriptions.insert_one(subscription_doc)
    print(f"✅ Subscription stored: {result.inserted_id}")
    
    # Store promotional
    promo_doc = {
        "user_id": test_user_id,
        "email_id": "test_email_3",
        "created_at": datetime.utcnow(),
        **promo_data
    }
    
    result = await db.promotional_emails.insert_one(promo_doc)
    print(f"✅ Promotional email stored: {result.inserted_id}")
    
    # Query and verify
    print("\n🔍 Verifying Stored Data")
    print("-" * 50)
    
    # Count documents in each collection
    financial_count = await db.financial_transactions.count_documents({"user_id": test_user_id})
    subscription_count = await db.subscriptions.count_documents({"user_id": test_user_id})
    promo_count = await db.promotional_emails.count_documents({"user_id": test_user_id})
    
    print(f"Financial transactions: {financial_count}")
    print(f"Subscriptions: {subscription_count}")
    print(f"Promotional emails: {promo_count}")
    
    # Get sample documents
    financial_sample = await db.financial_transactions.find_one({"user_id": test_user_id})
    subscription_sample = await db.subscriptions.find_one({"user_id": test_user_id})
    promo_sample = await db.promotional_emails.find_one({"user_id": test_user_id})
    
    print("\n📊 Sample Financial Transaction:")
    if financial_sample:
        print(f"  Merchant: {financial_sample.get('merchant_name', 'N/A')}")
        print(f"  Amount: {financial_sample.get('amount', 'N/A')} {financial_sample.get('currency', 'N/A')}")
        print(f"  Payment Method: {financial_sample.get('payment_method', 'N/A')}")
        print(f"  UPI ID: {financial_sample.get('upi_details', {}).get('receiver', {}).get('upi_id', 'N/A')}")
    
    print("\n📺 Sample Subscription:")
    if subscription_sample:
        print(f"  Service: {subscription_sample.get('service_name', 'N/A')}")
        print(f"  Plan: {subscription_sample.get('plan_name', 'N/A')}")
        print(f"  Amount: {subscription_sample.get('amount', 'N/A')} {subscription_sample.get('currency', 'N/A')}")
        print(f"  Billing: {subscription_sample.get('billing_frequency', 'N/A')}")
    
    print("\n🎁 Sample Promotional Email:")
    if promo_sample:
        print(f"  Merchant: {promo_sample.get('merchant_name', 'N/A')}")
        print(f"  Discount: {promo_sample.get('discount_percentage', 'N/A')}%")
        print(f"  Original Price: {promo_sample.get('original_price', 'N/A')} {promo_sample.get('currency', 'N/A')}")
        print(f"  Promo Code: {promo_sample.get('promotion_code', 'N/A')}")
    
    print("\n✅ Enhanced Extraction Demo Completed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_enhanced_extraction()) 