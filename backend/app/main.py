from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import time
import logging
from contextlib import asynccontextmanager
import os
from pathlib import Path
import asyncio
from contextlib import suppress

from app.config.settings import settings
from app.api import auth, sync, query, health
from app.api.intelligent_email_system import router as intelligent_email_router
# Enhanced processing router removed - not part of main flow
from app.api.financial_analytics import router as financial_analytics_router
from app.services.cache_service import InMemoryCache
from app.services.database_service import DatabaseService
from app.utils.middleware import RequestLoggingMiddleware, RateLimitMiddleware

# Background email processing worker
from start_background_worker import BackgroundWorker

# Global background worker instance (will be started in lifespan)
background_worker: BackgroundWorker | None = None

# Configure structured logging early
from app.utils.logging_utils import configure_logging
import logging

configure_logging(level=settings.log_level)
logger = logging.getLogger(__name__)

# Global cache instance
cache = InMemoryCache(max_size=1000, default_ttl=300)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Pluto Money application...")
    try:
        await DatabaseService.initialize()
        logger.info("Database connected successfully")

        # Start background worker
        global background_worker
        background_worker = BackgroundWorker()
        app.state.worker_task = asyncio.create_task(background_worker.start())
        logger.info("Background email worker task started")
    except Exception as e:
        logger.warning(f"Database connection failed: {e}")
        logger.info("Application will run without database functionality")
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Pluto Money application...")
    try:
        await DatabaseService.close()

        # Stop background worker
        if background_worker and background_worker.running:
            background_worker.running = False
            await background_worker.stop()
        if hasattr(app.state, 'worker_task'):
            app.state.worker_task.cancel()
            with suppress(asyncio.CancelledError):
                await app.state.worker_task
    except Exception as e:
        logger.warning(f"Error closing database connection: {e}")

