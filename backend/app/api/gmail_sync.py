"""
Gmail Sync API
==============

Endpoints for synchronizing Gmail data.
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from typing import Dict, Any
import logging
from datetime import datetime
import requests
from bson import ObjectId

from app.services.database_service import DatabaseService
from app.api.auth import _get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/start")
async def start_gmail_sync(request: Request, background_tasks: BackgroundTasks):
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
        background_tasks.add_task(sync_gmail_emails, current_user["user_id"], google_access_token)
        
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

async def sync_gmail_emails(user_id: str, access_token: str):
    """Background task to sync Gmail emails."""
    try:
        logger.info(f"Starting background Gmail sync for user: {user_id}")
        
        db = DatabaseService.get_database()
        
        # Get Gmail messages
        gmail_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Get first 100 messages
        params = {"maxResults": 100}
        
        logger.info("Fetching Gmail messages...")
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
        
        logger.info(f"Found {len(messages)} Gmail messages")
        
        # Process each message (simplified - just store basic info)
        email_count = 0
        for message in messages:
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
                        "raw_data": msg_data
                    }
                    
                    # Insert or update email
                    await db.email_logs.update_one(
                        {"user_id": user_id, "gmail_id": message['id']},
                        {"$set": email_doc},
                        upsert=True
                    )
                    
                    email_count += 1
                    
                    if email_count % 10 == 0:
                        logger.info(f"Processed {email_count} emails...")
                
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
        
        logger.info(f"Gmail sync completed successfully. Processed {email_count} emails")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"Error in background Gmail sync: {e}")
        
        # Update user sync status to error
        try:
            db = DatabaseService.get_database()
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "gmail_sync_status": "error",
                        "sync_error": str(e),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        except Exception as db_error:
            logger.error(f"Error updating sync status: {db_error}") 