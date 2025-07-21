"""
Gmail Sync API
==============

Endpoints for synchronizing Gmail data.
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import requests
from bson import ObjectId

from app.services.database_service import DatabaseService
from app.api.auth import _get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/start")
async def start_gmail_sync(request: Request, background_tasks: BackgroundTasks, limit: Optional[int] = 500, store_raw: bool = True):
    """Start Gmail synchronization for the current user."""
    try:
        logger.info("="*50)
        logger.info("STARTING GMAIL SYNC PROCESS")
        logger.info("="*50)
        
        # Get current user
        current_user = await _get_current_user(request)
        logger.info(f"Starting sync for user: {current_user['email']}")
        
        # Get user from database
        db = DatabaseService.get_database()
        user = await db.users.find_one({"_id": ObjectId(current_user["user_id"])})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user has Google access token
        google_access_token = user.get("google_access_token")
        if not google_access_token:
            raise HTTPException(status_code=400, detail="No Google access token found")
        
        # Update sync status to 'syncing'
        await db.users.update_one(
            {"_id": ObjectId(current_user["user_id"])},
            {
                "$set": {
                    "gmail_sync_status": "syncing",
                    "sync_started_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info("Updated user sync status to 'syncing'")
        
        # Start background sync task
        background_tasks.add_task(sync_gmail_emails, current_user["user_id"], google_access_token, limit, store_raw)
        
        logger.info("Background sync task started")
        logger.info("="*50)
        
        return {
            "message": "Gmail sync started successfully",
            "status": "syncing",
            "user_id": current_user["user_id"]
        }
        
    except Exception as e:
        logger.error(f"Error starting Gmail sync: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start Gmail sync: {str(e)}")

@router.get("/status")
async def get_sync_status(request: Request):
    """Get Gmail sync status for the current user."""
    try:
        logger.info("Getting Gmail sync status")
        
        # Get current user
        current_user = await _get_current_user(request)
        
        # Get user from database
        db = DatabaseService.get_database()
        user = await db.users.find_one({"_id": ObjectId(current_user["user_id"])})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        sync_status = {
            "gmail_sync_status": user.get("gmail_sync_status", "not_synced"),
            "last_synced": user.get("last_synced"),
            "email_count": user.get("email_count", 0),
            "sync_started_at": user.get("sync_started_at"),
            "sync_error": user.get("sync_error")
        }
        
        logger.info(f"Sync status for {current_user['email']}: {sync_status}")
        
        return sync_status
        
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sync status: {str(e)}")

async def sync_gmail_emails(user_id: str, access_token: str, limit: int = 500, store_raw: bool = True):
    """Background task to sync Gmail emails."""
    try:
        logger.info(f"Starting background Gmail sync for user: {user_id}")
        
        db = DatabaseService.get_database()
        
        # Get Gmail messages
        gmail_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Get messages with proper limit (up to 20,000) from last 6 months
        from app.config.constants import DefaultLimits
        from datetime import datetime, timedelta
        
        # Calculate date 6 months ago
        six_months_ago = datetime.now() - timedelta(days=180)
        date_query = six_months_ago.strftime("%Y/%m/%d")
        
        params = {
            "maxResults": DefaultLimits.EMAIL_FETCH_LIMIT, # Fetch all messages for now, pagination will handle limit
            "q": f"after:{date_query}"  # Only get emails from last 6 months
        }
        
        logger.info("Fetching Gmail messages with pagination...")
        
        all_messages = []
        page_token = None
        total_fetched = 0
        
        while True:
            # Add page token if we have one
            if page_token:
                params["pageToken"] = page_token
            
            response = requests.get(gmail_url, headers=headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"Gmail API error: {response.status_code} - {response.text}")
                await db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {
                        "$set": {
                            "gmail_sync_status": "error",
                            "sync_error": f"Gmail API error: {response.status_code}",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                return
            
            messages_data = response.json()
            messages = messages_data.get("messages", [])
            if limit:
                remaining = limit - total_fetched
                messages = messages[:remaining]
            all_messages.extend(messages)
            total_fetched += len(messages)
            
            logger.info(f"Fetched page: {len(messages)} messages (Total: {total_fetched})")
            
            # Check if there are more pages
            page_token = messages_data.get("nextPageToken")
            if not page_token:
                break
            if limit and total_fetched >= limit:
                logger.info("Reached fetch limit, stopping pagination")
                break
        
        logger.info(f"Found {len(all_messages)} total Gmail messages across all pages")
        
        # Process each message (simplified - just store basic info)
        email_count = 0
        for message in all_messages[:limit]:
            try:
                # Get message details
                message_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message['id']}"
                msg_response = requests.get(message_url, headers=headers)
                
                if msg_response.status_code == 200:
                    msg_data = msg_response.json()
                    
                    # Extract basic email info
                    email_doc = {
                        "user_id": user_id,
                        "gmail_id": message['id'],
                        "thread_id": message.get('threadId'),
                        "snippet": msg_data.get('snippet', ''),
                        "received_date": datetime.utcnow(),  # Simplified
                        "processed_at": datetime.utcnow(),
                    }
                    if store_raw:
                        email_doc["raw_data"] = msg_data
                    
                    # Insert or update email
                    await db.email_logs.update_one(
                        {"user_id": user_id, "gmail_id": message['id']},
                        {"$set": email_doc},
                        upsert=True
                    )
                    
                    email_count += 1
                    
                    if email_count % 50 == 0:
                        logger.info(f"Processed {email_count}/{len(all_messages)} emails... ({email_count/len(all_messages)*100:.1f}%)")
                
            except Exception as msg_error:
                logger.error(f"Error processing message {message['id']}: {msg_error}")
                continue
        
        # Update user sync status
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "gmail_sync_status": "synced",
                    "last_synced": datetime.utcnow(),
                    "email_count": email_count,
                    "sync_error": None,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Gmail sync completed successfully. Processed {email_count}/{len(all_messages)} emails")
        logger.info(f"Success rate: {email_count/len(all_messages)*100:.1f}%")
        
        # Automatically trigger categorization after successful sync
        if email_count > 0:
            logger.info("="*50)
            logger.info("AUTOMATICALLY TRIGGERING EMAIL CATEGORIZATION")
            logger.info("="*50)
            
            try:
                from app.workers.email_worker import queue_email_processing
                
                # Find all pending emails for this user
                pending_emails = await db.email_logs.find({
                    "user_id": user_id,
                    "classification_status": {"$in": ["pending", None]}
                }).to_list(length=None)
                
                if pending_emails:
                    email_ids = [str(email["_id"]) for email in pending_emails]
                    logger.info(f"Found {len(email_ids)} emails to categorize automatically")
                    
                    # Queue for processing
                    await queue_email_processing(user_id, email_ids)
                    
                    # Update user status to indicate categorization is running
                    await db.users.update_one(
                        {"_id": ObjectId(user_id)},
                        {
                            "$set": {
                                "categorization_status": "in_progress",
                                "categorization_started_at": datetime.utcnow(),
                                "emails_to_categorize": len(email_ids)
                            }
                        }
                    )
                    
                    logger.info(f"Automatic categorization started for {len(email_ids)} emails")
                else:
                    logger.info("No pending emails found for categorization")
                    
            except Exception as cat_error:
                logger.error(f"Error starting automatic categorization: {cat_error}")
        
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"Critical error during Gmail sync: {e}")
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"gmail_sync_status": "error", "sync_error": str(e), "updated_at": datetime.utcnow()}}
        )
    finally:
        # Make sure status is no longer 'syncing' if task terminates
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user and user.get("gmail_sync_status") == "syncing":
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"gmail_sync_status": "synced", "last_synced": datetime.utcnow()}}
            )
        logger.info(f"Background Gmail sync task finished for {user_id}") 