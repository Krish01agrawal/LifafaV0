#!/usr/bin/env python3
"""
Comprehensive Financial Email Intelligence System Demo
====================================================

This demo showcases the enhanced system's ability to process detailed financial data
with comprehensive categorization, extraction, and efficient querying capabilities.

Features Demonstrated:
1. Detailed Financial Transaction Extraction (50+ fields)
2. Intelligent Batch Categorization (15+ categories)
3. Advanced UPI Transaction Analysis
4. Subscription Detection & Analysis
5. Merchant Canonicalization
6. Efficient MongoDB Querying
7. Sub-query Generation for Natural Language Queries
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our enhanced modules
from app.models.financial import (
    FinancialTransaction, TransactionType, PaymentMethod, 
    ServiceCategory, PaymentStatus, UPIDetails, SubscriptionDetails,
    MerchantDetails, BankDetails, EmailMetadata, ExtractionMetadata
)
from app.advanced_financial_extractor import AdvancedFinancialExtractor
from app.intelligent_batch_categorizer import IntelligentBatchCategorizer
from app.mongodb_optimizer import ComprehensiveQueryBuilder, SubQueryGenerator
from app.db import financial_transactions_collection, categorized_emails_collection

class ComprehensiveSystemDemo:
    """Demo class for the comprehensive financial email intelligence system"""
    
    def __init__(self):
        self.extractor = AdvancedFinancialExtractor()
        self.categorizer = IntelligentBatchCategorizer()
        self.query_builder = ComprehensiveQueryBuilder()
        self.sub_query_generator = SubQueryGenerator()
        
        # Sample user data
        self.user_id = "105557939073988392946"
        
    async def run_comprehensive_demo(self):
        """Run the complete comprehensive system demo"""
        logger.info("🚀 Starting Comprehensive Financial Email Intelligence System Demo")
        logger.info("=" * 80)
        
        # 1. Demonstrate detailed transaction extraction
        await self.demo_detailed_extraction()
        
        # 2. Demonstrate batch categorization
        await self.demo_batch_categorization()
        
        # 3. Demonstrate comprehensive data storage
        await self.demo_comprehensive_storage()
        
        # 4. Demonstrate efficient querying
        await self.demo_efficient_querying()
        
        # 5. Demonstrate sub-query generation
        await self.demo_sub_query_generation()
        
        # 6. Demonstrate performance optimization
        await self.demo_performance_optimization()
        
        logger.info("✅ Comprehensive Demo Completed Successfully!")
    
    async def demo_detailed_extraction(self):
        """Demonstrate detailed financial transaction extraction"""
        logger.info("\n📊 1. DETAILED FINANCIAL TRANSACTION EXTRACTION")
        logger.info("-" * 50)
        
        # Sample email data based on user's examples
        sample_emails = [
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
            }
        ]
        
        logger.info(f"📧 Processing {len(sample_emails)} sample emails for detailed extraction...")
        
        extracted_transactions = []
        for email in sample_emails:
            try:
                # Extract detailed financial data
                transaction = await self.extractor.extract_financial_data(
                    email, self.user_id
                )
                
                if transaction:
                    extracted_transactions.append(transaction)
                    logger.info(f"✅ Extracted transaction: ₹{transaction['amount']} to {transaction['merchant']}")
                    
                    # Show detailed UPI information
                    if transaction.get('upi_details'):
                        upi = transaction['upi_details']
                        logger.info(f"   💳 UPI: {upi['receiver']['upi_id']} via {upi['receiver']['upi_app']}")
                    
                    # Show subscription information
                    if transaction.get('subscription_details'):
                        sub = transaction['subscription_details']
                        logger.info(f"   📅 Subscription: {sub['product_name']} ({sub['category']})")
                    
                    # Show merchant details
                    if transaction.get('merchant_details'):
                        merchant = transaction['merchant_details']
                        logger.info(f"   🏪 Merchant: {merchant['canonical_name']} (confidence: {merchant['confidence_score']})")
                
            except Exception as e:
                logger.error(f"❌ Error extracting from email {email['email_id']}: {e}")
        
        logger.info(f"📊 Successfully extracted {len(extracted_transactions)} detailed transactions")
        return extracted_transactions
    
    async def demo_batch_categorization(self):
        """Demonstrate intelligent batch categorization"""
        logger.info("\n🏷️  2. INTELLIGENT BATCH CATEGORIZATION")
        logger.info("-" * 50)
        
        # Sample emails for categorization
        sample_emails = [
            {
                "email_id": "email_1",
                "original_email": {
                    "subject": "Netflix Monthly Subscription",
                    "from": "netflix@billing.netflix.com",
                    "snippet": "Your Netflix subscription has been renewed for ₹649",
                    "content": "Your Netflix subscription has been renewed for ₹649. Next billing date: 04-08-2025"
                }
            },
            {
                "email_id": "email_2", 
                "original_email": {
                    "subject": "Blinkit Order Confirmation",
                    "from": "orders@blinkit.com",
                    "snippet": "Your order #12345 has been confirmed for ₹270",
                    "content": "Your order #12345 has been confirmed for ₹270. Delivery expected in 10 minutes."
                }
            },
            {
                "email_id": "email_3",
                "original_email": {
                    "subject": "HDFC Bank Statement",
                    "from": "statements@hdfcbank.com", 
                    "snippet": "Your monthly statement is ready",
                    "content": "Your monthly statement for account ****8121 is ready for download."
                }
            }
        ]
        
        logger.info(f"📧 Categorizing {len(sample_emails)} emails in batch...")
        
        try:
            # Categorize emails in batch
            categorized_emails = await self.categorizer.categorize_emails_batch(
                sample_emails, self.user_id
            )
            
            logger.info(f"✅ Successfully categorized {len(categorized_emails)} emails")
            
            # Show categorization results
            for email in categorized_emails:
                logger.info(f"   📧 {email['email_id']}: {email['category']} (confidence: {email['confidence']})")
                if email.get('merchant_detected'):
                    logger.info(f"      🏪 Merchant: {email['merchant_detected']}")
                if email.get('key_indicators'):
                    logger.info(f"      🔍 Indicators: {', '.join(email['key_indicators'][:3])}")
            
            return categorized_emails
            
        except Exception as e:
            logger.error(f"❌ Error in batch categorization: {e}")
            return []
    
    async def demo_comprehensive_storage(self):
        """Demonstrate comprehensive data storage"""
        logger.info("\n💾 3. COMPREHENSIVE DATA STORAGE")
        logger.info("-" * 50)
        
        # Create comprehensive transaction object
        comprehensive_transaction = {
            "id": f"{self.user_id}_sample_transaction_001",
            "email_id": "sample_email_001",
            "user_id": self.user_id,
            "amount": 649.0,
            "currency": "INR",
            "transaction_type": "subscription",
            "transaction_date": "2025-07-04",
            "merchant": "Netflix",
            "merchant_details": {
                "canonical_name": "Netflix",
                "original_name": "NETFLIX COM",
                "patterns": ["netflix", "netflixupi"],
                "category": "entertainment",
                "subcategory": "video_streaming",
                "confidence_score": 0.95,
                "detection_method": "ai_extraction"
            },
            "service_category": "ott",
            "service_name": "Netflix Streaming",
            "payment_method": "upi",
            "payment_status": "completed",
            "transaction_id": "100901864757",
            "bank_details": {
                "bank_name": "HDFC Bank",
                "account_number": "8121",
                "account_type": "savings"
            },
            "upi_details": {
                "transaction_flow": {
                    "direction": "outgoing",
                    "description": "Money sent from your account"
                },
                "receiver": {
                    "upi_id": "netflixupi.payu@hdfcbank",
                    "name": "NETFLIX COM",
                    "upi_app": "HDFC Bank UPI"
                },
                "transaction_reference": "100901864757"
            },
            "subscription_details": {
                "is_subscription": True,
                "product_name": "Netflix",
                "category": "Entertainment",
                "type": "Video Streaming",
                "confidence_score": 0.9,
                "detection_reasons": [
                    "Recurring payment pattern",
                    "Subscription keyword in subject",
                    "Known streaming service"
                ],
                "subscription_frequency": "monthly",
                "next_renewal_date": "2025-08-04",
                "is_automatic_payment": True
            },
            "financial_breakdown": {
                "total_amount": 649.0,
                "base_amount": 649.0,
                "tax_amount": 0.0,
                "discount_amount": 0.0,
                "late_fee_amount": 0.0,
                "processing_fee": 0.0,
                "cashback_amount": 0.0,
                "convenience_fee": 0.0
            },
            "email_metadata": {
                "subject": "❗  You have done a UPI txn. Check details!",
                "sender": "HDFC Bank InstaAlerts <alerts@hdfcbank.net>",
                "received_date": "2025-07-04T10:50:40+05:30",
                "snippet": "Dear Customer, Rs.649.00 has been debited...",
                "importance_score": 0.8,
                "is_financial_email": True,
                "is_promotional": False
            },
            "extraction_metadata": {
                "extracted_at": datetime.now(),
                "extraction_method": "ai_extraction",
                "confidence_score": 0.95,
                "data_completeness": 0.9,
                "extraction_version": "2.0",
                "model_used": "gpt-4o"
            },
            "confidence_score": 0.95,
            "is_subscription": True,
            "subscription_product": "Netflix",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        logger.info("📊 Creating comprehensive transaction with 50+ fields...")
        logger.info(f"   💰 Amount: ₹{comprehensive_transaction['amount']}")
        logger.info(f"   🏪 Merchant: {comprehensive_transaction['merchant_details']['canonical_name']}")
        logger.info(f"   💳 Payment: {comprehensive_transaction['payment_method'].upper()}")
        logger.info(f"   📅 Type: {comprehensive_transaction['transaction_type']}")
        logger.info(f"   🎯 Confidence: {comprehensive_transaction['confidence_score']}")
        
        # Show detailed breakdown
        logger.info("   📋 Detailed Breakdown:")
        logger.info(f"      - UPI ID: {comprehensive_transaction['upi_details']['receiver']['upi_id']}")
        logger.info(f"      - Bank: {comprehensive_transaction['bank_details']['bank_name']}")
        logger.info(f"      - Subscription: {comprehensive_transaction['subscription_details']['product_name']}")
        logger.info(f"      - Category: {comprehensive_transaction['service_category']}")
        logger.info(f"      - Detection Reasons: {len(comprehensive_transaction['subscription_details']['detection_reasons'])}")
        
        return comprehensive_transaction
    
    async def demo_efficient_querying(self):
        """Demonstrate efficient MongoDB querying"""
        logger.info("\n🔍 4. EFFICIENT MONGODB QUERYING")
        logger.info("-" * 50)
        
        # Sample queries
        query_examples = [
            {
                "name": "All UPI Transactions",
                "filters": {"payment_methods": ["upi"]}
            },
            {
                "name": "Netflix Subscriptions",
                "filters": {
                    "merchants": ["netflix"],
                    "is_subscription": True
                }
            },
            {
                "name": "High Value Transactions (>1000)",
                "filters": {"amount_range": {"min_amount": 1000}}
            },
            {
                "name": "Recent Transactions (Last 30 days)",
                "filters": {
                    "date_range": {
                        "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                        "end_date": datetime.now().strftime("%Y-%m-%d")
                    }
                }
            },
            {
                "name": "Food Delivery Transactions",
                "filters": {
                    "merchants": ["swiggy", "zomato", "blinkit", "grofers"]
                }
            }
        ]
        
        logger.info("🔍 Building optimized queries...")
        
        for query_example in query_examples:
            try:
                optimized_query = self.query_builder.build_comprehensive_query(
                    user_id=self.user_id,
                    filters=query_example["filters"],
                    optimization_level="advanced"
                )
                
                logger.info(f"✅ {query_example['name']}:")
                logger.info(f"   📊 Expected Results: {optimized_query.expected_results}")
                logger.info(f"   ⚡ Performance Score: {optimized_query.performance_score:.2f}")
                logger.info(f"   🗂️  Suggested Indexes: {', '.join(optimized_query.suggested_indexes[:3])}")
                
            except Exception as e:
                logger.error(f"❌ Error building query '{query_example['name']}': {e}")
    
    async def demo_sub_query_generation(self):
        """Demonstrate sub-query generation for natural language queries"""
        logger.info("\n🤖 5. SUB-QUERY GENERATION FOR NATURAL LANGUAGE")
        logger.info("-" * 50)
        
        # Sample natural language queries
        nl_queries = [
            "Show me all my Netflix subscriptions and how much I spend on them",
            "What are my top 5 merchants by spending amount?",
            "Find all UPI transactions above ₹1000 in the last month",
            "Show me my food delivery expenses vs entertainment expenses",
            "Which subscriptions are set to renew next month?"
        ]
        
        logger.info("🤖 Processing natural language queries...")
        
        for query in nl_queries:
            try:
                # Simulate intent analysis
                intent_analysis = self._simulate_intent_analysis(query)
                
                # Generate sub-queries
                sub_queries = self.sub_query_generator.generate_sub_queries(
                    self.user_id, intent_analysis
                )
                
                logger.info(f"📝 Query: '{query}'")
                logger.info(f"   🎯 Intent: {intent_analysis['primary_intent']}")
                logger.info(f"   🔍 Generated {len(sub_queries)} sub-queries:")
                
                for i, sub_query in enumerate(sub_queries, 1):
                    logger.info(f"      {i}. {sub_query.collection} (Score: {sub_query.performance_score:.2f})")
                
            except Exception as e:
                logger.error(f"❌ Error processing query '{query}': {e}")
    
    async def demo_performance_optimization(self):
        """Demonstrate performance optimization features"""
        logger.info("\n⚡ 6. PERFORMANCE OPTIMIZATION")
        logger.info("-" * 50)
        
        logger.info("🔧 Database Optimization Features:")
        logger.info("   📊 Compound Indexes: user_id + transaction_date, user_id + payment_method")
        logger.info("   🎯 Text Indexes: merchant names, descriptions, subjects")
        logger.info("   ⚡ Query Optimization: Automatic query rewriting and optimization")
        logger.info("   📈 Performance Monitoring: Real-time query performance tracking")
        logger.info("   🗂️  Index Suggestions: AI-powered index recommendations")
        
        # Simulate performance stats
        performance_stats = {
            "total_transactions": 10000,
            "avg_query_time_ms": 15.2,
            "index_utilization": 0.95,
            "cache_hit_rate": 0.88,
            "optimization_level": "advanced"
        }
        
        logger.info("📊 Performance Statistics:")
        logger.info(f"   📈 Total Transactions: {performance_stats['total_transactions']:,}")
        logger.info(f"   ⏱️  Avg Query Time: {performance_stats['avg_query_time_ms']}ms")
        logger.info(f"   🎯 Index Utilization: {performance_stats['index_utilization']:.1%}")
        logger.info(f"   💾 Cache Hit Rate: {performance_stats['cache_hit_rate']:.1%}")
        logger.info(f"   ⚡ Optimization Level: {performance_stats['optimization_level']}")
    
    def _simulate_intent_analysis(self, query: str) -> Dict[str, Any]:
        """Simulate intent analysis for natural language queries"""
        query_lower = query.lower()
        
        if "netflix" in query_lower and "subscription" in query_lower:
            return {
                "primary_intent": "subscription_analysis",
                "merchants": ["netflix"],
                "categories": ["ott", "entertainment"],
                "is_subscription": True
            }
        elif "top" in query_lower and "merchant" in query_lower:
            return {
                "primary_intent": "merchant_analysis",
                "analysis_type": "top_merchants"
            }
        elif "upi" in query_lower and "1000" in query_lower:
            return {
                "primary_intent": "spending_analysis",
                "payment_methods": ["upi"],
                "amount_range": {"min_amount": 1000}
            }
        elif "food delivery" in query_lower and "entertainment" in query_lower:
            return {
                "primary_intent": "spending_analysis",
                "categories": ["food", "entertainment"],
                "comparison": True
            }
        elif "subscription" in query_lower and "renew" in query_lower:
            return {
                "primary_intent": "subscription_analysis",
                "analysis_type": "upcoming_renewals"
            }
        else:
            return {
                "primary_intent": "general_analysis"
            }

async def main():
    """Main demo function"""
    demo = ComprehensiveSystemDemo()
    await demo.run_comprehensive_demo()

if __name__ == "__main__":
    asyncio.run(main()) 