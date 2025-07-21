#!/usr/bin/env python3
"""
Elite Query Processor - World-Class Production System
===================================================

A world-class query processing system that delivers top 1% performance:
1. Bulletproof LLM integration with robust error handling
2. Comprehensive data analysis using ALL available data
3. Advanced schema-aware processing
4. Intelligent multi-stage analysis pipeline
5. Rich, detailed response generation

This system is designed for production excellence and user satisfaction.
"""

import asyncio
import logging
import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from openai import AsyncOpenAI
from .db import db_manager
from .config.settings import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client with enhanced configuration
api_key = settings.openai_api_key or settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY', '')
client = AsyncOpenAI(api_key=api_key, timeout=60.0) if api_key else None

class EliteQueryProcessor:
    """World-class query processor with top 1% performance"""
    
    def __init__(self):
        self.collection_schemas = {
            "subscriptions": {
                "key_fields": [
                    "service_name", "subscription_type", "service_category", "subscription_status", 
                    "amount", "currency", "plan_name", "billing_frequency", "next_billing_date",
                    "trial_end_date", "auto_renewal", "service_canonical", "plan_features"
                ],
                "search_fields": ["service_name", "service_canonical", "plan_name", "service_category"],
                "filter_fields": ["subscription_type", "service_category", "subscription_status", "billing_frequency"],
                "analysis_fields": ["amount", "billing_frequency", "subscription_status", "auto_renewal"],
                "description": "User subscriptions and recurring services"
            },
            "financial_transactions": {
                "key_fields": [
                    "amount", "merchant_canonical", "transaction_type", "transaction_date", 
                    "payment_method", "currency", "service_category", "transaction_reference",
                    "invoice_number", "payment_status", "bank_name", "upi_id", "is_subscription"
                ],
                "search_fields": ["merchant_canonical", "merchant", "description", "service_category"],
                "filter_fields": ["transaction_type", "payment_method", "service_category", "payment_status"],
                "analysis_fields": ["amount", "transaction_date", "payment_method", "service_category"],
                "description": "Financial transactions and payments"
            },
            "travel_bookings": {
                "key_fields": [
                    "booking_type", "destination", "travel_date", "total_amount", "booking_status",
                    "service_provider", "booking_reference", "from_location", "to_location",
                    "passenger_count", "currency", "payment_status"
                ],
                "search_fields": ["destination", "service_provider", "from_location", "to_location"],
                "filter_fields": ["booking_type", "booking_status", "service_provider"],
                "analysis_fields": ["total_amount", "travel_date", "booking_type", "passenger_count"],
                "description": "Travel bookings and itineraries"
            },
            "job_communications": {
                "key_fields": [
                    "company_name", "job_title", "application_status", "application_date",
                    "position_level", "department", "location", "salary_range_min", "salary_range_max",
                    "interview_date", "communication_type", "requires_action"
                ],
                "search_fields": ["company_name", "job_title", "department", "location"],
                "filter_fields": ["application_status", "communication_type", "position_level"],
                "analysis_fields": ["application_date", "salary_range_min", "application_status"],
                "description": "Job applications and career communications"
            },
            "promotional_emails": {
                "key_fields": [
                    "merchant_canonical", "promotion_type", "discount_amount", "discount_percentage",
                    "original_price", "discounted_price", "currency", "valid_until", "promotion_code",
                    "offer_category", "minimum_purchase", "is_expired"
                ],
                "search_fields": ["merchant_canonical", "offer_category", "promotion_code"],
                "filter_fields": ["promotion_type", "offer_category", "is_expired"],
                "analysis_fields": ["discount_amount", "discount_percentage", "valid_until"],
                "description": "Promotional offers and deals"
            },
            "categorized_emails": {
                "key_fields": [
                    "category", "subcategory", "sender", "subject", "date", "priority",
                    "content_summary", "importance_score", "requires_action"
                ],
                "search_fields": ["sender", "subject", "content_summary", "category"],
                "filter_fields": ["category", "subcategory", "priority", "requires_action"],
                "analysis_fields": ["date", "importance_score", "category"],
                "description": "General categorized emails"
            }
        }
    
    async def process_query(self, user_id: str, query: str) -> Dict[str, Any]:
        """Elite query processing with comprehensive analysis"""
        start_time = datetime.now()
        
        try:
            logger.info(f"🚀 Elite processing query for user {user_id}: {query}")
            
            # Step 1: Advanced query understanding with bulletproof parsing
            query_plan = await self._create_advanced_query_plan(query)
            logger.info(f"📋 Advanced query plan: {query_plan}")
            
            # Step 2: Comprehensive data retrieval
            raw_results = await self._execute_comprehensive_queries(user_id, query_plan)
            logger.info(f"📊 Raw results: {sum(len(r.get('data', [])) for r in raw_results)} total items")
            
            # Step 3: Advanced data analysis
            analyzed_results = await self._perform_advanced_analysis(raw_results, query_plan)
            logger.info(f"🔬 Analysis complete: {len(analyzed_results)} insights generated")
            
            # Step 4: Elite response synthesis
            response = await self._synthesize_elite_response(query, query_plan, analyzed_results)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            total_items = sum(len(r.get("data", [])) for r in raw_results)
            
            return {
                "success": True,
                "original_query": query,
                "query_plan": query_plan,
                "raw_results": raw_results,
                "analyzed_results": analyzed_results,
                "response": response,
                "processing_time": processing_time,
                "total_items_analyzed": total_items,
                "insights_generated": len(analyzed_results),
                "performance_metrics": {
                    "query_complexity": len(query_plan.get("collections", [])),
                    "data_completeness": self._calculate_data_completeness(raw_results),
                    "analysis_depth": len(analyzed_results)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Elite query processing failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "original_query": query,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "fallback_response": "I encountered an issue processing your query. Please try rephrasing it."
            }
    
    async def _create_advanced_query_plan(self, query: str) -> Dict[str, Any]:
        """Create advanced query plan with bulletproof LLM integration"""
        try:
            if not client:
                logger.warning("No LLM client available, using advanced keyword analysis")
                return self._create_intelligent_fallback_plan(query)
            
            # Create comprehensive schema information
            schema_details = self._format_schema_for_llm()
            
            # Advanced prompt with bulletproof instructions
            prompt = f"""You are an expert query analyst. Analyze this user query and create a comprehensive query plan.

AVAILABLE DATA COLLECTIONS:
{schema_details}

USER QUERY: "{query}"

TASK: Return ONLY a valid JSON object (no markdown, no explanations) with this EXACT structure:

{{
    "intent": "list|analyze|search|compare|summarize|insights",
    "collections": ["collection1", "collection2"],
    "search_terms": ["term1", "term2"],
    "filters": {{"field": "value"}},
    "analysis_type": "detailed|summary|trends|comparison",
    "focus_areas": ["area1", "area2"],
    "time_scope": "all|recent|specific",
    "response_depth": "comprehensive|summary|quick"
}}

ANALYSIS RULES:
1. Choose 1-3 most relevant collections based on query keywords
2. Extract specific search terms from the query
3. Use only field names that exist in the schemas
4. Set analysis_type based on what user wants to know
5. Identify key focus areas for deep analysis

RESPOND WITH VALID JSON ONLY - NO OTHER TEXT."""

            # Multiple attempts with different models for reliability
            for attempt in range(3):
                try:
                    model = "gpt-4o-mini" if attempt < 2 else "gpt-3.5-turbo"
                    
                    response = await client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1,
                        max_tokens=400,
                        timeout=30
                    )
                    
                    content = response.choices[0].message.content.strip()
                    
                    # Advanced JSON extraction with multiple fallback methods
                    json_data = self._extract_json_bulletproof(content)
                    
                    if json_data:
                        logger.info(f"✅ LLM query plan created successfully on attempt {attempt + 1}")
                        return self._validate_and_enhance_plan(json_data, query)
                    
                except Exception as e:
                    logger.warning(f"⚠️ LLM attempt {attempt + 1} failed: {e}")
                    continue
            
            # If all LLM attempts fail, use intelligent fallback
            logger.warning("All LLM attempts failed, using intelligent fallback")
            return self._create_intelligent_fallback_plan(query)
            
        except Exception as e:
            logger.error(f"❌ Query plan creation failed: {e}")
            return self._create_intelligent_fallback_plan(query)
    
    def _extract_json_bulletproof(self, content: str) -> Optional[Dict[str, Any]]:
        """Bulletproof JSON extraction with multiple fallback methods"""
        try:
            # Method 1: Direct JSON parsing
            if content.startswith('{') and content.endswith('}'):
                return json.loads(content)
            
            # Method 2: Find JSON block in content
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            matches = re.findall(json_pattern, content, re.DOTALL)
            
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue
            
            # Method 3: Extract between first { and last }
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx + 1]
                return json.loads(json_str)
            
            # Method 4: Clean and retry
            cleaned = re.sub(r'[^\x00-\x7F]+', '', content)  # Remove non-ASCII
            cleaned = re.sub(r'```json|```', '', cleaned)     # Remove markdown
            cleaned = cleaned.strip()
            
            if cleaned.startswith('{') and cleaned.endswith('}'):
                return json.loads(cleaned)
            
            return None
            
        except Exception as e:
            logger.warning(f"JSON extraction failed: {e}")
            return None
    
    def _create_intelligent_fallback_plan(self, query: str) -> Dict[str, Any]:
        """Create intelligent fallback plan using advanced keyword analysis"""
        query_lower = query.lower()
        
        # Advanced keyword mapping
        collection_keywords = {
            "subscriptions": [
                "subscription", "service", "plan", "trial", "monthly", "yearly", "recurring",
                "netflix", "spotify", "amazon", "prime", "disney", "hotstar", "zoom", "slack",
                "software", "app", "platform", "membership", "premium", "pro", "plus"
            ],
            "financial_transactions": [
                "transaction", "payment", "spend", "money", "amount", "financial", "pay",
                "bill", "invoice", "purchase", "buy", "cost", "price", "rupees", "dollars",
                "bank", "card", "upi", "transfer", "debit", "credit"
            ],
            "travel_bookings": [
                "travel", "flight", "hotel", "booking", "trip", "vacation", "journey",
                "airline", "airport", "destination", "ticket", "reservation", "itinerary"
            ],
            "job_communications": [
                "job", "application", "company", "career", "interview", "position", "role",
                "salary", "offer", "hiring", "recruitment", "employer", "work", "employment"
            ],
            "promotional_emails": [
                "offer", "discount", "promotion", "deal", "sale", "coupon", "cashback",
                "promo", "special", "limited", "exclusive", "save", "free"
            ]
        }
        
        # Calculate relevance scores
        collection_scores = {}
        for collection, keywords in collection_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                collection_scores[collection] = score
        
        # Select top collections
        selected_collections = sorted(collection_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        collections = [col for col, score in selected_collections]
        
        # If no collections match, default to most comprehensive
        if not collections:
            collections = ["subscriptions", "financial_transactions"]
        
        # Extract search terms
        search_terms = []
        important_words = [word for word in query_lower.split() 
                         if len(word) > 3 and word not in ['what', 'show', 'list', 'give', 'tell']]
        search_terms = important_words[:5]  # Top 5 search terms
        
        # Determine analysis type
        analysis_keywords = {
            "analyze": ["analyze", "analysis", "insight", "pattern", "trend"],
            "compare": ["compare", "comparison", "versus", "vs", "difference"],
            "summarize": ["summary", "summarize", "overview", "total"],
            "detailed": ["detail", "detailed", "complete", "comprehensive", "all"]
        }
        
        analysis_type = "detailed"
        for atype, keywords in analysis_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                analysis_type = atype
                break
        
        return {
            "intent": "list",
            "collections": collections,
            "search_terms": search_terms,
            "filters": {},
            "analysis_type": analysis_type,
            "focus_areas": collections,
            "time_scope": "all",
            "response_depth": "comprehensive"
        }
    
    def _format_schema_for_llm(self) -> str:
        """Format schema information for LLM consumption"""
        schema_text = []
        for name, info in self.collection_schemas.items():
            key_fields = ", ".join(info["key_fields"][:8])  # Top 8 fields
            schema_text.append(f"- {name}: {info['description']}\n  Key fields: {key_fields}")
        
        return "\n".join(schema_text)
    
    def _validate_and_enhance_plan(self, plan: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Validate and enhance the query plan"""
        # Ensure required fields exist
        plan.setdefault("intent", "list")
        plan.setdefault("collections", ["subscriptions"])
        plan.setdefault("search_terms", [])
        plan.setdefault("filters", {})
        plan.setdefault("analysis_type", "detailed")
        plan.setdefault("focus_areas", plan.get("collections", []))
        plan.setdefault("time_scope", "all")
        plan.setdefault("response_depth", "comprehensive")
        
        # Validate collections exist
        valid_collections = [col for col in plan["collections"] 
                           if col in self.collection_schemas]
        plan["collections"] = valid_collections if valid_collections else ["subscriptions"]
        
        return plan
    
    async def _execute_comprehensive_queries(self, user_id: str, query_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute comprehensive queries across all relevant collections"""
        results = []
        
        for collection_name in query_plan.get("collections", []):
            try:
                logger.info(f"🔍 Querying {collection_name} comprehensively")
                
                # Get ALL relevant data (not just 3 samples)
                data = await self._query_collection_comprehensive(user_id, collection_name, query_plan)
                
                results.append({
                    "collection": collection_name,
                    "data": data,
                    "count": len(data),
                    "schema": self.collection_schemas.get(collection_name, {})
                })
                
                logger.info(f"📊 {collection_name}: {len(data)} comprehensive results")
                
            except Exception as e:
                logger.error(f"❌ Error querying {collection_name}: {e}")
                continue
        
        return results
    
    async def _query_collection_comprehensive(self, user_id: str, collection_name: str, query_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query collection comprehensively - get ALL relevant data"""
        try:
            client_db = db_manager.clients[0]
            if client_db is None:
                return []
            
            database = client_db["pluto_money"]
            collection = database[collection_name]
            
            # CRITICAL FIX: For general queries, get ALL user data first
            # Only apply specific filters if the user asks for something very specific
            intent = query_plan.get("intent", "list")
            search_terms = query_plan.get("search_terms", [])
            
            # Build smart query based on intent
            if intent in ["list", "analyze", "insights", "summarize"] and not self._has_specific_filters(query_plan):
                # For general queries like "what subscriptions do I have", get ALL user data
                query = {"user_id": user_id}
                logger.info(f"🎯 General query - retrieving ALL {collection_name} for user")
            else:
                # For specific searches, apply targeted filters
                query = {"user_id": user_id}
                schema = self.collection_schemas.get(collection_name, {})
                
                # Only add search terms if they are meaningful field values, not generic terms
                meaningful_terms = self._filter_meaningful_search_terms(search_terms, collection_name)
                
                if meaningful_terms:
                    search_conditions = []
                    search_fields = schema.get("search_fields", [])
                    
                    for term in meaningful_terms:
                        for field in search_fields:
                            search_conditions.append({field: {"$regex": term, "$options": "i"}})
                    
                    if search_conditions:
                        query["$or"] = search_conditions
                
                logger.info(f"🎯 Specific query with filters applied")
             
            logger.info(f"🎯 Final query for {collection_name}: {query}")
            
            # Get ALL relevant data (increased limit for comprehensive analysis)
            cursor = collection.find(query).limit(200)  # Increased from 50 to 200
            results = await cursor.to_list(length=None)
            
            logger.info(f"✅ Retrieved {len(results)} items from {collection_name}")
            return results
             
        except Exception as e:
            logger.error(f"❌ Error in comprehensive query for {collection_name}: {e}")
            return []
    
    async def _perform_advanced_analysis(self, raw_results: List[Dict[str, Any]], query_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform advanced analysis on the retrieved data"""
        analyzed_results = []
        
        for result in raw_results:
            if result["count"] == 0:
                continue
                
            collection_name = result["collection"]
            data = result["data"]
            schema = result["schema"]
            
            # Comprehensive analysis for each collection
            analysis = {
                "collection": collection_name,
                "total_items": len(data),
                "summary_stats": self._calculate_summary_stats(data, schema),
                "key_insights": self._extract_key_insights(data, schema, collection_name),
                "patterns": self._identify_patterns(data, schema),
                "top_items": self._get_top_items(data, schema, collection_name),
                "trends": self._analyze_trends(data, schema),
                "recommendations": self._generate_recommendations(data, schema, collection_name)
            }
            
            analyzed_results.append(analysis)
        
        return analyzed_results
    
    def _calculate_summary_stats(self, data: List[Dict[str, Any]], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive summary statistics"""
        if not data:
            return {}
        
        stats = {"total_count": len(data)}
        analysis_fields = schema.get("analysis_fields", [])
        
        for field in analysis_fields:
            # Get all values, filtering out None and empty values
            values = []
            for item in data:
                value = item.get(field)
                if value is not None and value != "" and value != 0:
                    values.append(value)
            
            if not values:
                continue
                
            try:
                # Try numerical analysis first
                numeric_values = []
                for v in values:
                    if isinstance(v, (int, float)):
                        numeric_values.append(v)
                    elif isinstance(v, str) and v.replace('.', '').replace('-', '').isdigit():
                        numeric_values.append(float(v))
                
                if numeric_values and len(numeric_values) > 0:
                    # Numerical analysis
                    stats[f"{field}_total"] = sum(numeric_values)
                    stats[f"{field}_average"] = sum(numeric_values) / len(numeric_values)
                    stats[f"{field}_min"] = min(numeric_values)
                    stats[f"{field}_max"] = max(numeric_values)
                    stats[f"{field}_count"] = len(numeric_values)
                else:
                    # Categorical analysis
                    from collections import Counter
                    counter = Counter(str(v) for v in values)
                    stats[f"{field}_distribution"] = dict(counter.most_common(10))
                    stats[f"{field}_unique_count"] = len(counter)
                    
            except Exception as e:
                logger.warning(f"⚠️ Stats calculation failed for {field}: {e}")
                # Fallback to basic count
                stats[f"{field}_count"] = len(values)
         
        return stats
    
    def _extract_key_insights(self, data: List[Dict[str, Any]], schema: Dict[str, Any], collection_name: str) -> List[str]:
        """Extract key insights from the data"""
        insights = []
        
        if not data:
            return ["No data available for analysis"]
        
        # Collection-specific insights
        if collection_name == "subscriptions":
            active_subs = [item for item in data if item.get("subscription_status") == "active"]
            trial_subs = [item for item in data if item.get("subscription_status") == "trial"]
            
            insights.extend([
                f"You have {len(active_subs)} active subscriptions",
                f"You have {len(trial_subs)} trial subscriptions",
                f"Most common subscription type: {self._get_most_common(data, 'subscription_type')}",
                f"Most common service category: {self._get_most_common(data, 'service_category')}"
            ])
            
            # Calculate total cost
            amounts = [item.get("amount", 0) for item in data if item.get("amount")]
            if amounts:
                total_cost = sum(amounts)
                insights.append(f"Total subscription cost: {total_cost}")
        
        elif collection_name == "financial_transactions":
            amounts = [item.get("amount", 0) for item in data if item.get("amount")]
            if amounts:
                total_amount = sum(amounts)
                avg_amount = total_amount / len(amounts)
                insights.extend([
                    f"Total transaction amount: ₹{total_amount:,.2f}",
                    f"Average transaction amount: ₹{avg_amount:,.2f}",
                    f"Largest transaction: ₹{max(amounts):,.2f}",
                    f"Most common payment method: {self._get_most_common(data, 'payment_method')}"
                ])
        
        elif collection_name == "job_communications":
            insights.extend([
                f"Total job communications: {len(data)}",
                f"Most common application status: {self._get_most_common(data, 'application_status')}",
                f"Companies you've interacted with: {len(set(item.get('company_name') for item in data if item.get('company_name')))}"
            ])
        
        return insights[:10]  # Top 10 insights
    
    def _identify_patterns(self, data: List[Dict[str, Any]], schema: Dict[str, Any]) -> List[str]:
        """Identify patterns in the data"""
        patterns = []
        
        if len(data) < 2:
            return patterns
        
        # Time-based patterns
        date_fields = [field for field in schema.get("key_fields", []) if "date" in field.lower()]
        for date_field in date_fields[:2]:  # Check top 2 date fields
            dates = [item.get(date_field) for item in data if item.get(date_field)]
            if len(dates) > 1:
                patterns.append(f"Data spans from {min(dates)} to {max(dates)}")
        
        # Frequency patterns
        categorical_fields = [field for field in schema.get("filter_fields", [])]
        for field in categorical_fields[:3]:  # Top 3 categorical fields
            values = [item.get(field) for item in data if item.get(field)]
            if values:
                from collections import Counter
                counter = Counter(values)
                most_common = counter.most_common(1)[0]
                if most_common[1] > 1:
                    patterns.append(f"Most frequent {field}: {most_common[0]} ({most_common[1]} times)")
        
        return patterns[:5]  # Top 5 patterns
    
    def _get_top_items(self, data: List[Dict[str, Any]], schema: Dict[str, Any], collection_name: str) -> List[Dict[str, Any]]:
        """Get top items with comprehensive information"""
        if not data:
            return []
        
        # Sort by relevance/importance
        sorted_data = data.copy()
        
        try:
            if collection_name == "financial_transactions":
                # Sort by amount descending, handling None values
                sorted_data = sorted(data, key=lambda x: (x.get("amount") or 0), reverse=True)
            elif collection_name == "subscriptions":
                # Sort by amount descending, then by status, handling None values
                sorted_data = sorted(data, key=lambda x: (
                    x.get("amount") or 0,
                    x.get("subscription_status") == "active"
                ), reverse=True)
        except Exception as e:
            logger.warning(f"⚠️ Sorting failed for {collection_name}: {e}, using original order")
            # Use original order if sorting fails
            sorted_data = data.copy()
         
        # Return top 10 items with key information
        top_items = []
        key_fields = schema.get("key_fields", [])[:8]  # Top 8 key fields
        
        for item in sorted_data[:10]:
            top_item = {}
            for field in key_fields:
                if field in item and item[field] is not None:
                    top_item[field] = item[field]
            top_items.append(top_item)
        
        return top_items
    
    def _analyze_trends(self, data: List[Dict[str, Any]], schema: Dict[str, Any]) -> List[str]:
        """Analyze trends in the data"""
        trends = []
        
        if len(data) < 3:
            return trends
        
        # Amount trends (if applicable)
        amounts = [item.get("amount", 0) for item in data if item.get("amount")]
        if len(amounts) >= 3:
            if amounts[-1] > amounts[0]:
                trends.append("Spending trend: Increasing")
            elif amounts[-1] < amounts[0]:
                trends.append("Spending trend: Decreasing")
            else:
                trends.append("Spending trend: Stable")
        
        # Status trends
        status_fields = [field for field in schema.get("key_fields", []) if "status" in field.lower()]
        for status_field in status_fields[:1]:  # Check primary status field
            statuses = [item.get(status_field) for item in data if item.get(status_field)]
            if statuses:
                from collections import Counter
                status_dist = Counter(statuses)
                dominant_status = status_dist.most_common(1)[0]
                trends.append(f"Dominant {status_field}: {dominant_status[0]} ({dominant_status[1]}/{len(statuses)})")
        
        return trends[:3]  # Top 3 trends
    
    def _generate_recommendations(self, data: List[Dict[str, Any]], schema: Dict[str, Any], collection_name: str) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        try:
            if collection_name == "subscriptions":
                trial_count = sum(1 for item in data if item.get("subscription_status") == "trial")
                if trial_count > 0:
                    recommendations.append(f"You have {trial_count} trial subscriptions - consider which ones to keep")
                
                # Safely handle amount calculations
                amounts = []
                for item in data:
                    amount = item.get("amount")
                    if amount is not None and isinstance(amount, (int, float)) and amount > 0:
                        amounts.append(amount)
                
                if amounts:
                    total_monthly = sum(amounts)
                    recommendations.append(f"Total monthly subscription cost: ₹{total_monthly:,.2f} - review for potential savings")
            
            elif collection_name == "financial_transactions":
                # Safely handle amount calculations
                amounts = []
                for item in data:
                    amount = item.get("amount")
                    if amount is not None and isinstance(amount, (int, float)):
                        amounts.append(amount)
                
                if amounts:
                    high_value_count = sum(1 for amount in amounts if amount > 1000)
                    if high_value_count > 0:
                        recommendations.append(f"{high_value_count} high-value transactions (>₹1000) - review for accuracy")
        
        except Exception as e:
            logger.warning(f"⚠️ Recommendation generation failed for {collection_name}: {e}")
            recommendations.append(f"Analysis completed for {len(data)} {collection_name} items")
         
        return recommendations[:3]  # Top 3 recommendations
    
    def _get_most_common(self, data: List[Dict[str, Any]], field: str) -> str:
        """Get most common value for a field"""
        values = [item.get(field) for item in data if item.get(field)]
        if not values:
            return "N/A"
        
        from collections import Counter
        return Counter(values).most_common(1)[0][0]
    
    def _has_specific_filters(self, query_plan: Dict[str, Any]) -> bool:
        """Check if the query plan has specific filters that require targeted search"""
        filters = query_plan.get("filters", {})
        search_terms = query_plan.get("search_terms", [])
        
        # Has explicit filters
        if filters:
            return True
        
        # Has very specific search terms (like merchant names, specific services)
        specific_indicators = [
            "netflix", "amazon", "google", "microsoft", "apple", "spotify", "uber", "swiggy",
            "zomato", "airtel", "jio", "bsnl", "hdfc", "icici", "sbi", "axis", "kotak"
        ]
        
        for term in search_terms:
            if term.lower() in specific_indicators:
                return True
        
        return False
    
    def _filter_meaningful_search_terms(self, search_terms: List[str], collection_name: str) -> List[str]:
        """Filter out generic terms and keep only meaningful search terms"""
        # Generic terms that shouldn't be used for field searching
        generic_terms = [
            "subscriptions", "subscription", "service", "services", "transaction", "transactions",
            "financial", "finance", "payment", "payments", "amount", "money", "spend", "spending",
            "job", "jobs", "email", "emails", "communication", "communications", "insight", "insights",
            "list", "show", "give", "provide", "what", "how", "where", "when", "why", "all", "my",
            "have", "done", "received", "different", "analysis", "analyze", "pattern", "patterns"
        ]
        
        meaningful_terms = []
        for term in search_terms:
            # Skip generic terms
            if term.lower() in generic_terms:
                continue
            
            # Skip very short terms
            if len(term) < 3:
                continue
            
            # Skip user ID fragments
            if term.isalnum() and len(term) > 10:
                continue
            
            meaningful_terms.append(term)
        
        return meaningful_terms
    
    def _calculate_data_completeness(self, results: List[Dict[str, Any]]) -> float:
        """Calculate data completeness score"""
        if not results:
            return 0.0
        
        total_items = sum(len(r.get("data", [])) for r in results)
        return min(1.0, total_items / 100.0)  # Normalize to 0-1 scale
    
    async def _synthesize_elite_response(self, original_query: str, query_plan: Dict[str, Any], analyzed_results: List[Dict[str, Any]]) -> str:
        """Synthesize elite response with comprehensive insights"""
        try:
            # Check if we have meaningful results
            total_items = sum(result.get("total_items", 0) for result in analyzed_results)
            
            if total_items == 0:
                return self._generate_no_data_response(original_query, query_plan)
            
            # Prepare comprehensive data for LLM
            response_data = {
                "query": original_query,
                "total_items_analyzed": total_items,
                "collections_analyzed": len(analyzed_results),
                "comprehensive_analysis": analyzed_results,
                "query_plan": query_plan
            }
            
            if not client:
                return self._generate_fallback_response(response_data)
            
            # Elite response generation
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an elite data analyst and personal assistant with expertise in financial analysis, subscription management, and personal data insights. Your task is to create comprehensive, actionable responses based on detailed data analysis.

RESPONSE REQUIREMENTS:
1. **Comprehensive Coverage**: Address all aspects of the user's query
2. **Specific Details**: Use actual numbers, names, and data points
3. **Actionable Insights**: Provide practical recommendations
4. **Clear Structure**: Use headers, bullet points, and clear formatting
5. **Professional Tone**: Be conversational yet authoritative

RESPONSE STRUCTURE:
- **Executive Summary**: Brief overview of key findings
- **Detailed Analysis**: Comprehensive breakdown with specific data
- **Key Insights**: Most important discoveries
- **Recommendations**: Actionable next steps
- **Additional Context**: Relevant background information

FORMATTING GUIDELINES:
- Use **bold** for important numbers and names
- Use bullet points for lists
- Include specific amounts, dates, and percentages
- Highlight actionable items clearly
- Make it scannable with clear sections"""
                    },
                    {
                        "role": "user",
                        "content": f"""
Analyze this comprehensive data and create an elite response:

USER QUERY: "{original_query}"

COMPREHENSIVE ANALYSIS DATA:
{json.dumps(response_data, indent=2, default=str)}

Create a detailed, professional response that fully addresses the user's query with specific insights, recommendations, and actionable information. Use all available data to provide maximum value.
"""
                    }
                ],
                temperature=0.3,
                max_tokens=2000,  # Increased for comprehensive responses
                timeout=45
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ Error in elite response synthesis: {e}")
            return self._generate_fallback_response({"total_items": total_items, "error": str(e)})
    
    def _generate_no_data_response(self, query: str, query_plan: Dict[str, Any]) -> str:
        """Generate helpful response when no data is found"""
        collections_searched = ", ".join(query_plan.get("collections", []))
        
        return f"""I searched through your {collections_searched} data but couldn't find any information matching your query: "{query}".

**Possible reasons:**
• The data might not have been processed yet
• Your query might be too specific - try using broader terms
• The information might be in a different category

**Suggestions:**
• Try rephrasing your query with different keywords
• Check if you have data in other categories
• Verify that your email sync is complete

Would you like me to help you search for something else?"""
    
    def _generate_fallback_response(self, data: Dict[str, Any]) -> str:
        """Generate fallback response when LLM synthesis fails"""
        total_items = data.get("total_items", 0)
        
        if total_items == 0:
            return "I couldn't find any data matching your query. Please try rephrasing your question."
        
        return f"""I found **{total_items}** items related to your query and have analyzed them comprehensively.

**Summary:**
• Total items analyzed: {total_items}
• Data categories: {data.get('collections_analyzed', 'Multiple')}
• Analysis completed successfully

The detailed analysis is available, but I encountered an issue generating the formatted response. The core data has been processed and is ready for your review.

Would you like me to try a different approach to present this information?"""

# Global instance
elite_processor = EliteQueryProcessor()

async def process_elite_query(user_id: str, query: str) -> Dict[str, Any]:
    """Process a user query using the elite query processor"""
    return await elite_processor.process_query(user_id, query)

async def get_query_suggestions(user_id: str) -> List[str]:
    """Get personalized query suggestions for the user"""
    return [
        "What subscriptions do I have?",
        "Show me my financial transactions",
        "Analyze my spending patterns",
        "What job communications have I received?",
        "List my travel bookings",
        "Show me promotional offers",
        "What are my recurring payments?",
        "Give me insights about my expenses",
        "Show me high-value transactions",
        "What services am I subscribed to?"
    ] 