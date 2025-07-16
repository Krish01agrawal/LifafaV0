"""
Centralized Settings Configuration
=================================

This module contains all application settings using Pydantic for type safety
and validation. Settings are loaded from environment variables with defaults.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "Pluto Money"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "emailStoragelifafa"
    
    # Authentication
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8001/auth/callback"
    google_scope: str = "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email"
    
    # LLM Configuration
    openai_api_key: str = ""
    OPENAI_API_KEY: str = ""  # Added for compatibility with existing code
    openai_model: str = "gpt-4o"
    openai_max_tokens: int = 4000
    openai_temperature: float = 0.1
    
    # Mem0 Configuration
    mem0_api_key: str = ""
    mem0_base_url: str = "https://api.mem0.ai"
    
    # Gmail API
    gmail_api_quota_limit: int = 1000000
    gmail_batch_size: int = 500
    
    # Processing
    email_batch_size: int = 16
    max_retries: int = 3
    worker_timeout: int = 300
    
    # Cache
    cache_max_size: int = 1000
    cache_default_ttl: int = 300
    
    # Rate Limiting
    requests_per_minute: int = 100
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/emailStoragelifafa.log"

    # Email limits (added for compatibility)
    default_email_limit: int = 100
    max_email_limit: int = 1000
    
    # Additional settings referenced in __init__.py
    enable_batch_processing: bool = True
    enable_smart_email_filtering: bool = True
    enable_smart_caching: bool = True
    is_production: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields from environment

# Global settings instance
settings = Settings() 