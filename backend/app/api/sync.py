from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from app.services.gmail_service import gmail_service
from app.services.database_service import DatabaseService
from app.services.cache_service import cache
from app.workers.email_worker import queue_email_processing

logger = logging.getLogger(__name__)

router = APIRouter()

class SyncRequest(BaseModel):
    user_id: str
    credentials: Dict[str, Any]
    max_emails: Optional[int] = 500
    query: Optional[str] = None

class SyncResponse(BaseModel):
    user_id: str
    status: str
    emails_fetched: int
    emails_queued: int
    sync_started_at: datetime
    estimated_completion: Optional[datetime] = None

class SyncStatusResponse(BaseModel):
    user_id: str
    status: str
    emails_fetched: int
    emails_processed: int
    emails_failed: int
    sync_started_at: datetime
    last_updated: datetime
    estimated_completion: Optional[datetime] = None

@router.post("/gmail", response_model=SyncResponse)
async def sync_gmail_emails(
    request: SyncRequest,
    background_tasks: BackgroundTasks
):
    """Start Gmail synchronization for a user."""
    try:
        logger.info(f"Starting Gmail sync for user: {request.user_id}")
        
        # Get database
        db = DatabaseService.get_database()
        
        # Update user sync status
        await db.users.update_one(
            {"_id": request.user_id},
            {
                "$set": {
                    "gmail_sync_status": "in_progress",
                    "sync_started_at": datetime.utcnow(),
                    "last_synced": datetime.utcnow()
                }
            }
        )
        
        # Fetch emails from Gmail
        emails = await gmail_service.fetch_emails(
            user_id=request.user_id,
            credentials_dict=request.credentials,
            max_results=request.max_emails,
            query=request.query
        )
        
        # Store raw emails in database
        email_docs = []
        for email in emails:
            email_doc = {
                "user_id": request.user_id,
                "gmail_id": email["gmail_id"],
                "email_subject": email["subject"],
                "email_body": email["body"],
                "body_hash": email["body_hash"],
                "from_address": email["from_address"],
                "to_address": email["to_address"],
                "received_date": email["received_date"],
                "classification_status": "pending",
                "processing_attempts": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            email_docs.append(email_doc)
        
        # Bulk insert emails
        if email_docs:
            result = await db.email_logs.insert_many(email_docs, ordered=False)
            emails_inserted = len(result.inserted_ids)
        else:
            emails_inserted = 0
        
        # Queue emails for processing
        email_ids = [str(doc["_id"]) for doc in email_docs]
        if email_ids:
            background_tasks.add_task(queue_email_processing, request.user_id, email_ids)
        
        # Update user with sync results
        await db.users.update_one(
            {"_id": request.user_id},
            {
                "$set": {
                    "email_count": emails_inserted,
                    "emails_to_categorize": emails_inserted,
                    "emails_categorized": 0,
                    "emails_failed": 0,
                    "last_synced": datetime.utcnow()
                }
            }
        )
        
        # Cache sync status
        sync_status = {
            "user_id": request.user_id,
            "status": "in_progress",
            "emails_fetched": emails_inserted,
            "emails_processed": 0,
            "emails_failed": 0,
            "sync_started_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        }
        cache.set(f"sync_status:{request.user_id}", sync_status, ttl=3600)
        
        logger.info(f"Gmail sync completed for user {request.user_id}: {emails_inserted} emails")
        
        return SyncResponse(
            user_id=request.user_id,
            status="started",
            emails_fetched=emails_inserted,
            emails_queued=len(email_ids),
            sync_started_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error in Gmail sync: {e}")
        
        # Update user status to failed
        try:
            db = DatabaseService.get_database()
            await db.users.update_one(
                {"_id": request.user_id},
                {
                    "$set": {
                        "gmail_sync_status": "failed",
                        "last_synced": datetime.utcnow()
                    }
                }
            )
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.get("/status/{user_id}", response_model=SyncStatusResponse)
async def get_sync_status(user_id: str):
    """Get synchronization status for a user."""
    try:
        # Check cache first
        cached_status = cache.get(f"sync_status:{user_id}")
        if cached_status:
            return SyncStatusResponse(**cached_status)
        
        # Get from database
        db = DatabaseService.get_database()
        
        # Get user info
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get email processing stats
        total_emails = await db.email_logs.count_documents({"user_id": user_id})
        processed_emails = await db.email_logs.count_documents({
            "user_id": user_id,
            "classification_status": {"$in": ["classified", "extracted"]}
        })
        failed_emails = await db.email_logs.count_documents({
            "user_id": user_id,
            "classification_status": "failed"
        })
        
        # Determine status
        if user.get("gmail_sync_status") == "in_progress":
            status = "in_progress"
        elif user.get("gmail_sync_status") == "failed":
            status = "failed"
        elif processed_emails == total_emails and total_emails > 0:
            status = "completed"
        else:
            status = "pending"
        
        sync_status = SyncStatusResponse(
            user_id=user_id,
            status=status,
            emails_fetched=total_emails,
            emails_processed=processed_emails,
            emails_failed=failed_emails,
            sync_started_at=user.get("sync_started_at", datetime.utcnow()),
            last_updated=user.get("last_synced", datetime.utcnow())
        )
        
        # Cache the status
        cache.set(f"sync_status:{user_id}", sync_status.dict(), ttl=300)
        
        return sync_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sync status")

@router.post("/retry/{user_id}")
async def retry_failed_emails(user_id: str):
    """Retry processing of failed emails."""
    try:
        db = DatabaseService.get_database()
        
        # Find failed emails
        failed_emails = await db.email_logs.find({
            "user_id": user_id,
            "classification_status": "failed"
        }).to_list(length=None)
        
        if not failed_emails:
            return {"message": "No failed emails to retry"}
        
        # Reset status and queue for processing
        email_ids = []
        for email in failed_emails:
            await db.email_logs.update_one(
                {"_id": email["_id"]},
                {
                    "$set": {
                        "classification_status": "pending",
                        "processing_attempts": 0,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            email_ids.append(str(email["_id"]))
        
        # Queue for processing
        from app.workers.email_worker import queue_email_processing
        await queue_email_processing(user_id, email_ids)
        
        logger.info(f"Retrying {len(email_ids)} failed emails for user {user_id}")
        
        return {
            "message": f"Retrying {len(email_ids)} failed emails",
            "emails_queued": len(email_ids)
        }
        
    except Exception as e:
        logger.error(f"Error retrying failed emails: {e}")
        raise HTTPException(status_code=500, detail="Failed to retry emails")

@router.delete("/cancel/{user_id}")
async def cancel_sync(user_id: str):
    """Cancel ongoing synchronization."""
    try:
        db = DatabaseService.get_database()
        
        # Update user status
        await db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "gmail_sync_status": "cancelled",
                    "last_synced": datetime.utcnow()
                }
            }
        )
        
        # Clear cache
        cache.delete(f"sync_status:{user_id}")
        
        logger.info(f"Sync cancelled for user {user_id}")
        
        return {"message": "Sync cancelled successfully"}
        
    except Exception as e:
        logger.error(f"Error cancelling sync: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel sync")

@router.get("/quota/{user_id}")
async def get_quota_info(user_id: str):
    """Get Gmail API quota information."""
    try:
        db = DatabaseService.get_database()
        
        # Get user credentials
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.get("google_auth_token"):
            raise HTTPException(status_code=400, detail="User not authenticated")
        
        # Check quota
        quota_info = await gmail_service.check_quota(user["google_auth_token"])
        
        return quota_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quota info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quota info")

@router.post("/categorize/{user_id}")
async def categorize_existing_emails(user_id: str, background_tasks: BackgroundTasks):
    """Trigger categorization of existing emails in email_logs."""
    try:
        logger.info(f"Starting categorization for user: {user_id}")
        
        # Get database
        db = DatabaseService.get_database()
        
        # Find all emails that need processing (pending, unclassified, or classified but not extracted)
        pending_emails = await db.email_logs.find({
            "user_id": user_id,
            "$or": [
                {"classification_status": {"$in": ["pending", None]}},
                {"classification_status": {"$exists": False}},
                {"classification_status": "classified", "email_category": {"$in": ["finance", "travel", "job", "promotion", "subscription", "shopping", "utilities", "insurance", "real_estate", "health", "education", "entertainment"]}}
            ]
        }).to_list(length=None)
        
        if not pending_emails:
            return {
                "user_id": user_id,
                "status": "no_emails_to_process",
                "message": "No pending emails found to categorize",
                "emails_found": 0
            }
        
        # Get email IDs
        email_ids = [str(email["_id"]) for email in pending_emails]
        
        logger.info(f"Found {len(email_ids)} emails to categorize for user {user_id}")
        
        # Queue for processing
        background_tasks.add_task(queue_email_processing, user_id, email_ids)
        
        # Update user status
        await db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "categorization_status": "in_progress",
                    "categorization_started_at": datetime.utcnow(),
                    "emails_to_categorize": len(email_ids)
                }
            }
        )
        
        return {
            "user_id": user_id,
            "status": "categorization_started",
            "emails_found": len(email_ids),
            "message": f"Started categorization of {len(email_ids)} emails",
            "started_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error starting categorization: {e}")
        raise HTTPException(status_code=500, detail=f"Categorization failed: {str(e)}")

@router.get("/debug/{user_id}")
async def debug_user_emails(user_id: str):
    """Debug endpoint to check user's emails."""
    try:
        db = DatabaseService.get_database()
        
        # Get all emails for this user
        all_emails = await db.email_logs.find({"user_id": user_id}).to_list(length=5)
        
        # Get count
        total_count = await db.email_logs.count_documents({"user_id": user_id})
        
        # Get status breakdown
        status_breakdown = await db.email_logs.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$classification_status", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        return {
            "user_id": user_id,
            "total_emails": total_count,
            "sample_emails": all_emails,
            "status_breakdown": status_breakdown
        }
        
    except Exception as e:
        logger.error(f"Error in debug endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Debug failed: {str(e)}") 