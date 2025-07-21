"""
Intelligent Query Processing System
==================================

This module implements intelligent query processing that breaks down user queries
into specific sub-queries for comprehensive data retrieval from MongoDB collections.

Key Features:
- Intent analysis and query understanding
- Sub-query generation for comprehensive coverage
- MongoDB query optimization
- Category-specific query handling
- Intelligent data combination and synthesis
- Response generation with insights

Query Types Supported:
- Financial transactions (spending, payments, subscriptions)
- Travel bookings (flights, hotels, transport)
- Shopping patterns (e-commerce, retail)
- Subscription services (premium, recurring)
- Investment activities (stocks, mutual funds)
- And many more categories
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json
import re
from dateutil import parser

# OpenAI
import openai
from openai import AsyncOpenAI

# Database
from .db import (
    categorized_emails_collection,
    email_logs_collection,
    db_manager
)
from .config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
api_key = settings.openai_api_key or settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY', '')
if not api_key:
    logger.warning("⚠️ OpenAI API key not found. Some features may not work.")
    client = None
else:
    client = AsyncOpenAI(api_key=api_key)

class QueryType(Enum):
    """Query types"""
    FINANCIAL = "financial"
    TRAVEL = "travel"
    SHOPPING = "shopping"
    SUBSCRIPTION = "subscription"
    INVESTMENT = "investment"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    GENERAL = "general"
    ANALYTICS = "analytics"
    COMPARISON = "comparison"
    TIMELINE = "timeline"

@dataclass
class SubQuery:
    """Sub-query data structure"""
    query_id: str
    category: str
    subcategory: str
    description: str
    mongodb_query: Dict[str, Any]
    collection_name: str
    expected_fields: List[str]
    priority: int = 1
    estimated_results: int = 0

@dataclass
class QueryResult:
    """Query result data structure"""
    sub_query_id: str
    category: str
    results: List[Dict[str, Any]]
    result_count: int
    total_amount: float = 0.0
    date_range: Optional[Dict[str, str]] = None
    merchants: List[str] = None
    
    def __post_init__(self):
        if self.merchants is None:
            self.merchants = []

class IntelligentQueryProcessor:
    """Intelligent query processing system"""
    
    def __init__(self):
        self.setup_category_patterns()
        self.setup_date_patterns()
    
    def setup_category_patterns(self):
        """Setup category patterns for query matching"""
        self.category_patterns = {
            "financial": ["spend", "payment", "bill", "transaction", "money", "amount", "cost"],
            "travel": ["flight", "hotel", "travel", "booking", "trip", "vacation", "journey"],
            "shopping": ["purchase", "buy", "order", "shop", "retail", "ecommerce"],
            "subscription": ["subscription", "recurring", "monthly", "yearly", "premium"],
            "investment": ["investment", "stock", "mutual fund", "sip", "portfolio"],
            "entertainment": ["movie", "game", "streaming", "event", "ticket"],
            "utilities": ["electricity", "water", "gas", "internet", "utility"],
            "healthcare": ["medical", "health", "pharmacy", "doctor", "hospital"],
            "education": ["course", "book", "certification", "learning", "study"]
        }
    
    def setup_date_patterns(self):
        """Setup date patterns for query parsing"""
        self.date_patterns = {
            "last_month": r"last\s+month",
            "last_3_months": r"last\s+3\s+months?|past\s+3\s+months?",
            "last_6_months": r"last\s+6\s+months?|past\s+6\s+months?",
            "this_year": r"this\s+year|current\s+year",
            "last_year": r"last\s+year|previous\s+year",
            "this_month": r"this\s+month|current\s+month"
        }
    
    async def process_intelligent_query(self, user_id: str, query: str) -> Dict[str, Any]:
        """
        Main function to process intelligent queries
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"🧠 Processing intelligent query for user {user_id}: {query}")
            
            # Step 1: Analyze query intent
            intent_analysis = await self._analyze_query_intent(query)
            logger.info("\n================ INTENT ANALYSIS ================")
            logger.info(json.dumps(intent_analysis, indent=2, default=str))
            logger.info("=================================================\n")
            
            # Step 2: Generate sub-queries
            sub_queries = await self._generate_sub_queries(intent_analysis, user_id)
            logger.info("\n================ SUB-QUERIES ====================")
            for sq in sub_queries:
                logger.info(f"{sq.query_id} | {sq.category}/{sq.subcategory} -> {sq.mongodb_query}")
            if not sub_queries:
                logger.warning("❌ No sub-queries generated – falling back to broad default query")
            logger.info("=================================================\n")
            
            # Step 3: Execute sub-queries
            query_results = await self._execute_sub_queries(sub_queries, user_id)
            logger.info("\n================ QUERY RESULTS ==================")
            for qr in query_results:
                logger.info(f"{qr.sub_query_id} -> {qr.result_count} docs, total_amount={qr.total_amount}")
            logger.info("=================================================\n")
            
            # Step 4: Synthesize response
            response = await self._synthesize_response(query, intent_analysis, query_results)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "original_query": query,
                "intent_analysis": intent_analysis,
                "sub_queries": [sq.__dict__ for sq in sub_queries],
                "query_results": [qr.__dict__ for qr in query_results],
                "response": response,
                "processing_time": processing_time,
                "total_results": sum(qr.result_count for qr in query_results),
                "total_amount": sum(qr.total_amount for qr in query_results)
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Intelligent query processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_query": query,
                "processing_time": processing_time
            }

    async def _analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze user query intent using OpenAI"""
        try:
            if not client:
                logger.error("❌ OpenAI client not initialized. Cannot analyze query intent.")
                return {
                    "primary_intent": "general",
                    "query_type": "general",
                    "confidence": 0.5
                }
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at analyzing user queries about email data to understand intent and extract key parameters.
                        
                        Your task is to analyze the user query and extract:
                        1. Primary intent (what they want to know)
                        2. Time period (if specified)
                        3. Categories of interest
                        4. Specific merchants or services
                        5. Amount ranges or thresholds
                        6. Transaction types
                        7. Any other relevant filters
                        
                        RESPONSE FORMAT (JSON):
                        {
                            "primary_intent": "spending_analysis|transaction_list|merchant_analysis|time_analysis|comparison|summary",
                            "query_type": "financial|travel|shopping|subscription|investment|entertainment|utilities|healthcare|education|general",
                            "time_period": {
                                "start_date": "YYYY-MM-DD",
                                "end_date": "YYYY-MM-DD",
                                "period_type": "specific|last_month|last_3_months|last_6_months|this_year|custom"
                            },
                            "categories": ["category1", "category2"],
                            "merchants": ["merchant1", "merchant2"],
                            "amount_filter": {
                                "min_amount": 0,
                                "max_amount": 10000,
                                "currency": "INR"
                            },
                            "transaction_types": ["payment", "bill", "subscription"],
                            "specific_requirements": ["requirement1", "requirement2"],
                            "confidence": 0.95
                        }
                        
                        ANALYSIS RULES:
                        - Extract specific dates, months, years mentioned
                        - Identify merchant names, brands, services
                        - Detect amount ranges or thresholds
                        - Understand comparison requests
                        - Identify analytical requirements
                        - Determine the scope of analysis needed
                        
                        RESPOND WITH VALID JSON ONLY."""
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this query: {query}"
                    }
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            response_content = response.choices[0].message.content
            intent_analysis = json.loads(response_content)
            
            return intent_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing query intent: {e}")
            return {
                "primary_intent": "general",
                "query_type": "general",
                "confidence": 0.5
            }

    async def _generate_sub_queries(self, intent_analysis: Dict[str, Any], user_id: str) -> List[SubQuery]:
        """Generate sub-queries based on intent analysis"""
        sub_queries: List[SubQuery] = []
        try:
            # Use OpenAI to generate structured sub-queries (simplified, robust to JSON errors)
            prompt = (
                "You are an email finance assistant. Produce ONLY valid JSON array (no markdown code fences) "
                "containing up to 10 objects with keys: category, subcategory, description, collection, query, fields.\n\n"
                "IMPORTANT COLLECTION MAPPING:\n"
                "- For subscription queries: use 'subscriptions' collection\n"
                "- For financial transactions: use 'financial_transactions' collection\n"
                "- For travel queries: use 'travel_bookings' collection\n"
                "- For job/career queries: use 'job_communications' collection\n"
                "- For promotional/marketing: use 'promotional_emails' collection\n"
                "- For general emails: use 'categorized_emails' collection\n\n"
                "IMPORTANT QUERY RULES:\n"
                "- Keep queries SIMPLE: use basic field matches only\n"
                "- For subscriptions: query should be empty {} (will be user-filtered automatically)\n"
                "- For financial: use simple fields like transaction_type, merchant_canonical\n"
                "- Avoid complex nested objects, date ranges, or amount filters\n"
                "- Focus on collection selection over complex query logic\n\n"
                f"User intent analysis:\n{intent_analysis}\n"
                "Return JSON now."
            )
            logger.debug("OpenAI prompt for sub-query generation:\n%s", prompt)
            if client:
                response = await client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=settings.openai_model,
                    temperature=settings.openai_temperature,
                    max_tokens=800,
                )
                content = response.choices[0].message.content.strip()
                logger.debug("Raw OpenAI sub-query generation response:\n%s", content)
                try:
                    sub_query_specs = json.loads(content)
                except json.JSONDecodeError as je:
                    logger.error("⚠️ OpenAI JSON parsing failed: %s", je)
                    # fallback: wrap content between first [ and last ]
                    try:
                        json_str = content[content.find('['):content.rfind(']')+1]
                        sub_query_specs = json.loads(json_str)
                    except Exception:
                        sub_query_specs = []
                for idx, spec in enumerate(sub_query_specs):
                    sub_queries.append(SubQuery(
                        query_id=f"SQ{idx+1}",
                        category=spec.get("category", "general"),
                        subcategory=spec.get("subcategory", "misc"),
                        description=spec.get("description", ""),
                        mongodb_query={**spec.get("query", {}), "user_id": user_id},
                        collection_name=spec.get("collection", "financial_transactions"),
                        expected_fields=spec.get("fields", []),
                    ))

            # -- FALLBACK: if no sub-query produced, use a broad default to avoid None --
            if not sub_queries:
                logger.warning("⚠️ No sub-queries produced; using default all-transactions query")
                sub_queries.append(SubQuery(
                    query_id="SQ1",
                    category="financial",
                    subcategory="all",
                    description="All financial transactions for user",
                    mongodb_query={"user_id": user_id},
                    collection_name="financial_transactions",
                    expected_fields=[],
                ))

            return sub_queries
        except Exception as e:
            logger.error(f"❌ Error generating sub-queries: {e}")
            # fallback default
            return [SubQuery(
                query_id="SQ1",
                category="financial",
                subcategory="all",
                description="All financial transactions for user",
                mongodb_query={"user_id": user_id},
                collection_name="financial_transactions",
                expected_fields=[],
            )]

    async def _execute_sub_queries(self, sub_queries: List[SubQuery], user_id: str) -> List[QueryResult]:
        """Execute all sub-queries and collect results"""
        query_results = []
 
        for sub_query in sub_queries:
            try:
                logger.info(f"🔄 Processing sub-query {sub_query.query_id}: {sub_query.collection_name}")
                logger.info(f"📝 Original query: {sub_query.mongodb_query}")
                
                # --- Normalize / fix LLM-generated query structure ------------------
                sub_query.mongodb_query = self._normalize_query(sub_query.mongodb_query)
                logger.info(f"🔧 Normalized query: {sub_query.mongodb_query}")

                # Always constrain to user
                sub_query.mongodb_query.setdefault('user_id', user_id)
                logger.info(f"👤 Final query with user_id: {sub_query.mongodb_query}")
                
                # CRITICAL FIX: If query is empty or overly complex, use simple fallback
                if len(sub_query.mongodb_query) <= 1:  # Only has user_id
                    logger.warning(f"🔧 Query too simple, using collection-specific fallback")
                    sub_query.mongodb_query = self._create_fallback_query(user_id, sub_query.collection_name)
                    logger.info(f"🎯 Fallback query: {sub_query.mongodb_query}")

                if sub_query.collection_name == "financial_transactions" or sub_query.collection_name.startswith("transaction"):
                    logger.info(f"💰 Executing financial transactions query...")
                    results = await self._query_financial_transactions(user_id, sub_query.mongodb_query)
                elif sub_query.collection_name == "categorized_emails":
                    logger.info(f"📧 Executing categorized emails query...")
                    results = await self._query_categorized_emails(sub_query.mongodb_query)
                elif sub_query.collection_name == "subscriptions" or sub_query.collection_name.startswith("subscription"):
                    logger.info(f"📱 Executing subscriptions query...")
                    results = await self._query_subscriptions(user_id, sub_query.mongodb_query)
                elif sub_query.collection_name == "travel_bookings" or sub_query.collection_name.startswith("travel"):
                    logger.info(f"✈️ Executing travel bookings query...")
                    results = await self._query_travel_bookings(user_id, sub_query.mongodb_query)
                elif sub_query.collection_name == "job_communications" or sub_query.collection_name.startswith("job"):
                    logger.info(f"💼 Executing job communications query...")
                    results = await self._query_job_communications(user_id, sub_query.mongodb_query)
                elif sub_query.collection_name == "promotional_emails" or sub_query.collection_name.startswith("promotional"):
                    logger.info(f"🎯 Executing promotional emails query...")
                    results = await self._query_promotional_emails(user_id, sub_query.mongodb_query)
                else:
                    logger.info(f"❓ Unknown collection type: {sub_query.collection_name}")
                    results = []
                
                # Calculate totals
                # Handle None values in amount field
                total_amount = self._calculate_total_amount(results, sub_query.collection_name)
                merchants = list(set(r.get('merchant_canonical', '') for r in results if r.get('merchant_canonical')))
                
                # Get service names for subscriptions
                if sub_query.collection_name.startswith("subscription"):
                    services = list(set(r.get('service_name', '') for r in results if r.get('service_name')))
                    merchants.extend(services)
                    merchants = list(set(merchants))  # Remove duplicates
                
                logger.info(f"📊 Sub-query {sub_query.query_id} results:")
                logger.info(f"   📈 Documents found: {len(results)}")
                logger.info(f"   💰 Total amount: {total_amount}")
                logger.info(f"   🏪 Merchants: {merchants[:5]}{'...' if len(merchants) > 5 else ''}")
                
                query_result = QueryResult(
                    sub_query_id=sub_query.query_id,
                    category=sub_query.category,
                    results=results,
                    result_count=len(results),
                    total_amount=total_amount,
                    merchants=merchants
                )
                
                query_results.append(query_result)
                
            except Exception as e:
                logger.error(f"❌ Error executing sub-query {sub_query.query_id}: {e}")
                import traceback
                logger.error(f"📋 Full traceback: {traceback.format_exc()}")
                continue
        
        return query_results

    # ---------------------------------------------------------------------
    # Helper: convert friendly filter objects (min/max etc.) to Mongo syntax
    # ---------------------------------------------------------------------
    def _normalize_query(self, q: Dict[str, Any]) -> Dict[str, Any]:
        """Turn LLM-generated filters into valid MongoDB query operators."""
        normalized = {}
        for k, v in q.items():
            # Skip complex nested objects that don't match collection schema
            if k in ["time_period", "amount_filter", "transaction_types", "specific_requirements"]:
                # These are LLM artifacts, not actual MongoDB fields
                continue
            elif k == "amount" and isinstance(v, dict):
                rng = {}
                if "min" in v:
                    rng["$gte"] = v["min"]
                if "max" in v:
                    rng["$lte"] = v["max"]
                # Ignore currency key for amount comparisons
                normalized["amount"] = rng if rng else v
            elif k == "user_id":
                # Always keep user_id
                normalized[k] = v
            else:
                # Only add simple field matches that might exist in the collection
                if isinstance(v, (str, int, float, bool)):
                    normalized[k] = v
        return normalized

    async def _query_financial_transactions(self, user_id: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query financial transactions collection"""
        try:
            # CRITICAL FIX: Use the actual database where data exists
            # The data is in 'pluto_money' database, not the sharded database
            client = db_manager.clients[0]
            if client is None:
                logger.error("❌ No database client available")
                return []
            
            # Use the correct database name where data actually exists
            database = client["pluto_money"]
            collection = database["financial_transactions"]
            
            logger.info(f"🔍 Querying financial_transactions with: {query}")
            
            cursor = collection.find(query)
            results = await cursor.to_list(length=None)
            
            logger.info(f"📊 Found {len(results)} financial transactions")
            
            # Debug: Show sample transaction structure
            if results:
                sample = results[0]
                logger.info(f"💡 Sample transaction keys: {list(sample.keys())}")
                logger.info(f"💰 Sample amount value: {sample.get('amount')} (type: {type(sample.get('amount'))})")
                logger.info(f"🏪 Sample merchant: {sample.get('merchant_canonical', 'N/A')}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error querying financial transactions: {e}")
            return []

    async def _query_categorized_emails(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query categorized emails collection"""
        try:
            # CRITICAL FIX: Use the actual database where data exists
            client = db_manager.clients[0]
            if client is None:
                logger.error("❌ No database client available")
                return []
            
            # Use the correct database name where data actually exists
            database = client["pluto_money"]
            collection = database["categorized_emails"]
            
            logger.info(f"🔍 Querying categorized_emails with: {query}")
            
            cursor = collection.find(query)
            results = await cursor.to_list(length=None)
            
            logger.info(f"📊 Found {len(results)} categorized emails")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error querying categorized emails: {e}")
            return []

    async def _query_subscriptions(self, user_id: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query subscriptions collection"""
        try:
            # Use the correct database name where data actually exists
            client = db_manager.clients[0]
            if client is None:
                logger.error("❌ No database client available")
                return []
            
            # Use the correct database name where data actually exists
            database = client["pluto_money"]
            collection = database["subscriptions"]
            
            logger.info(f"🔍 Querying subscriptions with: {query}")
            
            # DEBUG: First, let's see what's actually in the collection
            total_subscriptions = await collection.count_documents({"user_id": user_id})
            logger.info(f"🔍 Total subscriptions in collection for user: {total_subscriptions}")
            
            if total_subscriptions > 0:
                # Get a sample to understand the structure
                sample_sub = await collection.find_one({"user_id": user_id})
                if sample_sub:
                    logger.info(f"🏗️ Sample subscription structure: {list(sample_sub.keys())}")
                    logger.info(f"📋 Sample data: service_name={sample_sub.get('service_name')}, subscription_type={sample_sub.get('subscription_type')}")
            
            cursor = collection.find(query)
            results = await cursor.to_list(length=None)
            
            logger.info(f"📊 Found {len(results)} subscriptions")
            
            # Debug: Show sample subscription structure
            if results:
                sample = results[0]
                logger.info(f"💡 Sample subscription keys: {list(sample.keys())}")
                logger.info(f"💰 Sample amount value: {sample.get('amount')} (type: {type(sample.get('amount'))})")
                logger.info(f"🏪 Sample service: {sample.get('service_name', 'N/A')}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error querying subscriptions: {e}")
            return []

    async def _query_travel_bookings(self, user_id: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query travel bookings collection"""
        try:
            client = db_manager.clients[0]
            if client is None:
                logger.error("❌ No database client available")
                return []
            
            database = client["pluto_money"]
            collection = database["travel_bookings"]
            
            logger.info(f"🔍 Querying travel_bookings with: {query}")
            
            cursor = collection.find(query)
            results = await cursor.to_list(length=None)
            
            logger.info(f"📊 Found {len(results)} travel bookings")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error querying travel bookings: {e}")
            return []

    async def _query_job_communications(self, user_id: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query job communications collection"""
        try:
            client = db_manager.clients[0]
            if client is None:
                logger.error("❌ No database client available")
                return []
            
            database = client["pluto_money"]
            collection = database["job_communications"]
            
            logger.info(f"🔍 Querying job_communications with: {query}")
            
            cursor = collection.find(query)
            results = await cursor.to_list(length=None)
            
            logger.info(f"📊 Found {len(results)} job communications")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error querying job communications: {e}")
            return []

    async def _query_promotional_emails(self, user_id: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query promotional emails collection"""
        try:
            client = db_manager.clients[0]
            if client is None:
                logger.error("❌ No database client available")
                return []
            
            database = client["pluto_money"]
            collection = database["promotional_emails"]
            
            logger.info(f"🔍 Querying promotional_emails with: {query}")
            
            cursor = collection.find(query)
            results = await cursor.to_list(length=None)
            
            logger.info(f"📊 Found {len(results)} promotional emails")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error querying promotional emails: {e}")
            return []

    async def _synthesize_response(self, original_query: str, intent_analysis: Dict[str, Any], query_results: List[QueryResult]) -> str:
        """Synthesize comprehensive response from query results"""
        try:
            # Prepare summary data
            total_results = sum(qr.result_count for qr in query_results)
            total_amount = sum(qr.total_amount for qr in query_results)
            all_merchants = list(set(merchant for qr in query_results for merchant in qr.merchants))
            
            summary_data = {
                "total_results": total_results,
                "total_amount": total_amount,
                "categories_found": list(set(qr.category for qr in query_results)),
                "merchants_found": all_merchants,
                "query_type": intent_analysis.get('query_type', 'general'),
                "primary_intent": intent_analysis.get('primary_intent', 'general')
            }
            
            if not client:
                logger.error("❌ OpenAI client not initialized. Cannot synthesize response.")
                return f"Analysis completed. Found {total_results} results with total amount ₹{total_amount:.2f}."
            
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at synthesizing comprehensive responses from email data analysis.
                        
                        Your task is to create a clear, insightful response that answers the user's query
                        based on the data analysis results.
                        
                        RESPONSE GUIDELINES:
                        - Be conversational and helpful
                        - Provide specific insights and patterns
                        - Include relevant statistics and amounts
                        - Highlight important findings
                        - Suggest actionable insights
                        - Use clear formatting for readability
                        
                        Format the response with:
                        - Summary of findings
                        - Key statistics
                        - Notable patterns
                        - Recommendations (if applicable)
                        - Additional context"""
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Original Query: {original_query}
                        
                        Intent Analysis: {json.dumps(intent_analysis)}
                        
                        Summary Data: {json.dumps(summary_data)}
                        
                        Query Results: {json.dumps([qr.__dict__ for qr in query_results])}
                        
                        Please synthesize a comprehensive response.
                        """
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Error synthesizing response: {e}")
            return f"Analysis completed. Found {total_results} results with total amount ₹{total_amount:.2f}."

    def _calculate_total_amount(self, results: List[Dict[str, Any]], collection_name: str) -> float:
        """Calculate total amount from query results, handling different field names."""
        total_amount = 0.0
        if collection_name == "financial_transactions":
            total_amount = sum(
                float(r.get('amount', 0)) if r.get('amount') is not None else 0 
                for r in results
            )
        elif collection_name == "subscriptions":
            total_amount = sum(
                float(r.get('amount', 0)) if r.get('amount') is not None else 0 
                for r in results
            )
        elif collection_name == "travel_bookings":
            total_amount = sum(
                float(r.get('total_amount', 0)) if r.get('total_amount') is not None else 0 
                for r in results
            )
        elif collection_name == "job_communications":
            total_amount = sum(
                float(r.get('amount', 0)) if r.get('amount') is not None else 0 
                for r in results
            )
        elif collection_name == "promotional_emails":
            total_amount = sum(
                float(r.get('amount', 0)) if r.get('amount') is not None else 0 
                for r in results
            )
        return total_amount

    def _create_fallback_query(self, user_id: str, collection_name: str) -> Dict[str, Any]:
        """Creates a simple, effective fallback query for collections with complex schemas."""
        logger.warning(f"🔧 Creating fallback query for collection: {collection_name}")
        if collection_name == "subscriptions":
            return {"user_id": user_id}
        elif collection_name == "travel_bookings":
            return {"user_id": user_id}
        elif collection_name == "job_communications":
            return {"user_id": user_id}
        elif collection_name == "promotional_emails":
            return {"user_id": user_id}
        elif collection_name == "financial_transactions":
            return {"user_id": user_id}
        elif collection_name == "categorized_emails":
            return {"user_id": user_id}
        else:
            return {"user_id": user_id}

# Convenience functions
async def process_user_query(user_id: str, query: str) -> Dict[str, Any]:
    """Process a user query using intelligent query processing"""
    processor = IntelligentQueryProcessor()
    return await processor.process_intelligent_query(user_id, query)

async def get_query_suggestions(user_id: str) -> List[str]:
    """Get query suggestions for a user"""
    return [
        "Show me my spending in the last 3 months",
        "What are my recurring subscriptions?",
        "How much did I spend on food delivery?",
        "Show me all travel bookings",
        "What are my top spending categories?",
        "Show me investment transactions",
        "How much did I spend on entertainment?",
        "Show me utility bills",
        "What are my shopping patterns?",
        "Show me healthcare expenses"
    ] 