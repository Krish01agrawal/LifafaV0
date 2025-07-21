#!/usr/bin/env python3
"""
Test Subscription Query Fix
===========================

This script tests the subscription query functionality to ensure it works correctly.
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

from app.db import db_manager

async def test_subscription_query():
    """Test subscription query directly"""
    try:
        print("=== Testing Subscription Query ===")
        
        user_id = '687e146ac871501608b62951'
        
        # Get the correct database
        client = db_manager.clients[0]
        if client is None:
            print("❌ No database client available")
            return
        
        database = client["pluto_money"]
        collection = database["subscriptions"]
        
        # Test 1: Count total subscriptions for user
        total_count = await collection.count_documents({"user_id": user_id})
        print(f"📊 Total subscriptions for user: {total_count}")
        
        # Test 2: Get a sample subscription
        if total_count > 0:
            sample = await collection.find_one({"user_id": user_id})
            if sample:
                print(f"🏗️ Sample subscription structure: {list(sample.keys())}")
                print(f"📋 Sample data:")
                print(f"   - service_name: {sample.get('service_name')}")
                print(f"   - subscription_type: {sample.get('subscription_type')}")
                print(f"   - amount: {sample.get('amount')}")
                print(f"   - subscription_status: {sample.get('subscription_status')}")
        
        # Test 3: Query with simple filter
        simple_query = {"user_id": user_id}
        print(f"\n🔍 Testing simple query: {simple_query}")
        
        cursor = collection.find(simple_query)
        results = await cursor.to_list(length=None)
        
        print(f"📊 Results found: {len(results)}")
        
        if results:
            print("\n📋 All subscriptions:")
            for i, sub in enumerate(results, 1):
                print(f"   {i}. {sub.get('service_name', 'Unknown')} - {sub.get('subscription_status', 'Unknown status')}")
        
        # Test 4: Query with complex filter (what LLM was generating)
        complex_query = {
            'time_period': {'start_date': None, 'end_date': None, 'period_type': 'specific'}, 
            'amount_filter': {'min_amount': 0, 'max_amount': 10000, 'currency': 'INR'}, 
            'transaction_types': ['subscription'], 
            'user_id': user_id
        }
        print(f"\n🔍 Testing complex query (what was failing): {complex_query}")
        
        cursor = collection.find(complex_query)
        results = await cursor.to_list(length=None)
        
        print(f"📊 Results found with complex query: {len(results)}")
        print("❌ This is why it was failing - complex query fields don't exist in collection")
        
    except Exception as e:
        print(f"❌ Error testing subscription query: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_subscription_query()) 