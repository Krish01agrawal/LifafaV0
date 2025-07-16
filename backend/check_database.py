#!/usr/bin/env python3
"""
Check Database and Collections
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.database_service import DatabaseService

async def check_database():
    """Check the database and collections."""
    try:
        # Initialize database
        await DatabaseService.initialize()
        db = DatabaseService.get_database()
        
        print("=" * 60)
        print("🗄️  DATABASE INFORMATION")
        print("=" * 60)
        print(f"Database Name: {db.name}")
        print(f"Database Address: {db.address}")
        
        # List all collections
        collections = await db.list_collection_names()
        
        print(f"\n📁 Collections ({len(collections)}):")
        for collection in collections:
            count = await db[collection].count_documents({})
            print(f"  - {collection}: {count} documents")
        
        # Check specific collections
        print("\n" + "=" * 60)
        print("🔍 DETAILED COLLECTION ANALYSIS")
        print("=" * 60)
        
        collections_to_check = [
            'users', 'email_logs', 'financial_transactions', 
            'subscriptions', 'promotional_emails', 'travel_bookings',
            'job_communications', 'email_queue', 'extraction_failures'
        ]
        
        for collection_name in collections_to_check:
            if collection_name in collections:
                count = await db[collection_name].count_documents({})
                print(f"📊 {collection_name}: {count} documents")
                
                if count > 0:
                    # Get a sample document
                    sample = await db[collection_name].find_one({})
                    if sample:
                        print(f"   Sample ID: {sample.get('_id', 'N/A')}")
                        if 'user_id' in sample:
                            print(f"   User ID: {sample.get('user_id', 'N/A')}")
                        if 'email' in sample:
                            print(f"   Email: {sample.get('email', 'N/A')}")
            else:
                print(f"❌ {collection_name}: Collection not found")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE CHECK COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await DatabaseService.close()

if __name__ == "__main__":
    asyncio.run(check_database()) 