#!/usr/bin/env python3
"""
Comprehensive test script for Pluto Money backend.
Tests all major components and dependencies.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

class TestRunner:
    """Comprehensive test runner for Pluto Money backend."""
    
    def __init__(self):
        self.results = []
        self.errors = []
    
    async def test_imports(self):
        """Test all critical imports."""
        print("🔍 Testing imports...")
        
        try:
            # Test FastAPI and core dependencies
            import fastapi
            import uvicorn
            import motor
            import pymongo
            print("✅ Core dependencies: OK")
            
            # Test authentication
            import jwt
            import google.auth
            print("✅ Authentication dependencies: OK")
            
            # Test AI/LLM
            import openai
            print("✅ AI/LLM dependencies: OK")
            
            # Test data processing
            import pydantic
            import pydantic_settings
            print("✅ Data processing dependencies: OK")
            
            return True
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            self.errors.append(f"Import error: {e}")
            return False
    
    async def test_settings(self):
        """Test settings configuration."""
        print("⚙️  Testing settings...")
        
        try:
            from app.config.settings import settings
            
            # Check required settings
            required_settings = [
                'app_name', 'mongodb_url', 'mongodb_database',
                'secret_key', 'google_client_id', 'google_client_secret',
                'openai_api_key'
            ]
            
            for setting in required_settings:
                if not hasattr(settings, setting):
                    print(f"❌ Missing setting: {setting}")
                    return False
            
            print("✅ Settings configuration: OK")
            return True
            
        except Exception as e:
            print(f"❌ Settings error: {e}")
            self.errors.append(f"Settings error: {e}")
            return False
    
    async def test_database_service(self):
        """Test database service."""
        print("🗄️  Testing database service...")
        
        try:
            from app.services.database_service import DatabaseService
            
            # Test initialization
            await DatabaseService.initialize()
            print("✅ Database initialization: OK")
            
            # Test health check
            health = await DatabaseService.health_check()
            if health["status"] == "healthy":
                print("✅ Database health check: OK")
            else:
                print(f"⚠️  Database health: {health}")
            
            # Test cleanup
            await DatabaseService.close()
            print("✅ Database cleanup: OK")
            
            return True
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            self.errors.append(f"Database error: {e}")
            return False
    
    async def test_cache_service(self):
        """Test cache service."""
        print("💾 Testing cache service...")
        
        try:
            from app.services.cache_service import cache
            
            # Test basic operations
            cache.set("test_key", "test_value", ttl=60)
            value = cache.get("test_key")
            
            if value == "test_value":
                print("✅ Cache operations: OK")
            else:
                print("❌ Cache value mismatch")
                return False
            
            # Test stats
            stats = cache.get_stats()
            if "hits" in stats and "misses" in stats:
                print("✅ Cache stats: OK")
            
            return True
            
        except Exception as e:
            print(f"❌ Cache error: {e}")
            self.errors.append(f"Cache error: {e}")
            return False
    
    async def test_llm_service(self):
        """Test LLM service configuration."""
        print("🤖 Testing LLM service...")
        
        try:
            from app.services.llm_service import llm_service
            
            # Test if service is properly initialized
            if hasattr(llm_service, 'client') and llm_service.client:
                print("✅ LLM service initialization: OK")
            else:
                print("❌ LLM service not properly initialized")
                return False
            
            # Test if API key is configured
            if llm_service.client.api_key:
                print("✅ OpenAI API key: Configured")
            else:
                print("⚠️  OpenAI API key: Not configured")
            
            return True
            
        except Exception as e:
            print(f"❌ LLM service error: {e}")
            self.errors.append(f"LLM service error: {e}")
            return False
    
    async def test_gmail_service(self):
        """Test Gmail service configuration."""
        print("📧 Testing Gmail service...")
        
        try:
            from app.services.gmail_service import gmail_service
            
            # Test if service is properly initialized
            if hasattr(gmail_service, 'SCOPES'):
                print("✅ Gmail service initialization: OK")
            else:
                print("❌ Gmail service not properly initialized")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Gmail service error: {e}")
            self.errors.append(f"Gmail service error: {e}")
            return False
    
    async def test_api_routers(self):
        """Test API router imports."""
        print("🌐 Testing API routers...")
        
        try:
            from app.api import auth, sync, query, health
            
            # Test if routers are properly defined
            if hasattr(auth, 'router'):
                print("✅ Auth router: OK")
            else:
                print("❌ Auth router: Missing")
                return False
            
            if hasattr(sync, 'router'):
                print("✅ Sync router: OK")
            else:
                print("❌ Sync router: Missing")
                return False
            
            if hasattr(query, 'router'):
                print("✅ Query router: OK")
            else:
                print("❌ Query router: Missing")
                return False
            
            if hasattr(health, 'router'):
                print("✅ Health router: OK")
            else:
                print("❌ Health router: Missing")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ API router error: {e}")
            self.errors.append(f"API router error: {e}")
            return False
    
    async def test_models(self):
        """Test data models."""
        print("📋 Testing data models...")
        
        try:
            from app.models.financial import FinancialTransaction
            
            # Test model creation
            transaction = FinancialTransaction(
                user_id="test_user",
                transaction_type="payment",
                amount=100.0,
                currency="INR",
                transaction_date="2024-01-01",
                email_subject="Test transaction",
                extraction_confidence=0.95
            )
            
            print("✅ Financial transaction model: OK")
            return True
            
        except Exception as e:
            print(f"❌ Model error: {e}")
            self.errors.append(f"Model error: {e}")
            return False
    
    async def test_workers(self):
        """Test background workers."""
        print("⚙️  Testing background workers...")
        
        try:
            from app.workers.email_worker import email_worker
            
            # Test if worker is properly initialized
            if hasattr(email_worker, 'db'):
                print("✅ Email worker: OK")
            else:
                print("❌ Email worker: Not properly initialized")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Worker error: {e}")
            self.errors.append(f"Worker error: {e}")
            return False
    
    async def test_middleware(self):
        """Test middleware components."""
        print("🛡️  Testing middleware...")
        
        try:
            from app.utils.middleware import (
                RequestLoggingMiddleware, 
                RateLimitMiddleware,
                ErrorHandlingMiddleware
            )
            
            print("✅ Middleware imports: OK")
            return True
            
        except Exception as e:
            print(f"❌ Middleware error: {e}")
            self.errors.append(f"Middleware error: {e}")
            return False
    
    async def test_environment(self):
        """Test environment configuration."""
        print("🌍 Testing environment...")
        
        try:
            # Check if .env file exists
            env_file = Path(".env")
            if env_file.exists():
                print("✅ .env file: Found")
            else:
                print("⚠️  .env file: Not found (copy from env.example)")
            
            # Check required environment variables
            required_vars = [
                "GOOGLE_CLIENT_ID",
                "GOOGLE_CLIENT_SECRET", 
                "OPENAI_API_KEY",
                "SECRET_KEY"
            ]
            
            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
                print("   Please configure these in your .env file")
            else:
                print("✅ Environment variables: Configured")
            
            return len(missing_vars) == 0
            
        except Exception as e:
            print(f"❌ Environment error: {e}")
            self.errors.append(f"Environment error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🧪 Running Comprehensive Pluto Money Tests")
        print("=" * 60)
        
        tests = [
            ("Environment", self.test_environment),
            ("Imports", self.test_imports),
            ("Settings", self.test_settings),
            ("Database Service", self.test_database_service),
            ("Cache Service", self.test_cache_service),
            ("LLM Service", self.test_llm_service),
            ("Gmail Service", self.test_gmail_service),
            ("API Routers", self.test_api_routers),
            ("Data Models", self.test_models),
            ("Background Workers", self.test_workers),
            ("Middleware", self.test_middleware),
        ]
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                self.results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                self.errors.append(f"{test_name} exception: {e}")
                self.results.append((test_name, False))
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in self.results if result)
        total = len(self.results)
        
        for test_name, result in self.results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if self.errors:
            print(f"\n❌ ERRORS FOUND:")
            for error in self.errors:
                print(f"   - {error}")
        
        if passed == total:
            print("\n🎉 All tests passed! Pluto Money is ready to run!")
            print("\n🚀 To start the application:")
            print("   python start.py")
            return True
        else:
            print(f"\n⚠️  {total - passed} test(s) failed.")
            print("Please fix the issues above before running the application.")
            return False

async def main():
    """Main test runner."""
    runner = TestRunner()
    success = await runner.run_all_tests()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 