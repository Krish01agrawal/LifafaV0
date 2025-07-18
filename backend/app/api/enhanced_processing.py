"""
Enhanced Processing API
=======================

API endpoints for the enhanced email processing system with comprehensive
categorization, extraction, and storage capabilities.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
import logging
import asyncio
from datetime import datetime

# Database
from ..db import (
    financial_transactions_collection, categorized_emails_collection,
    email_logs_collection, subscriptions_collection, travel_bookings_collection,
    job_communications_collection, promotional_emails_collection,
    user_analytics_collection, extraction_failures_collection
)

# Models
from ..models.financial import (
    User, FinancialTransaction, Subscription, TravelBooking,
    JobCommunication, PromotionalEmail, UserAnalytics
)

# Services
from ..enhanced_email_processor import enhanced_processor, ProcessingResult
from ..services.database_service import DatabaseService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/enhanced", tags=["Enhanced Processing"])

@router.post("/process-email")
async def process_email_enhanced(
    email_data: Dict[str, Any],
    user_id: str,
    background_tasks: BackgroundTasks
):
    """
    Process a single email with enhanced categorization and storage.
    
    This endpoint demonstrates the comprehensive database architecture:
    - Stores in email_logs collection
    - Categorizes using LLM and pattern matching
    - Stores in categorized_emails collection
    - Extracts detailed data based on category
    - Stores in specialized collections (financial_transactions, subscriptions, etc.)
    - Updates user analytics
    """
    try:
        logger.info(f"🔄 Processing email for user {user_id}")
        
        # Process email with enhanced processor
        result = await enhanced_processor.process_email_comprehensive(email_data, user_id)
        
        if result.success:
            return {
                "success": True,
                "message": "Email processed successfully",
                "data": {
                    "email_id": result.email_id,
                    "category": result.category,
                    "subcategory": result.subcategory,
                    "confidence": result.confidence,
                    "processing_time_ms": result.processing_time_ms,
                    "stored_collections": result.stored_collections,
                    "extracted_data": result.extracted_data
                }
            }
        else:
            return {
                "success": False,
                "message": "Email processing failed",
                "error": result.error,
                "processing_time_ms": result.processing_time_ms
            }
            
    except Exception as e:
        logger.error(f"❌ Error in enhanced email processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-batch")
async def process_email_batch_enhanced(
    emails: List[Dict[str, Any]],
    user_id: str,
    background_tasks: BackgroundTasks
):
    """
    Process multiple emails in batch with enhanced categorization.
    
    This demonstrates batch processing capabilities with:
    - Parallel processing for efficiency
    - Comprehensive error handling
    - Detailed progress tracking
    - Analytics aggregation
    """
    try:
        logger.info(f"🔄 Processing batch of {len(emails)} emails for user {user_id}")
        
        results = []
        successful = 0
        failed = 0
        
        # Process emails in parallel
        tasks = [
            enhanced_processor.process_email_comprehensive(email, user_id)
            for email in emails
        ]
        
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(batch_results):
            if isinstance(result, Exception):
                failed += 1
                results.append({
                    "email_id": emails[i].get('id', 'unknown'),
                    "success": False,
                    "error": str(result)
                })
            else:
                if result.success:
                    successful += 1
                else:
                    failed += 1
                results.append({
                    "email_id": result.email_id,
                    "success": result.success,
                    "category": result.category,
                    "confidence": result.confidence,
                    "processing_time_ms": result.processing_time_ms,
                    "error": result.error
                })
        
        return {
            "success": True,
            "message": f"Batch processing completed: {successful} successful, {failed} failed",
            "data": {
                "total_emails": len(emails),
                "successful": successful,
                "failed": failed,
                "results": results
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database-stats")
async def get_database_stats(user_id: Optional[str] = None):
    """
    Get comprehensive database statistics showing all collections and their data.
    
    This demonstrates the enhanced database architecture with:
    - Collection counts and statistics
    - User-specific data breakdown
    - Performance metrics
    - Data quality indicators
    """
    try:
        # Get database health
        db_health = await DatabaseService.health_check()
        
        # Get collection statistics
        collection_stats = await DatabaseService.get_collection_stats()
        
        # User-specific statistics
        user_stats = {}
        if user_id:
            user_stats = await _get_user_specific_stats(user_id)
        
        return {
            "success": True,
            "data": {
                "database_health": db_health,
                "collection_statistics": collection_stats,
                "user_statistics": user_stats if user_id else None
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/analytics")
async def get_user_analytics(user_id: str, date: Optional[str] = None):
    """
    Get comprehensive user analytics showing email processing statistics.
    
    This demonstrates the analytics capabilities with:
    - Daily processing statistics
    - Category breakdowns
    - Financial insights
    - Processing efficiency metrics
    """
    try:
        # Build query
        query = {"user_id": user_id}
        if date:
            query["date"] = date
        
        # Get analytics data
        analytics_data = await user_analytics_collection.find(query).to_list(length=None)
        
        # Get financial summary
        financial_summary = await _get_financial_summary(user_id, date)
        
        # Get category breakdown
        category_breakdown = await _get_category_breakdown(user_id, date)
        
        return {
            "success": True,
            "data": {
                "analytics": analytics_data,
                "financial_summary": financial_summary,
                "category_breakdown": category_breakdown
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections/{collection_name}")
async def get_collection_data(
    collection_name: str,
    user_id: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """
    Get data from specific collections to demonstrate the enhanced schema.
    
    Available collections:
    - email_logs: Raw email data
    - categorized_emails: Categorized email data
    - financial_transactions: Financial transaction data
    - subscriptions: Subscription data
    - travel_bookings: Travel booking data
    - job_communications: Job communication data
    - promotional_emails: Promotional email data
    - user_analytics: User analytics data
    """
    try:
        # Map collection names to actual collections
        collection_map = {
            "email_logs": email_logs_collection,
            "categorized_emails": categorized_emails_collection,
            "financial_transactions": financial_transactions_collection,
            "subscriptions": subscriptions_collection,
            "travel_bookings": travel_bookings_collection,
            "job_communications": job_communications_collection,
            "promotional_emails": promotional_emails_collection,
            "user_analytics": user_analytics_collection
        }
        
        if collection_name not in collection_map:
            raise HTTPException(status_code=400, detail=f"Invalid collection: {collection_name}")
        
        collection = collection_map[collection_name]
        
        # Build query
        query = {}
        if user_id:
            query["user_id"] = user_id
        
        # Get data
        data = await collection.find(query).skip(skip).limit(limit).to_list(length=None)
        
        # Get total count
        total_count = await collection.count_documents(query)
        
        return {
            "success": True,
            "data": {
                "collection": collection_name,
                "total_count": total_count,
                "returned_count": len(data),
                "skip": skip,
                "limit": limit,
                "documents": data
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting collection data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/financial-transactions/{user_id}")
async def get_financial_transactions(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    merchant: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """
    Get financial transactions with advanced filtering and aggregation.
    
    This demonstrates the comprehensive financial data model with:
    - Detailed transaction information
    - UPI and bank details
    - Subscription detection
    - Merchant categorization
    - Amount breakdowns
    """
    try:
        # Build query
        query = {"user_id": user_id}
        
        if start_date and end_date:
            query["date"] = {
                "$gte": datetime.fromisoformat(start_date),
                "$lte": datetime.fromisoformat(end_date)
            }
        
        if category:
            query["primary_category"] = category
        
        if merchant:
            query["merchant_canonical"] = {"$regex": merchant, "$options": "i"}
        
        # Get transactions
        transactions = await financial_transactions_collection.find(query).skip(skip).limit(limit).to_list(length=None)
        
        # Get summary statistics
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "total_transactions": {"$sum": 1},
                    "total_amount": {"$sum": "$amount"},
                    "avg_amount": {"$avg": "$amount"},
                    "categories": {"$addToSet": "$primary_category"},
                    "merchants": {"$addToSet": "$merchant_canonical"}
                }
            }
        ]
        
        summary = await financial_transactions_collection.aggregate(pipeline).to_list(length=None)
        
        return {
            "success": True,
            "data": {
                "transactions": transactions,
                "summary": summary[0] if summary else {},
                "query": {
                    "user_id": user_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "category": category,
                    "merchant": merchant
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting financial transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscriptions/{user_id}")
async def get_user_subscriptions(user_id: str):
    """
    Get user subscriptions with detailed information.
    
    This demonstrates the subscription tracking capabilities with:
    - Service categorization
    - Billing frequency
    - Payment methods
    - Renewal dates
    - Trial information
    """
    try:
        # Get active subscriptions
        active_subscriptions = await subscriptions_collection.find({
            "user_id": user_id,
            "status": "active"
        }).to_list(length=None)
        
        # Get subscription summary
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": None,
                    "total_subscriptions": {"$sum": 1},
                    "active_subscriptions": {"$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}},
                    "total_monthly_cost": {"$sum": {"$cond": [{"$eq": ["$billing_frequency", "monthly"]}, "$amount", 0]}},
                    "total_yearly_cost": {"$sum": {"$cond": [{"$eq": ["$billing_frequency", "yearly"]}, "$amount", 0]}},
                    "categories": {"$addToSet": "$service_category"}
                }
            }
        ]
        
        summary = await subscriptions_collection.aggregate(pipeline).to_list(length=None)
        
        return {
            "success": True,
            "data": {
                "subscriptions": active_subscriptions,
                "summary": summary[0] if summary else {}
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting subscriptions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _get_user_specific_stats(user_id: str) -> Dict[str, Any]:
    """Get user-specific database statistics"""
    try:
        stats = {}
        
        # Count documents in each collection for this user
        collections = [
            ("email_logs", email_logs_collection),
            ("categorized_emails", categorized_emails_collection),
            ("financial_transactions", financial_transactions_collection),
            ("subscriptions", subscriptions_collection),
            ("travel_bookings", travel_bookings_collection),
            ("job_communications", job_communications_collection),
            ("promotional_emails", promotional_emails_collection)
        ]
        
        for name, collection in collections:
            count = await collection.count_documents({"user_id": user_id})
            stats[name] = count
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting user stats: {e}")
        return {}

async def _get_financial_summary(user_id: str, date: Optional[str] = None) -> Dict[str, Any]:
    """Get financial summary for user"""
    try:
        query = {"user_id": user_id}
        if date:
            query["date"] = {"$gte": datetime.fromisoformat(date)}
        
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "total_transactions": {"$sum": 1},
                    "total_amount": {"$sum": "$amount"},
                    "avg_amount": {"$avg": "$amount"},
                    "top_categories": {
                        "$top": {
                            "output": {"category": "$primary_category", "amount": "$amount"},
                            "sortBy": {"amount": -1},
                            "n": 5
                        }
                    }
                }
            }
        ]
        
        result = await financial_transactions_collection.aggregate(pipeline).to_list(length=None)
        return result[0] if result else {}
        
    except Exception as e:
        logger.error(f"❌ Error getting financial summary: {e}")
        return {}

async def _get_category_breakdown(user_id: str, date: Optional[str] = None) -> Dict[str, Any]:
    """Get category breakdown for user"""
    try:
        query = {"user_id": user_id}
        if date:
            query["date"] = {"$gte": datetime.fromisoformat(date)}
        
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$primary_category",
                    "count": {"$sum": 1},
                    "total_amount": {"$sum": "$amount"}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        result = await categorized_emails_collection.aggregate(pipeline).to_list(length=None)
        return {"categories": result}
        
    except Exception as e:
        logger.error(f"❌ Error getting category breakdown: {e}")
        return {"categories": []} 