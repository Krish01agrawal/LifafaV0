#!/usr/bin/env python3
"""
Test Elite Query Processor
==========================

Comprehensive testing for the world-class elite query processor.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_elite_query_processor():
    """Test the elite query processor with comprehensive scenarios"""
    try:
        print("=== Testing Elite Query Processor ===")
        
        from app.elite_query_processor import process_elite_query
        
        user_id = '687e146ac871501608b62951'
        
        # Comprehensive test queries
        test_scenarios = [
            {
                "name": "Subscription Analysis",
                "query": "What subscriptions do I have and how much am I spending?",
                "expected_collections": ["subscriptions"]
            },
            {
                "name": "Financial Overview", 
                "query": "Show me my financial transactions and spending patterns",
                "expected_collections": ["financial_transactions"]
            },
            {
                "name": "Multi-Collection Analysis",
                "query": "Give me insights about all my services, subscriptions, and payments",
                "expected_collections": ["subscriptions", "financial_transactions"]
            },
            {
                "name": "Job Communications",
                "query": "What job-related communications have I received?",
                "expected_collections": ["job_communications"]
            },
            {
                "name": "Complex Analysis",
                "query": "Analyze my spending patterns, subscription costs, and provide recommendations",
                "expected_collections": ["subscriptions", "financial_transactions"]
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}: {scenario['name']}")
            print(f"Query: {scenario['query']}")
            print(f"{'='*60}")
            
            try:
                result = await process_elite_query(user_id, scenario['query'])
                
                if result.get("success"):
                    print(f"✅ SUCCESS")
                    print(f"📊 Items Analyzed: {result.get('total_items_analyzed', 0)}")
                    print(f"🔬 Insights Generated: {result.get('insights_generated', 0)}")
                    print(f"⏱️  Processing Time: {result.get('processing_time', 0):.2f}s")
                    print(f"📋 Collections: {[r['collection'] for r in result.get('raw_results', [])]}")
                    
                    # Show performance metrics
                    metrics = result.get('performance_metrics', {})
                    print(f"📈 Performance Metrics:")
                    print(f"   - Query Complexity: {metrics.get('query_complexity', 0)}")
                    print(f"   - Data Completeness: {metrics.get('data_completeness', 0):.2f}")
                    print(f"   - Analysis Depth: {metrics.get('analysis_depth', 0)}")
                    
                    # Show response preview
                    response = result.get('response', '')
                    print(f"💬 Response Preview: {response[:200]}...")
                    
                    # Show detailed analysis for first scenario
                    if i == 1:
                        print(f"\n🔍 DETAILED ANALYSIS:")
                        for analysis in result.get('analyzed_results', []):
                            collection = analysis['collection']
                            print(f"\n   📁 {collection.upper()}:")
                            print(f"      Total Items: {analysis['total_items']}")
                            
                            # Show key insights
                            insights = analysis.get('key_insights', [])[:3]
                            for insight in insights:
                                print(f"      💡 {insight}")
                            
                            # Show top items
                            top_items = analysis.get('top_items', [])[:2]
                            for j, item in enumerate(top_items, 1):
                                print(f"      🏆 Top {j}: {item}")
                    
                else:
                    print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
                    if result.get('fallback_response'):
                        print(f"🔄 Fallback: {result.get('fallback_response')}")
                
            except Exception as e:
                print(f"❌ EXCEPTION: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*60}")
        print("🎯 ELITE QUERY PROCESSOR TEST COMPLETE")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ Error testing elite query processor: {e}")
        import traceback
        traceback.print_exc()

async def test_data_availability():
    """Test data availability across collections"""
    try:
        print("\n=== Testing Data Availability ===")
        
        import sys
        sys.path.insert(0, '.')
        from app.db import db_manager
        
        user_id = '687e146ac871501608b62951'
        client = db_manager.clients[0]
        database = client['pluto_money']
        
        collections_to_test = [
            'subscriptions',
            'financial_transactions', 
            'travel_bookings',
            'job_communications',
            'promotional_emails',
            'categorized_emails'
        ]
        
        total_items = 0
        for collection_name in collections_to_test:
            collection = database[collection_name]
            count = await collection.count_documents({'user_id': user_id})
            total_items += count
            print(f"📊 {collection_name}: {count} items")
            
            if count > 0:
                # Show sample data structure
                sample = await collection.find_one({'user_id': user_id})
                if sample:
                    key_fields = list(sample.keys())[:8]
                    print(f"   🔑 Key fields: {', '.join(key_fields)}")
        
        print(f"\n📈 Total items available: {total_items}")
        return total_items > 0
        
    except Exception as e:
        print(f"❌ Error testing data availability: {e}")
        return False

if __name__ == "__main__":
    async def main():
        # Test data availability first
        data_available = await test_data_availability()
        
        if data_available:
            # Run comprehensive tests
            await test_elite_query_processor()
        else:
            print("❌ No data available for testing")
    
    asyncio.run(main()) 