"""
Enhanced Email Processing System Demo
====================================

This script demonstrates the comprehensive enhanced email processing system
with all the new database collections, models, and features.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample email data for demonstration
SAMPLE_EMAILS = [
    {
        "id": "email_001",
        "email_id": "email_001",
        "gmail_id": "gmail_001",
        "subject": "Netflix Payment Successful - ₹499.00",
        "from": "netflix@netflix.com",
        "to": "user@example.com",
        "snippet": "Your Netflix subscription payment of ₹499.00 has been processed successfully. Your next billing date is December 15, 2024.",
        "body": "Dear User, Your Netflix subscription payment of ₹499.00 has been processed successfully using UPI. Your next billing date is December 15, 2024. Thank you for choosing Netflix!",
        "received_date": datetime.now(),
        "labels": ["INBOX"],
        "is_read": True,
        "importance_score": 8.5,
        "financial": True
    },
    {
        "id": "email_002", 
        "email_id": "email_002",
        "gmail_id": "gmail_002",
        "subject": "HDFC Bank - Transaction Alert",
        "from": "alerts@hdfcbank.net",
        "to": "user@example.com",
        "snippet": "Transaction Alert: ₹1,250.00 debited from your account ending 1234 on 2024-11-15 at 14:30:25",
        "body": "Transaction Alert: ₹1,250.00 has been debited from your account ending 1234 on 2024-11-15 at 14:30:25. Merchant: SWIGGY. Location: Mumbai, India.",
        "received_date": datetime.now() - timedelta(hours=2),
        "labels": ["INBOX"],
        "is_read": True,
        "importance_score": 9.0,
        "financial": True
    },
    {
        "id": "email_003",
        "email_id": "email_003", 
        "gmail_id": "gmail_003",
        "subject": "Amazon Prime - Your subscription has been renewed",
        "from": "prime@amazon.com",
        "to": "user@example.com",
        "snippet": "Your Amazon Prime subscription has been renewed for ₹1,499.00. Next renewal: December 15, 2024",
        "body": "Your Amazon Prime subscription has been renewed for ₹1,499.00. You will be charged on December 15, 2024 for the next billing cycle.",
        "received_date": datetime.now() - timedelta(days=1),
        "labels": ["INBOX"],
        "is_read": True,
        "importance_score": 7.5,
        "financial": True
    },
    {
        "id": "email_004",
        "email_id": "email_004",
        "gmail_id": "gmail_004", 
        "subject": "Interview Invitation - Software Engineer at Google",
        "from": "careers@google.com",
        "to": "user@example.com",
        "snippet": "Congratulations! You have been selected for an interview for the Software Engineer position at Google.",
        "body": "Congratulations! You have been selected for an interview for the Software Engineer position at Google. Please schedule your interview for next week. Salary range: ₹25-35 LPA.",
        "received_date": datetime.now() - timedelta(days=2),
        "labels": ["INBOX"],
        "is_read": False,
        "importance_score": 9.5,
        "financial": False
    },
    {
        "id": "email_005",
        "email_id": "email_005",
        "gmail_id": "gmail_005",
        "subject": "50% OFF on Myntra - Limited Time Offer!",
        "from": "offers@myntra.com", 
        "to": "user@example.com",
        "snippet": "Get 50% OFF on all fashion items. Use code MYNTRA50. Valid until December 31, 2024.",
        "body": "Get 50% OFF on all fashion items at Myntra. Use code MYNTRA50 at checkout. This offer is valid until December 31, 2024. Minimum purchase: ₹999.",
        "received_date": datetime.now() - timedelta(days=3),
        "labels": ["PROMOTIONS"],
        "is_read": False,
        "importance_score": 4.0,
        "financial": False
    },
    {
        "id": "email_006",
        "email_id": "email_006",
        "gmail_id": "gmail_006",
        "subject": "Flight Booking Confirmation - Mumbai to Delhi",
        "from": "bookings@makemytrip.com",
        "to": "user@example.com", 
        "snippet": "Your flight booking is confirmed. Flight: AI-101, Date: December 20, 2024, Amount: ₹8,500",
        "body": "Your flight booking is confirmed. Flight: AI-101 from Mumbai to Delhi on December 20, 2024. Total amount: ₹8,500. PNR: ABC123456.",
        "received_date": datetime.now() - timedelta(days=4),
        "labels": ["INBOX"],
        "is_read": True,
        "importance_score": 8.0,
        "financial": True
    }
]

async def demo_enhanced_system():
    """Demonstrate the enhanced email processing system"""
    
    logger.info("🚀 Starting Enhanced Email Processing System Demo")
    logger.info("=" * 60)
    
    # Initialize database service
    from app.services.database_service import DatabaseService
    await DatabaseService.initialize()
    
    # Import enhanced processor
    from app.enhanced_email_processor import enhanced_processor
    
    # Test user ID
    user_id = "demo_user_123"
    
    logger.info(f"📧 Processing {len(SAMPLE_EMAILS)} sample emails for user: {user_id}")
    logger.info("=" * 60)
    
    # Process each email individually
    for i, email_data in enumerate(SAMPLE_EMAILS, 1):
        logger.info(f"\n📨 Processing Email {i}/{len(SAMPLE_EMAILS)}")
        logger.info(f"Subject: {email_data['subject']}")
        
        try:
            # Process email with enhanced processor
            result = await enhanced_processor.process_email_comprehensive(email_data, user_id)
            
            if result.success:
                logger.info(f"✅ Successfully processed email {result.email_id}")
                logger.info(f"   Category: {result.category}")
                logger.info(f"   Subcategory: {result.subcategory}")
                logger.info(f"   Confidence: {result.confidence:.2f}")
                logger.info(f"   Processing time: {result.processing_time_ms}ms")
                logger.info(f"   Stored in collections: {', '.join(result.stored_collections)}")
                
                if result.extracted_data:
                    logger.info(f"   Extracted data type: {result.extracted_data.get('type')}")
            else:
                logger.error(f"❌ Failed to process email {result.email_id}")
                logger.error(f"   Error: {result.error}")
                
        except Exception as e:
            logger.error(f"❌ Exception processing email {i}: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 Database Statistics After Processing")
    logger.info("=" * 60)
    
    # Get database statistics
    try:
        db_health = await DatabaseService.health_check()
        collection_stats = await DatabaseService.get_collection_stats()
        
        logger.info("Database Health:")
        logger.info(f"  Status: {db_health['status']}")
        logger.info(f"  Collections: {db_health['collections']}")
        logger.info(f"  Data Size: {db_health['data_size']} bytes")
        logger.info(f"  Storage Size: {db_health['storage_size']} bytes")
        
        logger.info("\nCollection Statistics:")
        for collection_name, stats in collection_stats.items():
            if isinstance(stats, dict) and 'document_count' in stats:
                logger.info(f"  {collection_name}: {stats['document_count']} documents")
            else:
                logger.info(f"  {collection_name}: {stats}")
                
    except Exception as e:
        logger.error(f"❌ Error getting database stats: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("🔍 Querying Enhanced Collections")
    logger.info("=" * 60)
    
    # Query different collections
    await query_collections(user_id)
    
    logger.info("\n" + "=" * 60)
    logger.info("📈 User Analytics")
    logger.info("=" * 60)
    
    # Get user analytics
    await get_user_analytics(user_id)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Enhanced Email Processing System Demo Completed!")
    logger.info("=" * 60)

async def query_collections(user_id: str):
    """Query different collections to show the enhanced data"""
    
    from app.db import (
        email_logs_collection, categorized_emails_collection,
        financial_transactions_collection, subscriptions_collection,
        travel_bookings_collection, job_communications_collection,
        promotional_emails_collection
    )
    
    collections = [
        ("Email Logs", email_logs_collection),
        ("Categorized Emails", categorized_emails_collection),
        ("Financial Transactions", financial_transactions_collection),
        ("Subscriptions", subscriptions_collection),
        ("Travel Bookings", travel_bookings_collection),
        ("Job Communications", job_communications_collection),
        ("Promotional Emails", promotional_emails_collection)
    ]
    
    for name, collection in collections:
        try:
            count = await collection.count_documents({"user_id": user_id})
            logger.info(f"{name}: {count} documents")
            
            if count > 0:
                # Get a sample document
                sample = await collection.find_one({"user_id": user_id})
                if sample:
                    logger.info(f"  Sample: {sample.get('subject', sample.get('merchant', 'N/A'))}")
                    
        except Exception as e:
            logger.error(f"❌ Error querying {name}: {e}")

async def get_user_analytics(user_id: str):
    """Get and display user analytics"""
    
    from app.db import user_analytics_collection
    
    try:
        # Get today's analytics
        today = datetime.now().strftime("%Y-%m-%d")
        analytics = await user_analytics_collection.find_one({
            "user_id": user_id,
            "date": today
        })
        
        if analytics:
            logger.info("Today's Analytics:")
            logger.info(f"  Emails Categorized: {analytics.get('emails_categorized', 0)}")
            logger.info(f"  Emails Extracted: {analytics.get('emails_extracted', 0)}")
            logger.info(f"  Financial Transactions: {analytics.get('financial_transactions', 0)}")
            logger.info(f"  Subscriptions: {analytics.get('subscriptions', 0)}")
            logger.info(f"  Travel Bookings: {analytics.get('travel_bookings', 0)}")
            logger.info(f"  Job Communications: {analytics.get('job_communications', 0)}")
            logger.info(f"  Promotional Emails: {analytics.get('promotional_emails', 0)}")
            logger.info(f"  Total Spending: ₹{analytics.get('total_spending', 0):.2f}")
        else:
            logger.info("No analytics data found for today")
            
    except Exception as e:
        logger.error(f"❌ Error getting user analytics: {e}")

async def demo_api_endpoints():
    """Demonstrate the new API endpoints"""
    
    logger.info("\n" + "=" * 60)
    logger.info("🌐 API Endpoints Demo")
    logger.info("=" * 60)
    
    # This would typically be done with HTTP requests
    # For demo purposes, we'll show the endpoint structure
    
    endpoints = [
        "POST /enhanced/process-email - Process single email with enhanced categorization",
        "POST /enhanced/process-batch - Process multiple emails in batch",
        "GET /enhanced/database-stats - Get comprehensive database statistics",
        "GET /enhanced/user/{user_id}/analytics - Get user analytics",
        "GET /enhanced/collections/{collection_name} - Query specific collections",
        "GET /enhanced/financial-transactions/{user_id} - Get financial transactions",
        "GET /enhanced/subscriptions/{user_id} - Get user subscriptions"
    ]
    
    for endpoint in endpoints:
        logger.info(f"  {endpoint}")
    
    logger.info("\nThese endpoints demonstrate:")
    logger.info("  ✅ Enhanced email categorization and storage")
    logger.info("  ✅ Comprehensive data extraction")
    logger.info("  ✅ Specialized collection storage")
    logger.info("  ✅ User analytics and insights")
    logger.info("  ✅ Advanced querying capabilities")

def print_system_overview():
    """Print an overview of the enhanced system"""
    
    logger.info("\n" + "=" * 60)
    logger.info("🏗️ Enhanced Email Processing System Overview")
    logger.info("=" * 60)
    
    logger.info("📊 Database Collections:")
    collections = [
        "users - User accounts and authentication",
        "user_sessions - User session management", 
        "email_logs - Raw email data from Gmail",
        "emails - Processed email data",
        "categorized_emails - Categorized email data",
        "financial_transactions - Financial transaction data",
        "subscriptions - Subscription tracking",
        "travel_bookings - Travel booking data",
        "job_communications - Job-related communications",
        "promotional_emails - Promotional email data",
        "email_queue - Email processing queue",
        "extraction_failures - Failed extraction tracking",
        "query_logs - Query analytics",
        "user_analytics - User analytics data",
        "chats - Chat conversation data"
    ]
    
    for collection in collections:
        logger.info(f"  • {collection}")
    
    logger.info("\n🎯 Key Features:")
    features = [
        "Comprehensive email categorization (20+ categories)",
        "Advanced financial data extraction",
        "Subscription detection and tracking",
        "Travel booking extraction",
        "Job communication analysis",
        "Promotional email processing",
        "Real-time user analytics",
        "Enhanced database indexing",
        "Parallel batch processing",
        "Comprehensive error handling"
    ]
    
    for feature in features:
        logger.info(f"  • {feature}")
    
    logger.info("\n🔧 Technical Improvements:")
    improvements = [
        "Enhanced Pydantic models with comprehensive schemas",
        "Optimized MongoDB indexes for performance",
        "Structured data extraction with confidence scores",
        "Multi-level categorization system",
        "Comprehensive analytics and reporting",
        "Scalable architecture for large datasets"
    ]
    
    for improvement in improvements:
        logger.info(f"  • {improvement}")

if __name__ == "__main__":
    # Print system overview
    print_system_overview()
    
    # Run the demo
    asyncio.run(demo_enhanced_system())
    
    # Show API endpoints
    asyncio.run(demo_api_endpoints()) 