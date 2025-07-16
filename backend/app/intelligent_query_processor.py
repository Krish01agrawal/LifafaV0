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
    financial_transactions_collection,
    email_logs_collection
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
            logger.info(f"📊 Intent analysis: {intent_analysis.get('primary_intent', 'unknown')}")
            
            # Step 2: Generate sub-queries
            sub_queries = await self._generate_sub_queries(intent_analysis, user_id)
            logger.info(f"🔍 Generated {len(sub_queries)} sub-queries")
            
            # Step 3: Execute sub-queries
            query_results = await self._execute_sub_queries(sub_queries, user_id)
            logger.info(f"✅ Executed {len(query_results)} sub-queries")
            
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
        """Generate comprehensive sub-queries based on intent analysis"""
        try:
            if not client:
                logger.error("❌ OpenAI client not initialized. Cannot generate sub-queries.")
                return []
            
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at generating comprehensive sub-queries to ensure complete data retrieval for user queries.
                        
                        Your task is to break down the user's intent into specific sub-queries that cover all relevant aspects.
                        
                        For financial queries, generate sub-queries for:
                        1. Premium subscriptions (Netflix, Spotify, Amazon Prime, etc.)
                        2. Food delivery (Swiggy, Zomato, restaurants)
                        3. Transportation (Uber, Ola, BMTC, flights, trains)
                        4. Shopping (Amazon, Flipkart, Myntra, retail)
                        5. Utilities (electricity, water, gas, internet, telecom)
                        6. Entertainment (movies, events, gaming)
                        7. Healthcare (medical, pharmacy, insurance)
                        8. Education (courses, books, certifications)
                        9. Investment (stocks, mutual funds, SIPs)
                        10. Banking (transfers, fees, charges)
                        
                        RESPONSE FORMAT (JSON):
                        {
                            "sub_queries": [
                                {
                                    "query_id": "unique_id",
                                    "category": "category_name",
                                    "subcategory": "subcategory_name",
                                    "description": "What this sub-query finds",
                                    "mongodb_filter": {
                                        "category": "financial",
                                        "subcategory": "subscription",
                                        "merchant_patterns": ["netflix", "spotify"],
                                        "amount_range": {"$gte": 100, "$lte": 1000}
                                    },
                                    "collection": "financial_transactions",
                                    "expected_fields": ["amount", "merchant_canonical", "transaction_date"],
                                    "priority": 1
                                }
                            ],
                            "total_sub_queries": 10,
                            "coverage_analysis": "Comprehensive coverage of all relevant categories"
                        }
                        
                        RESPOND WITH VALID JSON ONLY."""
                    },
                    {
                        "role": "user",
                        "content": f"Generate sub-queries for this intent analysis: {json.dumps(intent_analysis)}"
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            response_content = response.choices[0].message.content
            sub_query_data = json.loads(response_content)
            
            sub_queries = []
            for sq_data in sub_query_data.get('sub_queries', []):
                sub_query = SubQuery(
                    query_id=sq_data['query_id'],
                    category=sq_data['category'],
                    subcategory=sq_data['subcategory'],
                    description=sq_data['description'],
                    mongodb_query=sq_data['mongodb_filter'],
                    collection_name=sq_data['collection'],
                    expected_fields=sq_data['expected_fields'],
                    priority=sq_data.get('priority', 1)
                )
                sub_queries.append(sub_query)
            
            return sub_queries
            
        except Exception as e:
            logger.error(f"❌ Error generating sub-queries: {e}")
            return []

    async def _execute_sub_queries(self, sub_queries: List[SubQuery], user_id: str) -> List[QueryResult]:
        """Execute all sub-queries and collect results"""
        query_results = []
        
        for sub_query in sub_queries:
            try:
                if sub_query.collection_name == "financial_transactions":
                    results = await self._query_financial_transactions(sub_query.mongodb_query)
                elif sub_query.collection_name == "categorized_emails":
                    results = await self._query_categorized_emails(sub_query.mongodb_query)
                else:
                    results = []
                
                # Calculate totals
                total_amount = sum(r.get('amount', 0) for r in results)
                merchants = list(set(r.get('merchant_canonical', '') for r in results if r.get('merchant_canonical')))
                
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
                continue
        
        return query_results

    async def _query_financial_transactions(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query financial transactions collection"""
        try:
            cursor = financial_transactions_collection.find(query)
            results = await cursor.to_list(length=None)
            return results
        except Exception as e:
            logger.error(f"❌ Error querying financial transactions: {e}")
            return []

    async def _query_categorized_emails(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query categorized emails collection"""
        try:
            cursor = categorized_emails_collection.find(query)
            results = await cursor.to_list(length=None)
            return results
        except Exception as e:
            logger.error(f"❌ Error querying categorized emails: {e}")
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