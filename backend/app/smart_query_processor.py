#!/usr/bin/env python3
"""
Smart Query Processor
====================

A fundamentally better approach to query processing that:
1. Uses collection schemas to generate accurate queries
2. Minimizes LLM calls for efficiency
3. Has intelligent fallbacks
4. Provides consistent, accurate results

Key Principles:
- Schema-aware: Knows what fields exist in each collection
- LLM-efficient: Single LLM call for intent + collection mapping
- Smart fallbacks: Always returns results when data exists
- User-focused: Optimized for user experience
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
import json
from openai import AsyncOpenAI
from .db import db_manager
from .config.settings import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
api_key = settings.openai_api_key or settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY', '')
client = AsyncOpenAI(api_key=api_key) if api_key else None

class SmartQueryProcessor:
    """Schema-aware, efficient query processor"""
    
    def __init__(self):
        self.collection_schemas = {
            "subscriptions": {
                "key_fields": ["service_name", "subscription_type", "service_category", "subscription_status", "amount"],
                "search_fields": ["service_name", "service_canonical", "plan_name"],
                "filter_fields": ["subscription_type", "service_category", "subscription_status"],
                "description": "User subscriptions and services"
            },
            "financial_transactions": {
                "key_fields": ["amount", "merchant_canonical", "transaction_type", "transaction_date", "payment_method"],
                "search_fields": ["merchant_canonical", "merchant", "description"],
                "filter_fields": ["transaction_type", "payment_method", "service_category"],
                "description": "Financial transactions and payments"
            },
            "travel_bookings": {
                "key_fields": ["booking_type", "destination", "travel_date", "total_amount", "booking_status"],
                "search_fields": ["destination", "airline", "hotel_name", "booking_reference"],
                "filter_fields": ["booking_type", "booking_status", "travel_class"],
                "description": "Travel bookings and itineraries"
            },
            "job_communications": {
                "key_fields": ["company_name", "job_title", "application_status", "application_date"],
                "search_fields": ["company_name", "job_title", "position_type"],
                "filter_fields": ["application_status", "job_type", "industry"],
                "description": "Job applications and career communications"
            },
            "promotional_emails": {
                "key_fields": ["sender", "offer_type", "discount_amount", "expiry_date"],
                "search_fields": ["sender", "brand_name", "offer_description"],
                "filter_fields": ["offer_type", "category", "is_expired"],
                "description": "Promotional offers and marketing emails"
            },
            "categorized_emails": {
                "key_fields": ["category", "subcategory", "sender", "subject", "date"],
                "search_fields": ["sender", "subject", "content_summary"],
                "filter_fields": ["category", "subcategory", "priority"],
                "description": "General categorized emails"
            }
        }
    
    async def process_query(self, user_id: str, query: str) -> Dict[str, Any]:
        """Main query processing function"""
        start_time = datetime.now()
        
        try:
            logger.info(f"🧠 Smart processing query for user {user_id}: {query}")
            
            # Step 1: Single LLM call for intent + collection mapping
            query_plan = await self._create_query_plan(query)
            logger.info(f"📋 Query plan: {query_plan}")
            
            # Step 2: Execute queries using schema-aware approach
            results = await self._execute_smart_queries(user_id, query_plan)
            logger.info(f"📊 Query results: {len(results)} collections queried")
            
            # Step 3: Synthesize response (only if we have data)
            response = await self._synthesize_smart_response(query, query_plan, results)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "original_query": query,
                "query_plan": query_plan,
                "results": results,
                "response": response,
                "processing_time": processing_time,
                "total_results": sum(len(r.get("data", [])) for r in results)
            }
            
        except Exception as e:
            logger.error(f"❌ Smart query processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_query": query,
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _create_query_plan(self, query: str) -> Dict[str, Any]:
        """Create a smart query plan using single LLM call"""
        try:
            if not client:
                # Fallback: analyze query with simple keywords
                return self._create_fallback_plan(query)
            
            # Create schema-aware prompt
            schema_info = "\n".join([
                f"- {name}: {info['description']} (fields: {', '.join(info['key_fields'])})"
                for name, info in self.collection_schemas.items()
            ])
            
            prompt = f"""Analyze this user query and create a query plan.

Available Collections:
{schema_info}

User Query: "{query}"

Return ONLY valid JSON with this structure:
{{
    "intent": "list|analyze|search|compare|summarize",
    "collections": ["collection1", "collection2"],
    "search_terms": ["term1", "term2"],
    "filters": {{"field": "value"}},
    "response_type": "detailed|summary|count"
}}