# Create FastAPI app
app = FastAPI(
    title="Pluto Money - GenAI Email Intelligence",
    description="Transform Gmail data into structured financial insights",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(sync.router, prefix="/sync", tags=["Email Sync"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(intelligent_email_router)
app.include_router(financial_analytics_router)

# Add Gmail sync router
from app.api import gmail_sync
app.include_router(gmail_sync.router, prefix="/gmail", tags=["Gmail Sync"])

# Add SMS router
from app.api import sms_api
app.include_router(sms_api.router, prefix="/sms", tags=["SMS Management"])

# Include WebSocket router for real-time chat and progress updates
from app import websocket as websocket_module
app.include_router(websocket_module.router, tags=["WebSocket"])

# Add /logout endpoint at root level for frontend compatibility
@app.post("/logout")
async def logout_user(request: Request):
    """Logout user - root level endpoint."""
    try:
        logger.info("="*50)
        logger.info("LOGOUT REQUEST RECEIVED")
        logger.info("="*50)
        
        # Import here to avoid circular imports
        from app.api.auth import _get_current_user
        
        try:
            current_user = await _get_current_user(request)
            logger.info(f"Logging out user: {current_user.get('email')}")
        except:
            logger.info("No valid user session found for logout")
        
        logger.info("Logout completed successfully")
        logger.info("="*50)
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        return {"message": "Logout completed"}

# Add /me endpoint at root level for frontend compatibility
@app.get("/me")
async def get_current_user_info(request: Request):
    """Get current user information - root level endpoint."""
    # Import here to avoid circular imports
    from app.api.auth import _get_current_user
    from app.services.database_service import DatabaseService
    from bson import ObjectId
    from datetime import datetime
    
    try:
        logger.info("="*50)
        logger.info("FETCHING USER PROFILE FROM /me ENDPOINT")
        logger.info("="*50)
        
        # Get current user from JWT token
        logger.info("Getting current user from JWT token")
        current_user = await _get_current_user(request)
        logger.info(f"Current user from JWT: {current_user}")
        
        db = DatabaseService.get_database()
        logger.info("Database connection obtained")
        
        user_id = current_user["user_id"]
        logger.info(f"Looking up user with ID: {user_id}")
        
        # Try to find user by email first (more reliable)
        user = None
        email = current_user.get("email")
        logger.info(f"Looking up user with email: {email}")
        
        if email:
            user = await db.users.find_one({"email": email})
            if user:
                logger.info(f"✅ Found user by email: {user['email']} (ID: {user['_id']})")
                # Update the user_id in current_user for consistency
                current_user["user_id"] = str(user["_id"])
                logger.info(f"Updated user_id to ObjectId: {current_user['user_id']}")
            else:
                logger.warning(f"❌ User not found by email: {email}")
        
        # If not found by email, try by ObjectId as fallback
        if not user:
            try:
                object_id = ObjectId(user_id)
                logger.info(f"Trying ObjectId lookup: {object_id}")
                user = await db.users.find_one({"_id": object_id})
                if user:
                    logger.info(f"✅ Found user by ObjectId: {user['_id']}")
                else:
                    logger.warning(f"❌ User not found by ObjectId: {object_id}")
            except Exception as oid_error:
                logger.warning(f"Invalid ObjectId '{user_id}': {oid_error}")
        
        if not user:
            logger.error(f"❌ User not found in database with ID: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"✅ User lookup successful: {user['email']} (ID: {user['_id']})")
        
        # Determine if Gmail is synced based on status
        gmail_sync_status = user.get("gmail_sync_status", "not_synced")
        initial_gmailData_sync = gmail_sync_status in ["synced", "completed"]
        
        logger.info(f"🔍 Sync Status Analysis:")
        logger.info(f"   - gmail_sync_status: {gmail_sync_status}")
        logger.info(f"   - initial_gmailData_sync: {initial_gmailData_sync}")
        logger.info(f"   - categorization_status: {user.get('categorization_status', 'not_started')}")
        
        response_data = {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "picture": user.get("picture"),
            "gmail_sync_status": gmail_sync_status,
            "initial_gmailData_sync": initial_gmailData_sync,  # Frontend expects this field
            "categorization_status": user.get("categorization_status", "not_started"),
            "last_synced": user.get("last_synced"),
            "email_count": user.get("email_count", 0),
            "emails_to_categorize": user.get("emails_to_categorize", 0),
            "emails_categorized": user.get("emails_categorized", 0),
            "emails_failed": user.get("emails_failed", 0),
            "created_at": user["created_at"],
            "last_login": user.get("last_login")
        }
        
        # Auto-start Gmail sync if not synced
        if user.get("gmail_sync_status") == "not_synced":
            logger.info("User not synced, auto-starting Gmail sync...")
            try:
                from app.api.gmail_sync import sync_gmail_emails
                import asyncio
                
                # Get Google access token
                google_access_token = user.get("google_access_token")
                if google_access_token:
                    # Update sync status to 'syncing'
                    # Ensure object_id variable exists
                    obj_id = user.get("_id")
                    await db.users.update_one(
                        {"_id": obj_id},
                        {
                            "$set": {
                                "gmail_sync_status": "syncing",
                                "sync_started_at": datetime.utcnow(),
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                    
                    # Start background sync
                    asyncio.create_task(sync_gmail_emails(user_id, google_access_token))
                    
                    response_data["gmail_sync_status"] = "syncing"
                    logger.info("Gmail sync started automatically")
                else:
                    logger.warning("No Google access token found for auto-sync")
                    
            except Exception as sync_error:
                logger.error(f"Error starting auto-sync: {sync_error}")
        
        logger.info(f"User profile response: {response_data}")
        logger.info("="*50)
        logger.info("USER PROFILE FETCHED SUCCESSFULLY")
        logger.info("="*50)
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to get user information")

# Login page endpoint
@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serve the login HTML page."""
    html_path = Path(__file__).parent.parent.parent / "frontend" / "login.html"
    if html_path.exists():
        with open(html_path, "r") as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="""
        <html>
        <body>
            <h1>Login Page Not Found</h1>
            <p>Please use the API endpoint: <a href="/auth/login">/auth/login</a></p>
        </body>
        </html>
        """)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Pluto Money - GenAI Email Intelligence Platform",
        "version": "1.0.0",
        "status": "running"
    }

# Favicon endpoint
@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon configured"}

# Dependency injection
def get_cache():
    return cache

def get_db():
    return DatabaseService.get_database()

# Make cache available globally
app.state.cache = cache
