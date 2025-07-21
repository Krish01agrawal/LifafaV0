#!/usr/bin/env python3
"""
Test Smart Query Processor
==========================

Test the new smart query processing system.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_smart_query_processor():
    """Test the smart query processor"""
    try:
        print("=== Testing Smart Query Processor ===")
        
        from app.smart_query_processor import process_smart_query
        
        user_id = '687e146ac871501608b62951'
        
        # Test queries
        test_queries = [
            "What subscriptions do I have?",
            "Show me my financial transactions",
            "List all my services and subscriptions",
            "What streaming services am I subscribed to?",
            "Show me all my payments and transactions"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Test {i}: {query} ---")
            
            result = await process_smart_query(user_id, query)
            
            if result.get("success"):
                print(f"✅ Success: {result.get('total_results', 0)} results found")
                print(f"📋 Query plan: {result.get('query_plan', {})}")
                print(f"📊 Collections: {[r['collection'] + ':' + str(r['count']) for r in result.get('results', [])]}")
                print(f"💬 Response: {result.get('response', '')[:100]}...")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Error testing smart query processor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_smart_query_processor()) 