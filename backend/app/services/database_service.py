"""
Database Service
================

Service layer for database operations.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from typing import Optional
import logging
from app.config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseService:
    """MongoDB database service with connection management."""
    
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def initialize(cls) -> None:
        """Initialize database connection."""
        try:
            cls._client = AsyncIOMotorClient(settings.mongodb_url)
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
            
            # Users collection indexes
            await db.users.create_index([("email", ASCENDING)], unique=True)
            await db.users.create_index([("google_auth_token", ASCENDING)])
            
            # Email logs collection indexes
            await db.email_logs.create_index([("user_id", ASCENDING), ("gmail_id", ASCENDING)], unique=True)
            await db.email_logs.create_index([("user_id", ASCENDING), ("received_date", DESCENDING)])
            await db.email_logs.create_index([("classification_status", ASCENDING)])
            await db.email_logs.create_index([("body_hash", ASCENDING)])
            
            # Financial transactions collection indexes
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("transaction_date", DESCENDING)])
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("merchant_canonical", ASCENDING)])
            await db.financial_transactions.create_index([("user_id", ASCENDING), ("service_category", ASCENDING)])
            await db.financial_transactions.create_index([("email_id", ASCENDING)])
            
            # Subscriptions collection indexes
            await db.subscriptions.create_index([("user_id", ASCENDING), ("service_name", ASCENDING)])
            await db.subscriptions.create_index([("user_id", ASCENDING), ("next_billing_date", ASCENDING)])
            
            # Travel bookings collection indexes
            await db.travel_bookings.create_index([("user_id", ASCENDING), ("travel_date", DESCENDING)])
            await db.travel_bookings.create_index([("user_id", ASCENDING), ("booking_type", ASCENDING)])
            
            # Job communications collection indexes
            await db.job_communications.create_index([("user_id", ASCENDING), ("communication_type", ASCENDING)])
            await db.job_communications.create_index([("user_id", ASCENDING), ("company_name", ASCENDING)])
            
            # Promotional emails collection indexes
            await db.promotional_emails.create_index([("user_id", ASCENDING), ("valid_until", ASCENDING)])
            await db.promotional_emails.create_index([("user_id", ASCENDING), ("merchant_canonical", ASCENDING)])
            
            # Query logs collection indexes
            await db.query_logs.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
            await db.query_logs.create_index([("query_text", "text")])
            
            # Extraction failures collection indexes
            await db.extraction_failures.create_index([("email_id", ASCENDING)])
            await db.extraction_failures.create_index([("is_resolved", ASCENDING)])
            
            # Queue collection indexes (for MongoDB-based queue)
            await db.email_queue.create_index([("status", ASCENDING), ("priority", DESCENDING), ("created_at", ASCENDING)])
            await db.email_queue.create_index([("user_id", ASCENDING)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
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
            
            return {
                "status": "healthy",
                "database": settings.mongodb_database,
                "collections": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "indexes": stats.get("indexes", 0)
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            } 