Rules:
- Choose 1-3 most relevant collections
- Use simple field names from the schema
- Keep filters basic and schema-aware
- Focus on user intent over complex logic"""

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            logger.warning(f"⚠️ LLM query planning failed: {e}, using fallback")
            return self._create_fallback_plan(query)
    
    def _create_fallback_plan(self, query: str) -> Dict[str, Any]:
        """Create fallback query plan using keyword analysis"""
        query_lower = query.lower()
        
        # Determine collections based on keywords
        collections = []
        if any(word in query_lower for word in ["subscription", "service", "plan", "trial", "monthly", "yearly"]):
            collections.append("subscriptions")
        if any(word in query_lower for word in ["transaction", "payment", "spend", "money", "amount", "financial"]):
            collections.append("financial_transactions")
        if any(word in query_lower for word in ["travel", "flight", "hotel", "booking", "trip"]):
            collections.append("travel_bookings")
        if any(word in query_lower for word in ["job", "application", "company", "career", "interview"]):
            collections.append("job_communications")
        if any(word in query_lower for word in ["offer", "discount", "promotion", "deal"]):
            collections.append("promotional_emails")
        
        # Default to subscriptions if no specific collection identified
        if not collections:
            collections = ["subscriptions", "financial_transactions"]
        
        return {
            "intent": "list",
            "collections": collections,
            "search_terms": [],
            "filters": {},
            "response_type": "detailed"
        }
    
    async def _execute_smart_queries(self, user_id: str, query_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute queries using schema-aware approach"""
        results = []
        
        for collection_name in query_plan.get("collections", []):
            try:
                logger.info(f"🔍 Querying {collection_name}")
                
                # Get collection data
                data = await self._query_collection_smart(user_id, collection_name, query_plan)
                
                results.append({
                    "collection": collection_name,
                    "data": data,
                    "count": len(data)
                })
                
                logger.info(f"📊 {collection_name}: {len(data)} results")
                
            except Exception as e:
                logger.error(f"❌ Error querying {collection_name}: {e}")
                continue
        
        return results
    
    async def _query_collection_smart(self, user_id: str, collection_name: str, query_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query a collection using smart, schema-aware approach"""
        try:
            # Get database connection
            client_db = db_manager.clients[0]
            if client_db is None:
                return []
            
            database = client_db["pluto_money"]
            collection = database[collection_name]
            
            # Build smart query
            query = {"user_id": user_id}
            
            # Add simple filters based on schema
            schema = self.collection_schemas.get(collection_name, {})
            filters = query_plan.get("filters", {})
            
            for field, value in filters.items():
                if field in schema.get("filter_fields", []):
                    query[field] = value
            
            # Add search terms if applicable
            search_terms = query_plan.get("search_terms", [])
            if search_terms and schema.get("search_fields"):
                search_conditions = []
                for term in search_terms:
                    for field in schema["search_fields"]:
                        search_conditions.append({field: {"$regex": term, "$options": "i"}})
                
                if search_conditions:
                    query["$or"] = search_conditions
            
            logger.info(f"🎯 Final query for {collection_name}: {query}")
            
            # Execute query
            cursor = collection.find(query).limit(50)  # Reasonable limit
            results = await cursor.to_list(length=None)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in smart query for {collection_name}: {e}")
            return []
    
    async def _synthesize_smart_response(self, original_query: str, query_plan: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
        """Synthesize response only when we have actual data"""
        try:
            # Check if we have any data
            total_results = sum(len(r.get("data", [])) for r in results)
            
            if total_results == 0:
                return "I couldn't find any data matching your query. Please try rephrasing your question or check if the data exists."
            
            # Create summary for LLM
            summary = {
                "total_results": total_results,
                "collections_queried": len(results),
                "data_summary": []
            }
            
            for result in results:
                if result["count"] > 0:
                    collection_name = result["collection"]
                    sample_data = result["data"][:3]  # First 3 items as sample
                    
                    summary["data_summary"].append({
                        "collection": collection_name,
                        "count": result["count"],
                        "sample_items": [self._extract_key_info(item, collection_name) for item in sample_data]
                    })
            
            # Generate response with LLM
            if client:
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that creates clear, informative responses about user data. Focus on the actual data found and provide specific insights."
                        },
                        {
                            "role": "user",
                            "content": f"""
                            User asked: "{original_query}"
                            
                            Data found: {json.dumps(summary)}
                            
                            Create a helpful response that:
                            1. Directly answers their question
                            2. Provides specific details from the data
                            3. Uses clear formatting
                            4. Is conversational and helpful
                            """
                        }
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                return response.choices[0].message.content.strip()
            else:
                # Fallback response without LLM
                return f"Found {total_results} items across {len([r for r in results if r['count'] > 0])} categories matching your query."
                
        except Exception as e:
            logger.error(f"❌ Error synthesizing response: {e}")
            return "I found some data matching your query, but encountered an error while formatting the response."
    
    def _extract_key_info(self, item: Dict[str, Any], collection_name: str) -> Dict[str, Any]:
        """Extract key information from an item based on collection schema"""
        schema = self.collection_schemas.get(collection_name, {})
        key_fields = schema.get("key_fields", [])
        
        key_info = {}
        for field in key_fields:
            if field in item:
                key_info[field] = item[field]
        
        return key_info

# Global instance
smart_processor = SmartQueryProcessor()

async def process_smart_query(user_id: str, query: str) -> Dict[str, Any]:
    """Process a user query using the smart query processor"""
    return await smart_processor.process_query(user_id, query) 