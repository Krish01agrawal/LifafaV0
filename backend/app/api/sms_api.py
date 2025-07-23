"""
SMS API Endpoints
================

This module provides API endpoints for SMS data management including:
- SMS data upload and processing
- SMS data retrieval and filtering
- Financial transaction extraction from SMS
- Integration with existing financial analytics
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional, Any
import json
import logging
from datetime import datetime, timedelta

from app.services.sms_service import (
    process_sms_data, get_sms_data, get_financial_sms, get_sms_stats,
    SMSProcessor, SMSPatternMatcher
)
from app.core.dependencies import get_current_user
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sms", tags=["SMS Management"])

@router.post("/upload")
async def upload_sms_data(
    sms_file: UploadFile = File(...),
    user: User = Depends(get_current_user)
):
    """
    Upload SMS data from file (JSON/CSV format)
    
    Expected JSON format:
    [
        {
            "id": "sms_123",
            "sender_number": "+919876543210",
            "sender_name": "HDFC Bank",
            "message_body": "Rs. 1000 debited from your account...",
            "received_date": "2024-01-15T10:30:00",
            "provider": "android_sms"
        }
    ]
    """
    try:
        if not sms_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        content = await sms_file.read()
        
        # Parse based on file type
        if sms_file.filename.endswith('.json'):
            sms_messages = json.loads(content.decode('utf-8'))
        elif sms_file.filename.endswith('.csv'):
            # Basic CSV parsing - you might want to use pandas for complex CSV
            lines = content.decode('utf-8').split('\n')
            headers = lines[0].split(',')
            sms_messages = []
            
            for line in lines[1:]:
                if line.strip():
                    values = line.split(',')
                    sms_data = dict(zip(headers, values))
                    sms_messages.append(sms_data)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use JSON or CSV")
        
        # Process SMS data
        result = await process_sms_data(user.id, sms_messages)
        
        if result['success']:
            return JSONResponse({
                "success": True,
                "message": "SMS data uploaded and processed successfully",
                "stats": result['stats'],
                "processed_sms": result['processed_sms'],
                "financial_sms": result['financial_sms'],
                "transactions_extracted": result['transactions_extracted']
            })
        else:
            raise HTTPException(status_code=500, detail=f"Processing failed: {result.get('error', 'Unknown error')}")
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        logger.error(f"Error uploading SMS data: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/upload-json")
async def upload_sms_json(
    sms_data: List[Dict[str, Any]],
    user: User = Depends(get_current_user)
):
    """
    Upload SMS data directly as JSON
    """
    try:
        result = await process_sms_data(user.id, sms_data)
        
        if result['success']:
            return JSONResponse({
                "success": True,
                "message": "SMS data processed successfully",
                "stats": result['stats'],
                "processed_sms": result['processed_sms'],
                "financial_sms": result['financial_sms'],
                "transactions_extracted": result['transactions_extracted']
            })
        else:
            raise HTTPException(status_code=500, detail=f"Processing failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error processing SMS data: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.get("/data")
async def get_user_sms_data(
    limit: int = 1000,
    financial_only: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    """
    Get SMS data for the current user with optional filtering
    """
    try:
        if financial_only:
            sms_data = await get_financial_sms(user.id, limit)
        else:
            sms_data = await get_sms_data(user.id, limit)
        
        # Apply date filtering if provided
        if start_date or end_date:
            filtered_data = []
            for sms in sms_data:
                sms_date = sms.get('received_date')
                if isinstance(sms_date, str):
                    sms_date = datetime.fromisoformat(sms_date.replace('Z', '+00:00'))
                
                if start_date:
                    start_dt = datetime.fromisoformat(start_date)
                    if sms_date < start_dt:
                        continue
                
                if end_date:
                    end_dt = datetime.fromisoformat(end_date)
                    if sms_date > end_dt:
                        continue
                
                filtered_data.append(sms)
            
            sms_data = filtered_data
        
        return JSONResponse({
            "success": True,
            "sms_data": sms_data,
            "count": len(sms_data)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving SMS data: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

@router.get("/stats")
async def get_user_sms_stats(
    user: User = Depends(get_current_user)
):
    """
    Get SMS statistics for the current user
    """
    try:
        stats = await get_sms_stats(user.id)
        
        return JSONResponse({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"Error getting SMS stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

@router.get("/financial")
async def get_financial_sms_data(
    limit: int = 500,
    user: User = Depends(get_current_user)
):
    """
    Get financial SMS data for the current user
    """
    try:
        financial_sms = await get_financial_sms(user.id, limit)
        
        return JSONResponse({
            "success": True,
            "financial_sms": financial_sms,
            "count": len(financial_sms)
        })
        
    except Exception as e:
        logger.error(f"Error retrieving financial SMS: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")

@router.post("/test-pattern")
async def test_sms_pattern(
    message_body: str = Form(...),
    sender_number: str = Form(...),
    user: User = Depends(get_current_user)
):
    """
    Test SMS pattern matching and classification
    """
    try:
        pattern_matcher = SMSPatternMatcher()
        
        # Classify SMS type
        sms_type = pattern_matcher.classify_sms_type(message_body, sender_number)
        
        # Check if financial
        is_financial = pattern_matcher.is_financial_sms(message_body, sender_number)
        
        # Extract information
        amount = pattern_matcher.extract_amount(message_body)
        bank_name = pattern_matcher.extract_bank_name(message_body, sender_number)
        merchant_name = pattern_matcher.extract_merchant_name(message_body)
        
        return JSONResponse({
            "success": True,
            "analysis": {
                "sms_type": sms_type,
                "is_financial": is_financial,
                "extracted_amount": amount,
                "extracted_bank": bank_name,
                "extracted_merchant": merchant_name,
                "original_message": message_body,
                "sender_number": sender_number
            }
        })
        
    except Exception as e:
        logger.error(f"Error testing SMS pattern: {e}")
        raise HTTPException(status_code=500, detail=f"Pattern testing failed: {str(e)}")

@router.delete("/clear")
async def clear_sms_data(
    user: User = Depends(get_current_user)
):
    """
    Clear all SMS data for the current user
    """
    try:
        from app.db import db_manager
        
        database = db_manager.get_database_for_user(user.id)
        sms_collection = database['sms_data']
        
        # Delete SMS data
        result = await sms_collection.delete_many({'user_id': user.id})
        
        return JSONResponse({
            "success": True,
            "message": f"Cleared {result.deleted_count} SMS messages",
            "deleted_count": result.deleted_count
        })
        
    except Exception as e:
        logger.error(f"Error clearing SMS data: {e}")
        raise HTTPException(status_code=500, detail=f"Clear operation failed: {str(e)}") 