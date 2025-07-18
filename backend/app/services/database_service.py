"""
Database Service
================

Service layer for database operations with enhanced collections for comprehensive email categorization.
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from typing import Optional
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseService:
    """MongoDB database service with connection management and enhanced collections."""
    
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def initialize(cls) -> None:
        """Initialize database connection."""
        try:
            # Use cloud MongoDB URI from environment variable
            mongodb_url = os.getenv("MONGO_URI", settings.mongodb_url)
            
            # Import URL encoding utilities
            from urllib.parse import quote_plus, urlparse, urlunparse
            
            # Parse and encode the URI to handle special characters in username/password
            try:
                parsed = urlparse(mongodb_url)
                if parsed.username and parsed.password:
                    # Encode username and password
                    encoded_username = quote_plus(parsed.username)
                    encoded_password = quote_plus(parsed.password)
                    
                    # Reconstruct the URI with encoded credentials
                    netloc = f"{encoded_username}:{encoded_password}@{parsed.hostname}"
                    if parsed.port:
                        netloc += f":{parsed.port}"
                    
                    encoded_uri = urlunparse((
                        parsed.scheme,
                        netloc,
                        parsed.path,
                        parsed.params,
                        parsed.query,
                        parsed.fragment
                    ))
                    
                    logger.info("🔐 MongoDB URI encoded successfully")
                    mongodb_url = encoded_uri
                    
            except Exception as encoding_error:
                logger.warning(f"⚠️ Failed to encode MongoDB URI: {encoding_error}")
                # Continue with original URI
            
            cls._client = AsyncIOMotorClient(mongodb_url)
            cls._database = cls._client[settings.mongodb_database]
            
            # Test connection
            await cls._client.admin.command('ping')
            
            # Create indexes
            await cls._create_indexes()
            
            logger.info(f"Connected to MongoDB: {settings.mongodb_database}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def close(cls) -> None:
        """Close database connection."""
        if cls._client is not None:
            cls._client.close()
            logger.info("MongoDB connection closed")
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if cls._database is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return cls._database
    
    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        """Get client instance."""
        if cls._client is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return cls._client
    
    @classmethod
    async def _create_indexes(cls) -> None:
        """Create database indexes for optimal performance."""
        try:
            db = cls.get_database()
            
            # ============================================================================
            # CORE USER & AUTHENTICATION COLLECTIONS
            # ============================================================================
            
            # Users collection indexes
            await db.users.create_index([("user_id", ASCENDING)], unique=True)
            await db.users.create_index([("email", ASCENDING)], unique=True)
            await db.users.create_index([("google_auth_token", ASCENDING)])
            await db.users.create_index([("last_sync_date", DESCENDING)])
            await db.users.create_index([("sync_status", ASCENDING)])
            await db.users.create_index([("categorization_status", ASCENDING)])
            
            # User sessions collection indexes
            await db.user_sessions.create_index([("user_id", ASCENDING), ("session_id", ASCENDING)], unique=True)
            await db.user_sessions.create_index([("access_token", ASCENDING)])
            await db.user_sessions.create_index([("is_active", ASCENDING), ("expires_at", ASCENDING)])
            await db.user_sessions.create_index([("last_activity", DESCENDING)])
            
            # ============================================================================
            # RAW EMAIL COLLECTIONS
            # ============================================================================
            
            # Email logs collection indexes
            await db.email_logs.create_index([("user_id", ASCENDING), ("gmail_id", ASCENDING)], unique=True)
            await db.email_logs.create_index([("user_id", ASCENDING), ("received_date", DESCENDING)])
            await db.email_logs.create_index([("user_id", ASCENDING), ("classification_status", ASCENDING)])
            await db.email_logs.create_index([("user_id", ASCENDING), ("email_category", ASCENDING)])
            await db.email_logs.create_index([("user_id", ASCENDING), ("financial", ASCENDING)])
            await db.email_logs.create_index([("body_hash", ASCENDING)])
            await db.email_logs.create_index([("subject_hash", ASCENDING)])
            await db.email_logs.create_index([("sender_domain", ASCENDING)])
            await db.email_logs.create_index([("importance_score", DESCENDING)])
            
            # Emails collection indexes
            await db.emails.create_index([("user_id", ASCENDING), ("date", DESCENDING)])
            await db.emails.create_index([("user_id", ASCENDING), ("financial", ASCENDING)])
            await db.emails.create_index([("user_id", ASCENDING), ("importance_score", DESCENDING)])
            await db.emails.create_index([("user_id", ASCENDING), ("sender_domain", ASCENDING)])
            await db.emails.create_index([("user_id", ASCENDING), ("is_transactional", ASCENDING)])
            
            # ============================================================================
            # CATEGORIZED EMAIL COLLECTIONS
            # ============================================================================
            
            # Categorized emails collection indexes
            await db.categorized_emails.create_index([("user_id", ASCENDING), ("email_id", ASCENDING)], unique=True)
            await db.categorized_emails.create_index([("user_id", ASCENDING), ("primary_category", ASCENDING)])
            await db.categorized_emails.create_index([("user_id", ASCENDING), ("secondary_category", ASCENDING)])
            await db.categorized_emails.create_index([("user_id", ASCENDING), ("merchant_detected", ASCENDING)])
            await db.categorized_emails.create_index([("user_id", ASCENDING), ("transaction_likely", ASCENDING)])
            await db.categorized_emails.create_index([("user_id", ASCENDING), ("priority", ASCENDING)])
            await db.categorized_emails.create_index([("user_id", ASCENDING), ("categorized_at", DESCENDING)])
            await db.categorized_emails.create_index([("user_id", ASCENDING), ("financial_data_extracted", ASCENDING)])
            
            # ============================================================================
            # FINANCIAL TRANSACTIONS COLLECTION
            # ============================================================================
            
            # Financial transactions collection indexes
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("email_id", ASCENDING)], unique=True)
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("date", DESCENDING)])
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("transaction_date", DESCENDING)])
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("merchant_canonical", ASCENDING)])
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("service_category", ASCENDING)])
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("payment_method", ASCENDING)])
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("transaction_type", ASCENDING)])
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("amount", DESCENDING)])
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("is_subscription", ASCENDING)])
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("primary_category", ASCENDING)])
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("secondary_category", ASCENDING)])
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("confidence_score", DESCENDING)])
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("extraction_confidence", DESCENDING)])
            await db.financial_transactions.create_index([("transaction_id", ASCENDING)])
            await db.financial_transactions.create_index([("upi_details.receiver.upi_id", ASCENDING)])
            await db.financial_transactions.create_index([("bank_details.bank_name", ASCENDING)])
            
            # ============================================================================
            # SPECIALIZED CATEGORY COLLECTIONS
            # ============================================================================
            
            # Subscriptions collection indexes
            await db.subscriptions.create_index([("user_id", ASCENDING), ("email_id", ASCENDING)], unique=True)
            await db.subscriptions.create_index([("user_id", ASCENDING), ("service_name", ASCENDING)])
            await db.subscriptions.create_index([("user_id", ASCENDING), ("service_category", ASCENDING)])
            await db.subscriptions.create_index([("user_id", ASCENDING), ("next_billing_date", ASCENDING)])
            await db.subscriptions.create_index([("user_id", ASCENDING), ("status", ASCENDING)])
            await db.subscriptions.create_index([("user_id", ASCENDING), ("is_automatic_payment", ASCENDING)])
            await db.subscriptions.create_index([("user_id", ASCENDING), ("billing_frequency", ASCENDING)])
            await db.subscriptions.create_index([("upi_id", ASCENDING)])
            
            # Travel bookings collection indexes
            await db.travel_bookings.create_index([("user_id", ASCENDING), ("email_id", ASCENDING)], unique=True)
            await db.travel_bookings.create_index([("user_id", ASCENDING), ("travel_date", DESCENDING)])
            await db.travel_bookings.create_index([("user_id", ASCENDING), ("booking_type", ASCENDING)])
            await db.travel_bookings.create_index([("user_id", ASCENDING), ("service_provider", ASCENDING)])
            await db.travel_bookings.create_index([("user_id", ASCENDING), ("booking_status", ASCENDING)])
            await db.travel_bookings.create_index([("user_id", ASCENDING), ("from_location.city", ASCENDING)])
            await db.travel_bookings.create_index([("user_id", ASCENDING), ("to_location.city", ASCENDING)])
            await db.travel_bookings.create_index([("booking_reference", ASCENDING)])
            await db.travel_bookings.create_index([("pnr_number", ASCENDING)])
            
            # Job communications collection indexes
            await db.job_communications.create_index([("user_id", ASCENDING), ("email_id", ASCENDING)], unique=True)
            await db.job_communications.create_index([("user_id", ASCENDING), ("communication_type", ASCENDING)])
            await db.job_communications.create_index([("user_id", ASCENDING), ("company_name", ASCENDING)])
            await db.job_communications.create_index([("user_id", ASCENDING), ("application_status", ASCENDING)])
            await db.job_communications.create_index([("user_id", ASCENDING), ("interview_date", ASCENDING)])
            await db.job_communications.create_index([("user_id", ASCENDING), ("urgency_level", ASCENDING)])
            await db.job_communications.create_index([("user_id", ASCENDING), ("position_title", ASCENDING)])
            await db.job_communications.create_index([("application_id", ASCENDING)])
            await db.job_communications.create_index([("job_id", ASCENDING)])
            
            # Promotional emails collection indexes
            await db.promotional_emails.create_index([("user_id", ASCENDING), ("email_id", ASCENDING)], unique=True)
            await db.promotional_emails.create_index([("user_id", ASCENDING), ("valid_until", ASCENDING)])
            await db.promotional_emails.create_index([("user_id", ASCENDING), ("merchant_canonical", ASCENDING)])
            await db.promotional_emails.create_index([("user_id", ASCENDING), ("promotion_type", ASCENDING)])
            await db.promotional_emails.create_index([("user_id", ASCENDING), ("offer_category", ASCENDING)])
            await db.promotional_emails.create_index([("user_id", ASCENDING), ("is_expired", ASCENDING)])
            await db.promotional_emails.create_index([("user_id", ASCENDING), ("is_used", ASCENDING)])
            await db.promotional_emails.create_index([("promotion_code", ASCENDING)])
            await db.promotional_emails.create_index([("valid_from", ASCENDING), ("valid_until", ASCENDING)])
            
            # ============================================================================
            # SYSTEM & ANALYTICS COLLECTIONS
            # ============================================================================
            
            # Email queue collection indexes
            await db.email_queue.create_index([("user_id", ASCENDING), ("email_id", ASCENDING)], unique=True)
            await db.email_queue.create_index([("status", ASCENDING), ("priority", DESCENDING), ("created_at", ASCENDING)])
            await db.email_queue.create_index([("user_id", ASCENDING), ("status", ASCENDING)])
            await db.email_queue.create_index([("queue_type", ASCENDING), ("status", ASCENDING)])
            await db.email_queue.create_index([("retry_after", ASCENDING)])
            await db.email_queue.create_index([("worker_id", ASCENDING)])
            
            # Extraction failures collection indexes
            await db.extraction_failures.create_index([("user_id", ASCENDING), ("email_id", ASCENDING)])
            await db.extraction_failures.create_index([("email_id", ASCENDING)])
            await db.extraction_failures.create_index([("failure_type", ASCENDING)])
            await db.extraction_failures.create_index([("is_resolved", ASCENDING)])
            await db.extraction_failures.create_index([("error_code", ASCENDING)])
            await db.extraction_failures.create_index([("created_at", DESCENDING)])
            
            # Query logs collection indexes
            await db.query_logs.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
            await db.query_logs.create_index([("user_id", ASCENDING), ("query_type", ASCENDING)])
            await db.query_logs.create_index([("user_id", ASCENDING), ("success", ASCENDING)])
            await db.query_logs.create_index([("query_text", "text")])
            await db.query_logs.create_index([("session_id", ASCENDING)])
            
            # User analytics collection indexes
            await db.user_analytics.create_index([("user_id", ASCENDING), ("date", ASCENDING)], unique=True)
            await db.user_analytics.create_index([("user_id", ASCENDING), ("date", DESCENDING)])
            await db.user_analytics.create_index([("date", ASCENDING)])
            
            # Chats collection indexes
            await db.chats.create_index([("user_id", ASCENDING), ("session_id", ASCENDING)])
            await db.chats.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)])
            await db.chats.create_index([("session_id", ASCENDING), ("timestamp", ASCENDING)])
            await db.chats.create_index([("message_type", ASCENDING)])
            
            logger.info("✅ Enhanced database indexes created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create indexes: {e}")
            raise
    
    @classmethod
    async def health_check(cls) -> dict:
        """Check database health."""
        try:
            db = cls.get_database()
            
            # Test connection
            await db.command("ping")
            
            # Get database stats
            stats = await db.command("dbStats")
            
            # Get collection counts
            collections = await db.list_collection_names()
            collection_stats = {}
            
            for collection_name in collections:
                try:
                    count = await db[collection_name].count_documents({})
                    collection_stats[collection_name] = count
                except Exception as e:
                    collection_stats[collection_name] = f"Error: {str(e)}"
            
            return {
                "status": "healthy",
                "database": settings.mongodb_database,
                "collections": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "indexes": stats.get("indexes", 0),
                "collection_stats": collection_stats
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    @classmethod
    async def get_collection_stats(cls) -> dict:
        """Get detailed collection statistics."""
        try:
            db = cls.get_database()
            collections = await db.list_collection_names()
            stats = {}
            
            for collection_name in collections:
                try:
                    count = await db[collection_name].count_documents({})
                    indexes = await db[collection_name].index_information()
                    stats[collection_name] = {
                        "document_count": count,
                        "index_count": len(indexes)
                    }
                except Exception as e:
                    stats[collection_name] = {
                        "error": str(e)
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)} 