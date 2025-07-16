#!/usr/bin/env python3
"""
Check Categorization Progress
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.database_service import DatabaseService
from bson import ObjectId

async def check_progress():
    """Check the categorization progress."""
    try:
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        user_id = '687783628bc131c83fa8ae83'
        user = await db.users.find_one({'_id': ObjectId(user_id)})
        
        if user:
            print("=" * 60)
            print("📊 CATEGORIZATION PROGRESS REPORT")
            print("=" * 60)
            print(f"👤 User: {user.get('email')}")
            print(f"📧 Gmail Sync Status: {user.get('gmail_sync_status')}")
            print(f"🏷️  Categorization Status: {user.get('categorization_status')}")
            print(f"📨 Email Count: {user.get('email_count')}")
            print(f"⏳ Emails to Categorize: {user.get('emails_to_categorize')}")
            print(f"✅ Emails Categorized: {user.get('emails_categorized')}")
            print(f"❌ Emails Failed: {user.get('emails_failed')}")
            
            if user.get('emails_to_categorize', 0) > 0:
                progress = (user.get('emails_categorized', 0) / user.get('emails_to_categorize', 1)) * 100
                print(f"📈 Progress: {progress:.1f}%")
        else:
            print("❌ User not found")
            return
        
        # Check collections
        print("\n" + "=" * 60)
        print("🗂️  COLLECTION STATISTICS")
        print("=" * 60)
        
        financial_count = await db.financial_transactions.count_documents({'user_id': user_id})
        subscription_count = await db.subscriptions.count_documents({'user_id': user_id})
        promo_count = await db.promotional_emails.count_documents({'user_id': user_id})
        travel_count = await db.travel_bookings.count_documents({'user_id': user_id})
        job_count = await db.job_communications.count_documents({'user_id': user_id})
        
        print(f"💰 Financial Transactions: {financial_count}")
        print(f"📺 Subscriptions: {subscription_count}")
        print(f"🎁 Promotional Emails: {promo_count}")
        print(f"✈️  Travel Bookings: {travel_count}")
        print(f"💼 Job Communications: {job_count}")
        
        # Check for detailed data
        if financial_count > 0:
            print("\n" + "=" * 60)
            print("🔍 SAMPLE FINANCIAL TRANSACTION")
            print("=" * 60)
            
            sample = await db.financial_transactions.find_one({'user_id': user_id})
            if sample:
                print(f"Merchant: {sample.get('merchant_name', 'N/A')}")
                print(f"Amount: {sample.get('amount', 'N/A')} {sample.get('currency', 'N/A')}")
                print(f"Payment Method: {sample.get('payment_method', 'N/A')}")
                print(f"Transaction Type: {sample.get('transaction_type', 'N/A')}")
                print(f"UPI ID: {sample.get('upi_details', {}).get('receiver', {}).get('upi_id', 'N/A')}")
                print(f"Bank: {sample.get('bank_details', {}).get('bank_name', 'N/A')}")
                print(f"Is Subscription: {sample.get('is_subscription', 'N/A')}")
        
        if subscription_count > 0:
            print("\n" + "=" * 60)
            print("📺 SAMPLE SUBSCRIPTION")
            print("=" * 60)
            
            sample = await db.subscriptions.find_one({'user_id': user_id})
            if sample:
                print(f"Service: {sample.get('service_name', 'N/A')}")
                print(f"Plan: {sample.get('plan_name', 'N/A')}")
                print(f"Amount: {sample.get('amount', 'N/A')} {sample.get('currency', 'N/A')}")
                print(f"Billing: {sample.get('billing_frequency', 'N/A')}")
        
        if promo_count > 0:
            print("\n" + "=" * 60)
            print("🎁 SAMPLE PROMOTIONAL EMAIL")
            print("=" * 60)
            
            sample = await db.promotional_emails.find_one({'user_id': user_id})
            if sample:
                print(f"Merchant: {sample.get('merchant_name', 'N/A')}")
                print(f"Discount: {sample.get('discount_percentage', 'N/A')}%")
                print(f"Original Price: {sample.get('original_price', 'N/A')} {sample.get('currency', 'N/A')}")
                print(f"Promo Code: {sample.get('promotion_code', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("✅ PROGRESS CHECK COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error checking progress: {e}")
    finally:
        await DatabaseService.close()

if __name__ == "__main__":
    asyncio.run(check_progress()) 