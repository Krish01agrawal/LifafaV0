#!/usr/bin/env python3
"""
Show Financial Transactions Script
==================================

This script shows detailed financial transactions to verify data quality.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from bson import ObjectId

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import required modules
from app.services.database_service import DatabaseService

async def show_financial_transactions():
    """Show detailed financial transactions."""
    try:
        logger.info("💳 Showing detailed financial transactions")
        
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        # Get all financial transactions
        transactions = await db.financial_transactions.find({}).to_list(length=None)
        
        logger.info(f"📊 Found {len(transactions)} financial transactions")
        
        for i, transaction in enumerate(transactions, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"💳 TRANSACTION #{i}")
            logger.info(f"{'='*60}")
            
            # Basic info
            logger.info(f"🆔 ID: {transaction.get('_id')}")
            logger.info(f"👤 User ID: {transaction.get('user_id')}")
            logger.info(f"📧 Email ID: {transaction.get('email_id')}")
            
            # Financial details
            logger.info(f"💰 Amount: {transaction.get('amount')} {transaction.get('currency', 'INR')}")
            logger.info(f"🏢 Merchant: {transaction.get('merchant_name')} ({transaction.get('merchant_canonical')})")
            logger.info(f"📋 Service: {transaction.get('service_name')} ({transaction.get('service_category')})")
            logger.info(f"💳 Transaction Type: {transaction.get('transaction_type')}")
            logger.info(f"📅 Transaction Date: {transaction.get('transaction_date')}")
            logger.info(f"💳 Payment Method: {transaction.get('payment_method')}")
            logger.info(f"📊 Payment Status: {transaction.get('payment_status')}")
            
            # Additional details
            logger.info(f"🧾 Invoice Number: {transaction.get('invoice_number')}")
            logger.info(f"🆔 Order ID: {transaction.get('order_id')}")
            logger.info(f"🧾 Receipt Number: {transaction.get('receipt_number')}")
            logger.info(f"🔄 Transaction Reference: {transaction.get('transaction_reference')}")
            
            # Subscription info
            logger.info(f"📅 Is Subscription: {transaction.get('is_subscription')}")
            logger.info(f"📊 Confidence Score: {transaction.get('confidence_score')}")
            logger.info(f"📊 Extraction Confidence: {transaction.get('extraction_confidence')}")
            
            # Check if it's a food delivery transaction
            merchant_name = transaction.get('merchant_name', '').lower()
            if 'swiggy' in merchant_name or 'zomato' in merchant_name or 'blinkit' in merchant_name:
                logger.info(f"🍕 FOOD DELIVERY TRANSACTION DETECTED!")
            
            # Check data quality
            meaningful_fields = 0
            key_fields = [
                "amount", "merchant_canonical", "merchant_name", 
                "transaction_type", "payment_method", "transaction_reference",
                "invoice_number", "order_id", "receipt_number"
            ]
            
            for field in key_fields:
                value = transaction.get(field)
                if value and value != "" and value != 0:
                    meaningful_fields += 1
            
            logger.info(f"📊 Data Quality: {meaningful_fields}/{len(key_fields)} meaningful fields")
            
            if meaningful_fields >= 2:
                logger.info(f"✅ GOOD QUALITY TRANSACTION")
            else:
                logger.info(f"⚠️ LOW QUALITY TRANSACTION")
        
        # Summary by merchant
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 SUMMARY BY MERCHANT")
        logger.info(f"{'='*60}")
        
        merchant_counts = {}
        for transaction in transactions:
            merchant = transaction.get('merchant_name', 'Unknown')
            merchant_counts[merchant] = merchant_counts.get(merchant, 0) + 1
        
        for merchant, count in merchant_counts.items():
            logger.info(f"🏢 {merchant}: {count} transactions")
        
        # Check for Swiggy specifically
        swiggy_transactions = [t for t in transactions if 'swiggy' in t.get('merchant_name', '').lower()]
        logger.info(f"\n🍕 Swiggy Transactions: {len(swiggy_transactions)}")
        
        for transaction in swiggy_transactions:
            logger.info(f"🍕 Swiggy: {transaction.get('merchant_name')} - {transaction.get('amount')} {transaction.get('currency')} - {transaction.get('service_name')}")
        
        return {
            "total_transactions": len(transactions),
            "swiggy_transactions": len(swiggy_transactions),
            "merchant_counts": merchant_counts
        }
        
    except Exception as e:
        logger.error(f"❌ Error showing transactions: {e}")
        raise

async def main():
    """Main function."""
    try:
        logger.info("🚀 Starting financial transaction analysis")
        
        result = await show_financial_transactions()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📋 FINAL SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"💳 Total transactions: {result['total_transactions']}")
        logger.info(f"🍕 Swiggy transactions: {result['swiggy_transactions']}")
        logger.info(f"🏢 Unique merchants: {len(result['merchant_counts'])}")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 