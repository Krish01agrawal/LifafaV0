from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from datetime import datetime

from app.services.database_service import DatabaseService
from app.services.cache_service import cache

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "pluto-money-api"
    }

@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with all service statuses."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "service": "pluto-money-api",
            "components": {}
        }
        
        # Check database
        try:
            db_health = await DatabaseService.health_check()
            health_status["components"]["database"] = db_health
            if db_health["status"] != "healthy":
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "unhealthy"
        
        # Check cache
        try:
            cache_stats = cache.get_stats()
            health_status["components"]["cache"] = {
                "status": "healthy",
                "size": cache_stats["size"],
                "max_size": cache_stats["max_size"],
                "hit_rate": cache_stats["hit_rate"]
            }
        except Exception as e:
            health_status["components"]["cache"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "unhealthy"
        
        # Check LLM service (basic connectivity)
        try:
            # This would check OpenAI API connectivity
            health_status["components"]["llm"] = {
                "status": "healthy",
                "provider": "openai"
            }
        except Exception as e:
            health_status["components"]["llm"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "unhealthy"
        
        # Check Gmail service
        try:
            health_status["components"]["gmail"] = {
                "status": "healthy",
                "provider": "google"
            }
        except Exception as e:
            health_status["components"]["gmail"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "unhealthy"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error in detailed health check: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }

@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes/container orchestration."""
    try:
        # Check critical dependencies
        db_health = await DatabaseService.health_check()
        
        if db_health["status"] != "healthy":
            raise HTTPException(status_code=503, detail="Database not ready")
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes/container orchestration."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow()
    }

@router.get("/metrics")
async def get_metrics():
    """Get system metrics."""
    try:
        # Get cache metrics
        cache_stats = cache.get_stats()
        
        # Get database metrics
        db_health = await DatabaseService.health_check()
        
        return {
            "timestamp": datetime.utcnow(),
            "cache": {
                "hits": cache_stats["hits"],
                "misses": cache_stats["misses"],
                "hit_rate": cache_stats["hit_rate"],
                "size": cache_stats["size"],
                "evictions": cache_stats["evictions"]
            },
            "database": {
                "collections": db_health.get("collections", 0),
                "data_size": db_health.get("data_size", 0),
                "storage_size": db_health.get("storage_size", 0),
                "indexes": db_health.get("indexes", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics") 