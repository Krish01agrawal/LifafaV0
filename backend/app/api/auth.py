from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import jwt
from bson import ObjectId
import requests
from datetime import datetime, timedelta

from app.services.gmail_service import gmail_service
from app.services.database_service import DatabaseService
from app.config.settings import settings
from app.services.auth_service import AuthService
from app.models.auth import User, UserCreate, LoginResponse

logger = logging.getLogger(__name__)

router = APIRouter()

def _create_access_token(user_id: str, email: str) -> str:
    """Create JWT access token."""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    }
    
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

async def _get_current_user(request: Request) -> Dict[str, Any]:
    """Get current user from JWT token."""
    try:
        # Get authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        # Extract token
        auth_parts = authorization.split(" ")
        if len(auth_parts) != 2:
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        scheme, token = auth_parts
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
        
        # Decode token
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Validate user exists (skip if database is not available)
        try:
            db = DatabaseService.get_database()
            user = await db.users.find_one({"_id": ObjectId(payload["user_id"])})
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
        except Exception as db_error:
            # If database is not available, just validate the JWT token
            logger.warning(f"Database validation skipped due to error: {db_error}")
            pass
        
        return {
            "user_id": payload["user_id"],
            "email": payload["email"]
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

class AuthRequest(BaseModel):
    auth_code: str

class AuthResponse(BaseModel):
    user_id: str
    access_token: str
    email: str
    name: str
    expires_at: datetime

class UserProfile(BaseModel):
    user_id: str
    email: str
    name: str
    gmail_sync_status: str
    last_synced: Optional[datetime]
    email_count: Optional[int]
    created_at: datetime

@router.post("/google", response_model=AuthResponse)
async def authenticate_google(request: AuthRequest):
    """Authenticate user with Google OAuth."""
    try:
        logger.info("Processing Google OAuth authentication")
        
        # Authenticate with Google
        credentials = await gmail_service.authenticate_user(request.auth_code)
        
        # Get or create user in database
        try:
            db = DatabaseService.get_database()
        except RuntimeError:
            # Database not initialized (possible code reload) – initialize on demand
            from app.services.database_service import DatabaseService as _DS
            await _DS.initialize()
            db = _DS.get_database()
        
        # Check if user exists
        existing_user = await db.users.find_one({"email": credentials["email"]})
        
        if existing_user:
            # Update existing user
            user_id = str(existing_user["_id"])
            await db.users.update_one(
                {"_id": existing_user["_id"]},
                {
                    "$set": {
                        "google_auth_token": credentials,
                        "last_login": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            logger.info(f"Updated existing user: {credentials['email']}")
        else:
            # Create new user
            user_doc = {
                "email": credentials["email"],
                "name": credentials["name"],
                "google_auth_token": credentials,
                "gmail_sync_status": "not_synced",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": datetime.utcnow()
            }
            
            result = await db.users.insert_one(user_doc)
            user_id = str(result.inserted_id)
            logger.info(f"Created new user: {credentials['email']}")
        
        # Generate JWT token
        access_token = _create_access_token(user_id, credentials["email"])
        
        return AuthResponse(
            user_id=user_id,
            access_token=access_token,
            email=credentials["email"],
            name=credentials["name"],
            expires_at=datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        )
        
    except Exception as e:
        logger.error(f"Error in Google authentication: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(request: Request):
    """Get current user profile."""
    try:
        # Get current user from JWT token
        current_user = await _get_current_user(request)
        
        db = DatabaseService.get_database()
        
        user = await db.users.find_one({"_id": ObjectId(current_user["user_id"])})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserProfile(
            user_id=str(user["_id"]),
            email=user["email"],
            name=user["name"],
            gmail_sync_status=user.get("gmail_sync_status", "not_synced"),
            last_synced=user.get("last_synced"),
            email_count=user.get("email_count", 0),
            created_at=user["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@router.post("/refresh")
async def refresh_token(request: Request):
    """Refresh access token."""
    try:
        # Get current user from JWT token
        current_user = await _get_current_user(request)
        
        db = DatabaseService.get_database()
        
        user = await db.users.find_one({"_id": ObjectId(current_user["user_id"])})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate new token
        access_token = _create_access_token(str(user["_id"]), user["email"])
        
        return {
            "access_token": access_token,
            "expires_at": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh token")

@router.post("/logout")
async def logout(request: Request):
    """Logout user (invalidate token)."""
    try:
        # Get current user from JWT token
        current_user = await _get_current_user(request)
        
        # In a production system, you'd add the token to a blacklist
        # For now, we'll just return success
        logger.info(f"User {current_user['user_id']} logged out")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise HTTPException(status_code=500, detail="Failed to logout")

@router.delete("/account")
async def delete_account(request: Request):
    """Delete user account and all associated data."""
    try:
        # Get current user from JWT token
        current_user = await _get_current_user(request)
        
        db = DatabaseService.get_database()
        user_id = current_user["user_id"]
        
        # Delete all user data
        await db.users.delete_one({"_id": ObjectId(user_id)})
        await db.email_logs.delete_many({"user_id": user_id})
        await db.financial_transactions.delete_many({"user_id": user_id})
        await db.travel_bookings.delete_many({"user_id": user_id})
        await db.job_communications.delete_many({"user_id": user_id})
        await db.promotional_emails.delete_many({"user_id": user_id})
        await db.query_logs.delete_many({"user_id": user_id})
        await db.extraction_failures.delete_many({"user_id": user_id})
        
        logger.info(f"Deleted account and all data for user {user_id}")
        
        return {"message": "Account deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete account")

@router.get("/login")
async def login_page():
    """Login endpoint - redirects directly to Google OAuth."""
    # Check if Google OAuth is configured
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=500, 
            detail="Google OAuth is not configured. Please set up Google OAuth credentials."
        )
    
    # Create OAuth URL
    oauth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={settings.google_client_id}&"
        f"redirect_uri={settings.google_redirect_uri}&"
        f"scope={settings.google_scope}&"
        f"response_type=code&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    # Redirect directly to Google OAuth
    return RedirectResponse(url=oauth_url)

@router.get("/callback")
async def google_oauth_callback(code: str, scope: str):
    """Handle Google OAuth callback with authorization code."""
    try:
        logger.info("="*50)
        logger.info("STARTING OAUTH CALLBACK PROCESS")
        logger.info("="*50)
        logger.info(f"Received OAuth callback with code: {code[:20]}...")
        logger.info(f"Received scope: {scope}")
        logger.info(f"Client ID: {settings.google_client_id}")
        logger.info(f"Redirect URI: {settings.google_redirect_uri}")
        
        # Step 1: Exchange authorization code for access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.google_redirect_uri
        }
        
        logger.info("Exchanging authorization code for access token...")
        token_response = requests.post(token_url, data=token_data)
        
        if token_response.status_code != 200:
            logger.error(f"Token exchange failed: {token_response.status_code} - {token_response.text}")
            raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_response.text}")
        
        token_info = token_response.json()
        logger.info(f"Token exchange successful. Token info keys: {list(token_info.keys())}")
        
        access_token = token_info.get("access_token")
        refresh_token = token_info.get("refresh_token")
        
        if not access_token:
            logger.error("No access token received from Google")
            raise HTTPException(status_code=400, detail="No access token received from Google")
        
        # Step 2: Get user profile from Google
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        logger.info("Fetching user profile from Google...")
        user_response = requests.get(user_info_url, headers=headers)
        
        if user_response.status_code != 200:
            logger.error(f"User info fetch failed: {user_response.status_code} - {user_response.text}")
            raise HTTPException(status_code=400, detail=f"User info fetch failed: {user_response.text}")
        
        user_info = user_response.json()
        logger.info(f"User profile fetched successfully. User: {user_info.get('email')}")
        logger.info(f"User info received: {user_info}")
        
        # Step 3: Create or update user in database
        logger.info("STEP 3: Creating or updating user in database")
        try:
            db = DatabaseService.get_database()
            logger.info("Database connection obtained")
            
            # Check if user exists
            existing_user = await db.users.find_one({"email": user_info.get("email")})
            logger.info(f"Existing user lookup result: {existing_user is not None}")
            if existing_user:
                logger.info(f"Found existing user: {existing_user['email']} (ID: {existing_user['_id']})")
            else:
                logger.info(f"No existing user found for email: {user_info.get('email')}")
            
            if existing_user:
                # Update existing user
                user_id = str(existing_user["_id"])
                logger.info(f"✅ Found existing user with MongoDB ID: {user_id}")
                await db.users.update_one(
                    {"_id": existing_user["_id"]},
                    {
                        "$set": {
                            "google_id": user_info.get("id"),
                            "name": user_info.get("name"),
                            "picture": user_info.get("picture"),
                            "google_access_token": access_token,
                            "google_refresh_token": refresh_token,
                            "last_login": datetime.utcnow(),
                            "updated_at": datetime.utcnow(),
                            "user_id": user_id  # ensure user_id field exists
                        }
                    }
                )
                logger.info(f"✅ Updated existing user: {user_info.get('email')}")
            else:
                # Create new user
                logger.info("Creating new user in database")
                user_doc = {
                    "user_id": str(ObjectId()),  # Unique user_id at creation
                    "email": user_info.get("email"),
                    "name": user_info.get("name"),
                    "picture": user_info.get("picture"),
                    "google_id": user_info.get("id"),
                    "google_access_token": access_token,
                    "google_refresh_token": refresh_token,
                    "gmail_sync_status": "not_synced",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "last_login": datetime.utcnow()
                }
                logger.info(f"User document to insert: {user_doc}")
                
                result = await db.users.insert_one(user_doc)
                user_id = str(result.inserted_id)
                
                # Update the user document to include user_id field
                await db.users.update_one(
                    {"_id": result.inserted_id},
                    {"$set": {"user_id": user_id}}
                )
                
                logger.info(f"Created new user: {user_info.get('email')} with MongoDB ID: {user_id}")
                
        except Exception as db_error:
            logger.error(f"Database error during user creation/update: {db_error}")
            # Try to create user with proper ObjectId
            try:
                user_doc = {
                    "user_id": str(ObjectId()),  # Unique user_id at creation
                    "email": user_info.get("email"),
                    "name": user_info.get("name"),
                    "picture": user_info.get("picture"),
                    "google_id": user_info.get("id"),
                    "google_access_token": access_token,
                    "google_refresh_token": refresh_token,
                    "gmail_sync_status": "not_synced",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "last_login": datetime.utcnow()
                }
                result = await db.users.insert_one(user_doc)
                user_id = str(result.inserted_id)
                
                # Update the user document to include user_id field
                await db.users.update_one(
                    {"_id": result.inserted_id},
                    {"$set": {"user_id": user_id}}
                )
                
                logger.info(f"Created new user with proper ObjectId: {user_id}")
            except Exception as retry_error:
                logger.error(f"Retry user creation failed: {retry_error}")
                # Try to find existing user by email
                existing_user = await db.users.find_one({"email": user_info.get("email")})
                if existing_user:
                    user_id = str(existing_user["_id"])
                    logger.info(f"Found existing user with ObjectId: {user_id}")
                else:
                    # Last resort - use Google ID but this will cause issues
                    user_id = user_info.get("id")
                    logger.warning(f"Using Google ID as fallback user_id: {user_id}")
            
        user_data = {
            "id": user_id,
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "google_id": user_info.get("id"),
            "google_access_token": access_token,
            "google_refresh_token": refresh_token
        }
        
        # Step 4: Generate JWT token
        logger.info("STEP 4: Generating JWT token")
        jwt_payload = {
            "user_id": user_id,
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes),
            "iat": datetime.utcnow()
        }
        logger.info(f"JWT payload: {jwt_payload}")
        
        jwt_token = jwt.encode(jwt_payload, settings.secret_key, algorithm=settings.algorithm)
        logger.info(f"JWT token generated successfully (length: {len(jwt_token)})")
        
        # Step 5: Redirect to frontend with user data and token
        logger.info("STEP 5: Redirecting to frontend")
        frontend_url = "http://localhost:8000"
        redirect_url = f"{frontend_url}?token={jwt_token}&user={user_info.get('email')}&name={user_info.get('name')}&picture={user_info.get('picture')}"
        
        logger.info(f"Redirecting to frontend: {frontend_url}")
        logger.info(f"Redirect URL: {redirect_url[:100]}...")
        logger.info("="*50)
        logger.info("OAUTH CALLBACK PROCESS COMPLETED SUCCESSFULLY")
        logger.info("="*50)
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"Error in OAuth callback: {e}")
        # Redirect to frontend with error
        error_url = f"http://localhost:8000?error=oauth_failed"
        return RedirectResponse(url=error_url)

@router.get("/gmail-data")
async def get_gmail_data(request: Request):
    """Fetch Gmail data for authenticated user."""
    try:
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        
        # Decode JWT token
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id = payload.get("user_id")
            email = payload.get("email")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Fetch Gmail data (simplified - you can expand this)
        gmail_data = {
            "user_email": email,
            "total_emails": 0,  # This would be fetched from Gmail API
            "recent_emails": [],  # This would be fetched from Gmail API
            "last_sync": datetime.utcnow().isoformat(),
            "status": "authenticated"
        }
        
        return {
            "status": "success",
            "gmail_data": gmail_data,
            "user": {
                "id": user_id,
                "email": email,
                "name": payload.get("name")
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching Gmail data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Gmail data: {str(e)}")

@router.get("/me")
async def get_me(request: Request):
    """Get current user information."""
    try:
        # Get current user from JWT token
        current_user = await _get_current_user(request)
        
        db = DatabaseService.get_database()
        
        user = await db.users.find_one({"_id": ObjectId(current_user["user_id"])})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "picture": user.get("picture"),
            "gmail_sync_status": user.get("gmail_sync_status", "not_synced"),
            "last_synced": user.get("last_synced"),
            "email_count": user.get("email_count", 0),
            "created_at": user["created_at"],
            "last_login": user.get("last_login")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user information")

@router.get("/health")
async def auth_health():
    """Health check for auth service."""
    return {
        "status": "healthy",
        "service": "auth",
        "timestamp": datetime.utcnow()
    }

 