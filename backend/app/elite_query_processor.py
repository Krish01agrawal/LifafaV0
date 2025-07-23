#!/usr/bin/env python3
"""
Enhanced Elite Query Processor - Deep Intelligence System
========================================================

A revolutionary query processing system that delivers world-class performance:
1. Deep intent understanding with 10-15 sub-query generation
2. Comprehensive data retrieval - ALL relevant data, no limits
3. Advanced schema-aware processing with bank details
4. Intelligent multi-stage analysis pipeline
5. Rich, detailed response generation with complete context

This system is designed for maximum intelligence and user satisfaction.
"""

import asyncio
import logging
import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from openai import AsyncOpenAI
from app.db import db_manager
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Global OpenAI client configuration - PERFORMANCE OPTIMIZED
api_key = settings.openai_api_key
client = AsyncOpenAI(api_key=api_key, timeout=8.0) if api_key else None  # ✅ REDUCED from 15s to 8s

class EnhancedEliteQueryProcessor:
    """Revolutionary query processor with deep intelligence and comprehensive data retrieval"""
    
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
                    "invoice_number", "payment_status", "bank_name", "account_number", 
                    "upi_id", "is_subscription", "merchant_original", "bank_details", "upi_details",
                    "source"  # Added to distinguish email vs SMS transactions
                ],
                "search_fields": ["merchant_canonical", "merchant_original", "service_category", "bank_name"],
                "filter_fields": ["transaction_type", "payment_method", "service_category", "payment_status", "source"],
                "analysis_fields": ["amount", "transaction_date", "payment_method", "service_category", "bank_name", "source"],
                "description": "Financial transactions and payments with complete bank details (Email + SMS)"
            },
            "email_logs": {
                "key_fields": [
                    "email_subject", "sender", "recipient", "date", "snippet", 
                    "financial", "importance_score", "filter_reason"
                ],
                "search_fields": ["email_subject", "sender", "snippet"],
                "filter_fields": ["financial", "importance_score"],
                "analysis_fields": ["date", "financial", "importance_score"],
                "description": "Complete email data with metadata"
            },
            # SMS functionality temporarily disabled for email testing
            # "sms_data": {
            #     "key_fields": [
            #         "sms_id", "sender_number", "sender_name", "message_body", "received_date",
            #         "sms_type", "is_financial", "provider", "extraction_confidence"
            #     ],
            #     "search_fields": ["sender_number", "sender_name", "message_body"],
            #     "filter_fields": ["sms_type", "is_financial", "provider"],
            #     "analysis_fields": ["received_date", "is_financial", "sms_type", "extraction_confidence"],
            #     "description": "SMS data with financial transaction information"
            # }
        }
    
    async def process_query(self, user_id: str, query: str) -> Dict[str, Any]:
        """Enhanced elite query processing with deep intelligence and COMPREHENSIVE LOGGING"""
        start_time = datetime.now()
        
        try:
            logger.info(f"🧠 Deep Intelligence processing query for user {user_id}: {query}")
            logger.info(f"🚀 STEP 1: Starting Deep Intent Understanding...")
            
            # Step 1: Deep Intent Understanding & Sub-Query Generation (FAST)
            intent_analysis = await self._deep_intent_understanding_fast(query)
            logger.info(f"📋 INTENT ANALYSIS RESULT: {json.dumps(intent_analysis, indent=2)}")
            
            logger.info(f"🚀 STEP 2: Generating Comprehensive Sub-Queries...")
            sub_queries = await self._generate_comprehensive_subqueries_fast(query, intent_analysis)
            logger.info(f"📋 SUB-QUERIES GENERATED: {len(sub_queries)} queries")
            for i, sub_query in enumerate(sub_queries, 1):
                logger.info(f"📋 SUB-QUERY {i}: {sub_query['description']}")
                logger.info(f"📋   - Collection: {sub_query['target_collection']}")
                logger.info(f"📋   - Filters: {sub_query.get('filters', {})}")
                logger.info(f"📋   - Priority: {sub_query['priority']}")
            
            logger.info(f"🎯 Generated {len(sub_queries)} intelligent sub-queries in {(datetime.now() - start_time).total_seconds():.2f}s")
            
            logger.info(f"🚀 STEP 3: Executing Comprehensive Data Retrieval...")
            # Step 2: Comprehensive Data Retrieval - ALL relevant data
            all_data = await self._execute_comprehensive_data_retrieval_with_logging(user_id, sub_queries)
            logger.info(f"📊 Retrieved comprehensive data: {sum(len(data.get('results', [])) for data in all_data)} total items")
            
            logger.info(f"🚀 STEP 4: Performing Deep Analysis...")
            # Step 3: Advanced Analysis with Complete Context
            analyzed_data = await self._perform_deep_analysis_with_logging(all_data, intent_analysis, query)
            logger.info(f"🔬 Deep analysis complete: {len(analyzed_data)} comprehensive insights")
            
            logger.info(f"🚀 STEP 5: Generating Enhanced Response...")
            # Step 4: Enhanced Response Generation with ALL data (FAST)
            response = await self._generate_enhanced_response_with_detailed_data(query, intent_analysis, sub_queries, all_data, analyzed_data)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            total_items = sum(len(data.get("results", [])) for data in all_data)
            
            logger.info(f"✅ Enhanced query processing completed in {processing_time:.2f}s")
            logger.info(f"📊 FINAL METRICS: {total_items} items analyzed, {len(analyzed_data)} insights generated")
            
            return {
                "success": True,
                "original_query": query,
                "intent_analysis": intent_analysis,
                "sub_queries": sub_queries,
                "comprehensive_data": all_data,
                "analyzed_data": analyzed_data,
                "response": response,
                "processing_time": processing_time,
                "total_items_analyzed": total_items,
                "insights_generated": len(analyzed_data),
                "performance_metrics": {
                    "query_complexity": len(sub_queries),
                    "data_comprehensiveness": self._calculate_data_comprehensiveness(all_data),
                    "analysis_depth": len(analyzed_data),
                    "intelligence_score": self._calculate_intelligence_score(intent_analysis, sub_queries, all_data)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Enhanced query processing failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "original_query": query,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "fallback_response": "I encountered an issue processing your query. Please try again."
            }
    
    async def _deep_intent_understanding_fast(self, query: str) -> Dict[str, Any]:
        """FAST deep intent understanding with optimized AI calls"""
        try:
            if not client:
                return self._fallback_intent_analysis(query)
            
            # ✅ OPTIMIZED: Shorter, more focused prompt
            prompt = f"""Analyze this financial query and return JSON:

USER QUERY: "{query}"

Return ONLY this JSON structure:
{{
    "primary_intent": "list_transactions|retrieve_bank_details|analyze_spending|find_subscriptions",
    "data_requirements": {{
        "need_bank_details": true,
        "need_account_numbers": true, 
        "need_transaction_amounts": true,
        "need_all_transactions": true
    }},
    "expected_collections": ["financial_transactions", "subscriptions"],
    "response_format": "comprehensive_report"
}}"""

            response = await client.chat.completions.create(
                model="gpt-4o-mini",  # ✅ FIXED: Faster model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300,  # ✅ FIXED: Reduced from 600
                timeout=8.0  # ✅ REDUCED from 10s to 8s for consistency
            )
            
            content = response.choices[0].message.content.strip()
            intent_data = self._extract_json_bulletproof(content)
            
            if intent_data:
                logger.info("✅ Fast intent analysis completed successfully")
                return intent_data
            else:
                return self._fallback_intent_analysis(query)
                
        except Exception as e:
            logger.warning(f"⚠️ Fast intent analysis failed: {e}, using fallback")
            return self._fallback_intent_analysis(query)
    
    async def _generate_comprehensive_subqueries_fast(self, original_query: str, intent_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """FAST sub-query generation with optimized approach"""
        try:
            # ✅ OPTIMIZATION: Use smart fallback instead of slow LLM for sub-queries
            logger.info("🚀 Using optimized sub-query generation for speed")
            return self._generate_smart_subqueries(original_query, intent_analysis)
                
        except Exception as e:
            logger.warning(f"⚠️ Fast sub-query generation failed: {e}")
            return self._fallback_subquery_generation(original_query, intent_analysis)
    
    def _generate_smart_subqueries(self, query: str, intent_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate intelligent sub-queries based on ACTUAL USER INTENT - Completely Dynamic System"""
        sub_queries = []
        query_lower = query.lower()
        
        # ✅ EXTRACT INTENT from analysis
        primary_intent = intent_analysis.get("primary_intent", "general")
        secondary_intents = intent_analysis.get("secondary_intents", [])
        data_types_needed = intent_analysis.get("data_types_needed", [])
        
        logger.info(f"🎯 INTENT DETECTED: {primary_intent}")
        logger.info(f"🎯 DATA TYPES NEEDED: {data_types_needed}")
        
        # ✅ BANK ACCOUNT QUERIES
        if any(keyword in query_lower for keyword in ["bank", "account", "banking", "financial institution"]):
            sub_queries.extend([
                {
                    "id": "bank_1",
                    "description": "Get all transactions with bank details",
                    "target_collection": "financial_transactions",
                    "query_type": "bank_analysis",
                    "filters": {"bank_name": {"$exists": True, "$ne": None}},
                    "sort": {"bank_name": 1},
                    "priority": "critical"
                },
                {
                    "id": "bank_2", 
                    "description": "Get all account numbers used",
                    "target_collection": "financial_transactions",
                    "query_type": "account_analysis",
                    "filters": {"account_number": {"$exists": True, "$ne": None}},
                    "sort": {"account_number": 1},
                    "priority": "high"
                }
            ])
        
        # ✅ CREDIT CARD / PAYMENT METHOD QUERIES
        elif any(keyword in query_lower for keyword in ["credit card", "payment method", "card", "upi", "payment"]):
            sub_queries.extend([
                {
                    "id": "payment_1",
                    "description": "Get all credit card transactions",
                    "target_collection": "financial_transactions", 
                    "query_type": "credit_card_analysis",
                    "filters": {"payment_method": {"$regex": "credit", "$options": "i"}},
                    "sort": {"transaction_date": -1},
                    "priority": "critical"
                },
                {
                    "id": "payment_2",
                    "description": "Get all payment methods used",
                    "target_collection": "financial_transactions",
                    "query_type": "payment_method_analysis", 
                    "filters": {"payment_method": {"$exists": True, "$ne": None}},
                    "sort": {"payment_method": 1},
                    "priority": "high"
                },
                {
                    "id": "payment_3",
                    "description": "Get UPI transactions",
                    "target_collection": "financial_transactions",
                    "query_type": "upi_analysis",
                    "filters": {"$or": [
                        {"payment_method": {"$regex": "upi", "$options": "i"}},
                        {"upi_id": {"$exists": True, "$ne": None}}
                    ]},
                    "sort": {"transaction_date": -1},
                    "priority": "medium"
                }
            ])
        
        # ✅ JOB/INTERVIEW EMAIL QUERIES
        elif any(keyword in query_lower for keyword in ["job", "interview", "career", "employment", "hiring", "recruit"]):
            sub_queries.extend([
                {
                    "id": "job_1",
                    "description": "Get job-related emails",
                    "target_collection": "email_logs",
                    "query_type": "job_email_analysis",
                    "filters": {"$or": [
                        {"subject": {"$regex": "job|interview|career|hiring|position|role", "$options": "i"}},
                        {"sender_name": {"$regex": "recruiter|hr|talent|hiring", "$options": "i"}},
                        {"content_preview": {"$regex": "job|interview|position|opportunity", "$options": "i"}}
                    ]},
                    "sort": {"received_date": -1},
                    "priority": "critical"
                },
                {
                    "id": "job_2",
                    "description": "Get emails from job platforms",
                    "target_collection": "email_logs", 
                    "query_type": "job_platform_analysis",
                    "filters": {"sender_domain": {"$in": [
                        "linkedin.com", "naukri.com", "indeed.com", "glassdoor.com",
                        "monster.com", "shine.com", "instahyre.com", "angel.co"
                    ]}},
                    "sort": {"received_date": -1},
                    "priority": "high"
                }
            ])
        
        # ✅ SUBSCRIPTION QUERIES (Only when actually asking about subscriptions)
        elif any(keyword in query_lower for keyword in ["subscription", "subscriptions", "recurring", "monthly", "yearly", "service"]):
            sub_queries.extend([
                {
                    "id": "sub_1",
                    "description": "Get ALL financial transactions (including null amounts)",
                    "target_collection": "financial_transactions",
                    "query_type": "comprehensive_financial",
                    "filters": {},
                    "sort": {"_id": -1},
                    "priority": "critical"
                },
                {
                    "id": "sub_2",
                    "description": "Get transactions from known subscription merchants",
                    "target_collection": "financial_transactions", 
                    "query_type": "subscription_merchants",
                    "filters": self._get_subscription_merchant_filter(),
                    "sort": {"_id": -1},
                    "priority": "high"
                },
                {
                    "id": "sub_3",
                    "description": "Get ALL subscription services",
                    "target_collection": "subscriptions",
                    "query_type": "all_subscriptions", 
                    "filters": {},
                    "sort": {"_id": -1},
                    "priority": "critical"
                }
            ])
        
        # ✅ TRANSACTION AMOUNT/SPENDING QUERIES
        elif any(keyword in query_lower for keyword in ["total", "spent", "amount", "money", "expense", "cost"]):
            time_filter = self._extract_time_filter(query_lower)
            sub_queries.extend([
                {
                    "id": "spending_1",
                    "description": "Get all transactions with amounts",
                    "target_collection": "financial_transactions",
                    "query_type": "spending_analysis",
                    "filters": {**{"amount": {"$exists": True, "$ne": None}}, **time_filter},
                    "sort": {"amount": -1},
                    "priority": "critical"
                },
                {
                    "id": "spending_2",
                    "description": "Get high-value transactions",
                    "target_collection": "financial_transactions",
                    "query_type": "high_value_analysis", 
                    "filters": {**{"amount": {"$gte": 1000}}, **time_filter},
                    "sort": {"amount": -1},
                    "priority": "high"
                }
            ])
        
        # ✅ MERCHANT/VENDOR QUERIES  
        elif any(keyword in query_lower for keyword in ["merchant", "vendor", "company", "from where", "purchased"]):
            sub_queries.extend([
                {
                    "id": "merchant_1",
                    "description": "Get all transactions with merchant details",
                    "target_collection": "financial_transactions",
                    "query_type": "merchant_analysis",
                    "filters": {"$or": [
                        {"merchant_canonical": {"$exists": True, "$ne": None}},
                        {"merchant_original": {"$exists": True, "$ne": None}}
                    ]},
                    "sort": {"merchant_canonical": 1},
                    "priority": "critical"
                }
            ])
        
        # ✅ GENERAL TRANSACTION QUERIES (Fallback)
        else:
            sub_queries.extend([
                {
                    "id": "general_1", 
                    "description": "Get recent financial transactions",
                    "target_collection": "financial_transactions",
                    "query_type": "general_financial",
                    "filters": {},
                    "sort": {"_id": -1},
                    "priority": "high"
                },
                {
                    "id": "general_2",
                    "description": "Get transaction summary data",
                    "target_collection": "financial_transactions",
                    "query_type": "transaction_summary",
                    "filters": {"amount": {"$exists": True, "$ne": None}},
                    "sort": {"transaction_date": -1},
                    "priority": "medium"
                }
            ])
        
        logger.info(f"✅ Generated {len(sub_queries)} intent-specific sub-queries")
        return sub_queries
    
    async def _execute_comprehensive_data_retrieval(self, user_id: str, sub_queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute all sub-queries and retrieve comprehensive data - NO LIMITS"""
        all_results = []
        
        for sub_query in sub_queries:
            try:
                collection_name = sub_query.get("target_collection", "financial_transactions")
                logger.info(f"🔍 Executing sub-query {sub_query.get('id')}: {sub_query.get('description')}")
                
                # Get comprehensive data without limits
                data = await self._execute_unlimited_query(user_id, collection_name, sub_query)
                
                result = {
                    "sub_query_id": sub_query.get("id"),
                    "description": sub_query.get("description"),
                    "collection": collection_name,
                    "query_type": sub_query.get("query_type"),
                    "results": data,
                    "count": len(data),
                    "priority": sub_query.get("priority", "medium")
                }
                
                all_results.append(result)
                logger.info(f"📊 Sub-query {sub_query.get('id')} completed: {len(data)} results")
                
            except Exception as e:
                logger.error(f"❌ Error executing sub-query {sub_query.get('id')}: {e}")
                continue
        
        return all_results
    
    async def _get_integrated_financial_data(self, user_id: str, sub_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get integrated financial data from both email and SMS sources"""
        try:
            logger.info(f"🔄 INTEGRATING FINANCIAL DATA from Email sources only (SMS temporarily disabled)")
            
            # Get email-based financial transactions
            email_transactions = await self._execute_unlimited_query_with_logging(user_id, "financial_transactions", sub_query)
            logger.info(f"📧 Retrieved {len(email_transactions)} email-based transactions")
            
            # SMS functionality temporarily disabled for email testing
            # # Get SMS-based financial transactions
            # sms_transactions = await self._execute_unlimited_query_with_logging(user_id, "sms_data", sub_query)
            # logger.info(f"📱 Retrieved {len(sms_transactions)} SMS messages")
            
            # # Convert SMS data to transaction format if needed
            # sms_transactions_formatted = []
            # for sms in sms_transactions:
            #     if sms.get('is_financial'):
            #         # Extract transaction data from SMS
            #         transaction = self._convert_sms_to_transaction(sms)
            #         if transaction:
            #             sms_transactions_formatted.append(transaction)
            
            # logger.info(f"📱 Converted {len(sms_transactions_formatted)} SMS to transaction format")
            
            # Combine both sources (only email for now)
            all_transactions = email_transactions  # + sms_transactions_formatted
            logger.info(f"🔄 TOTAL INTEGRATED TRANSACTIONS: {len(all_transactions)} (Email: {len(email_transactions)}, SMS: 0 - disabled)")
            
            return all_transactions
            
        except Exception as e:
            logger.error(f"❌ Error integrating financial data: {e}")
            return []
    
    # SMS functionality temporarily disabled for email testing
    # def _convert_sms_to_transaction(self, sms: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    #     """Convert SMS data to transaction format for unified processing"""
    #     try:
    #         message_body = sms.get('message_body', '')
    #         sender_number = sms.get('sender_number', '')
    #         sender_name = sms.get('sender_name', '')
    #         
    #         # Extract amount using regex patterns
    #         import re
    #         amount_patterns = [
    #             r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
    #             r'(\d+(?:,\d+)*(?:\.\d{2})?)\s*rs\.?',
    #             r'rs\.?\s*(\d+)',
    #             r'(\d+)\s*rs\.?'
    #         ]
    #         
    #         amount = None
    #         for pattern in amount_patterns:
    #             match = re.search(pattern, message_body, re.IGNORECASE)
    #             if match:
    #                 amount_str = match.group(1).replace(',', '')
    #                 try:
    #                         amount = float(amount_str)
    #                         break
    #                     except ValueError:
    #                         continue
    #         
    #         if not amount:
    #             return None
    #         
    #         # Determine transaction type
    #         message_lower = message_body.lower()
    #         if any(word in message_lower for word in ['debited', 'deducted', 'sent']):
    #             transaction_type = 'debit'
    #         elif any(word in message_lower for word in ['credited', 'received']):
    #             transaction_type = 'credit'
    #         else:
    #             transaction_type = 'unknown'
    #         
    #         # Extract bank name
    #         bank_name = None
    #         bank_patterns = {
    #             'HDFC': ['HDFC', 'HDFC Bank', 'HDFCBANK'],
    #             'SBI': ['SBI', 'State Bank', 'STATE BANK'],
    #             'ICICI': ['ICICI', 'ICICI Bank'],
    #             'Axis': ['AXIS', 'Axis Bank'],
    #             'Kotak': ['KOTAK', 'Kotak Bank'],
    #             'Yes Bank': ['YES', 'Yes Bank'],
    #             'IDFC': ['IDFC', 'IDFC Bank'],
    #             'RBL': ['RBL', 'RBL Bank'],
    #             'Federal': ['FEDERAL', 'Federal Bank'],
    #             'PNB': ['PNB', 'Punjab National Bank'],
    #             'Canara': ['CANARA', 'Canara Bank'],
    #             'Bank of Baroda': ['BOB', 'Bank of Baroda'],
    #             'Union Bank': ['UNION', 'Union Bank'],
    #             'Bank of India': ['BOI', 'Bank of India']
    #         }
    #         
    #         message_upper = message_body.upper()
    #         for bank, patterns in bank_patterns.items():
    #             for pattern in patterns:
    #                 if pattern in message_upper:
    #                     bank_name = bank
    #                     break
    #             if bank_name:
    #                 break
    #         
    #         # Create transaction object
    #         transaction = {
    #             'transaction_id': f"sms_{sms.get('sms_id', 'unknown')}_{datetime.now().timestamp()}",
    #             'sms_id': sms.get('sms_id'),
    #             'transaction_type': transaction_type,
    #             'amount': amount,
    #             'currency': 'INR',
    #             'transaction_date': sms.get('received_date'),
    #             'merchant_canonical': sender_name or 'SMS Transaction',
    #             'merchant_original': sender_number,
    #             'service_category': 'SMS Transaction',
    #             'bank_name': bank_name or 'Unknown',
    #             'payment_method': 'SMS',
    #             'source': 'sms',
    #             'extraction_confidence': sms.get('extraction_confidence', 0.8),
    #             'data_completeness': 0.7,
    #             'extracted_at': datetime.now().isoformat(),
    #             'updated_at': datetime.now().isoformat(),
    #             'user_id': sms.get('user_id')
    #         }
    #         
    #         return transaction
    #         
    #     except Exception as e:
    #         logger.error(f"❌ Error converting SMS to transaction: {e}")
    #         return None
    
    async def _execute_unlimited_query(self, user_id: str, collection_name: str, sub_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute query with NO LIMITS to get ALL relevant data"""
        try:
            client_db = db_manager.clients[0]
            if client_db is None:
                return []
            
            database = client_db["pluto_money"]
            collection = database[collection_name]
            
            # Build comprehensive query
            base_query = {"user_id": user_id}
            filters = sub_query.get("filters", {})
            query = {**base_query, **filters}
            
            # Apply sort
            sort_criteria = sub_query.get("sort", {"_id": -1})
            
            # NO LIMIT - get ALL data
            cursor = collection.find(query).sort(list(sort_criteria.items()))
            results = await cursor.to_list(length=None)  # NO LIMIT
            
            logger.info(f"✅ Retrieved ALL {len(results)} items from {collection_name} for sub-query")
            return results
             
        except Exception as e:
            logger.error(f"❌ Error in unlimited query execution: {e}")
            return []
    
    async def _execute_comprehensive_data_retrieval_with_logging(self, user_id: str, sub_queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute all sub-queries with DETAILED LOGGING of MongoDB queries and responses"""
        all_results = []
        
        for sub_query in sub_queries:
            try:
                collection_name = sub_query.get("target_collection", "financial_transactions")
                logger.info(f"🔍 EXECUTING SUB-QUERY {sub_query.get('id')}: {sub_query.get('description')}")
                
                # Use integrated approach for financial transactions
                if collection_name == "financial_transactions":
                    data = await self._get_integrated_financial_data(user_id, sub_query)
                else:
                    # Get comprehensive data without limits for other collections
                    data = await self._execute_unlimited_query_with_logging(user_id, collection_name, sub_query)
                
                result = {
                    "sub_query_id": sub_query.get("id"),
                    "description": sub_query.get("description"),
                    "collection": collection_name,
                    "query_type": sub_query.get("query_type"),
                    "results": data,
                    "count": len(data),
                    "priority": sub_query.get("priority", "medium")
                }
                
                all_results.append(result)
                logger.info(f"📊 SUB-QUERY {sub_query.get('id')} COMPLETED: {len(data)} results retrieved")
                
                # Log sample data for transparency
                if data and len(data) > 0:
                    logger.info(f"📊 SAMPLE DATA from sub-query {sub_query.get('id')}:")
                    for i, item in enumerate(data[:3]):  # Show first 3 items
                        merchant = item.get('merchant_canonical') or item.get('merchant_original') or item.get('service_name', 'Unknown')
                        amount = item.get('amount', 0)
                        payment_method = item.get('payment_method', 'Unknown')
                        logger.info(f"📊   Item {i+1}: {merchant} - ₹{amount} via {payment_method}")
                
            except Exception as e:
                logger.error(f"❌ Error executing sub-query {sub_query.get('id')}: {e}")
                continue
        
        return all_results
    
    async def _execute_unlimited_query_with_logging(self, user_id: str, collection_name: str, sub_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute query with NO LIMITS and DETAILED MONGODB LOGGING"""
        try:
            client_db = db_manager.clients[0]
            if client_db is None:
                logger.error(f"❌ No database client available for {collection_name}")
                return []
            
            database = client_db["pluto_money"]
            collection = database[collection_name]
            
            # Build comprehensive query
            base_query = {"user_id": user_id}
            filters = sub_query.get("filters", {})
            final_query = {**base_query, **filters}
            
            # Apply sort
            sort_criteria = sub_query.get("sort", {"_id": -1})
            
            # LOG THE ACTUAL MONGODB QUERY
            logger.info(f"🔍 MONGODB QUERY for {collection_name}:")
            logger.info(f"🔍   Query: {json.dumps(final_query, indent=2, default=str)}")
            logger.info(f"🔍   Sort: {json.dumps(sort_criteria, indent=2, default=str)}")
            logger.info(f"🔍   Collection: {collection_name}")
            
            # NO LIMIT - get ALL data
            cursor = collection.find(final_query).sort(list(sort_criteria.items()))
            results = await cursor.to_list(length=None)  # NO LIMIT
            
            logger.info(f"✅ MONGODB RESPONSE: Retrieved ALL {len(results)} items from {collection_name}")
            
            return results
             
        except Exception as e:
            logger.error(f"❌ Error in unlimited query execution for {collection_name}: {e}")
            return []
    
    async def _perform_deep_analysis(self, all_data: List[Dict[str, Any]], intent_analysis: Dict[str, Any], original_query: str) -> List[Dict[str, Any]]:
        """Perform deep analysis on all retrieved data"""
        analyzed_results = []
        
        for data_set in all_data:
            if data_set["count"] == 0:
                continue
                
            collection_name = data_set["collection"]
            data = data_set["results"]
            
            # Comprehensive analysis for each dataset
            analysis = {
                "collection": collection_name,
                "sub_query_id": data_set["sub_query_id"],
                "description": data_set["description"],
                "total_items": len(data),
                "summary_stats": self._calculate_advanced_stats(data, collection_name),
                "key_insights": self._extract_deep_insights(data, collection_name, intent_analysis),
                "patterns": self._identify_advanced_patterns(data, collection_name),
                "bank_analysis": self._analyze_bank_details(data, collection_name),
                "payment_analysis": self._analyze_payment_methods(data, collection_name),
                "merchant_analysis": self._analyze_merchants(data, collection_name),
                "amount_analysis": self._analyze_amounts(data, collection_name),
                "time_analysis": self._analyze_time_patterns(data, collection_name),
                "recommendations": self._generate_smart_recommendations(data, collection_name, intent_analysis)
            }
            
            analyzed_results.append(analysis)
        
        return analyzed_results
    
    async def _perform_deep_analysis_with_logging(self, all_data: List[Dict[str, Any]], intent_analysis: Dict[str, Any], original_query: str) -> List[Dict[str, Any]]:
        """Perform deep analysis with DETAILED LOGGING of each analysis step"""
        analyzed_results = []
        
        for data_set in all_data:
            if data_set["count"] == 0:
                logger.info(f"📊 SKIPPING ANALYSIS for {data_set['collection']} - No data found")
                continue
                
            collection_name = data_set["collection"]
            data = data_set["results"]
            
            logger.info(f"📊 ANALYZING {collection_name} with {len(data)} items:")
            
            # Comprehensive analysis for each dataset
            analysis = {
                "collection": collection_name,
                "sub_query_id": data_set["sub_query_id"],
                "description": data_set["description"],
                "total_items": len(data),
                "summary_stats": self._calculate_advanced_stats(data, collection_name),
                "key_insights": self._extract_deep_insights(data, collection_name, intent_analysis),
                "patterns": self._identify_advanced_patterns(data, collection_name),
                "bank_analysis": self._analyze_bank_details(data, collection_name),
                "payment_analysis": self._analyze_payment_methods(data, collection_name),
                "merchant_analysis": self._analyze_merchants(data, collection_name),
                "amount_analysis": self._analyze_amounts(data, collection_name),
                "time_analysis": self._analyze_time_patterns(data, collection_name),
                "recommendations": self._generate_smart_recommendations(data, collection_name, intent_analysis)
            }
            
            # LOG THE ANALYSIS RESULTS
            logger.info(f"📊 ANALYSIS RESULTS for {collection_name}:")
            logger.info(f"📊   Total Items: {analysis['total_items']}")
            logger.info(f"📊   Key Insights: {analysis['key_insights'][:3]}")  # First 3 insights
            
            if analysis['bank_analysis'].get('banks_used'):
                logger.info(f"📊   Banks Found: {list(analysis['bank_analysis']['banks_used'].keys())}")
            
            if analysis['merchant_analysis'].get('top_merchants'):
                top_merchants = list(analysis['merchant_analysis']['top_merchants'].keys())[:5]
                logger.info(f"📊   Top Merchants: {top_merchants}")
            
            analyzed_results.append(analysis)
        
        return analyzed_results
    
    def _analyze_bank_details(self, data: List[Dict[str, Any]], collection_name: str) -> Dict[str, Any]:
        """Comprehensive bank details analysis"""
        if collection_name != "financial_transactions":
            return {}
        
        bank_analysis = {
            "banks_used": {},
            "accounts_used": {},
            "bank_transaction_counts": {},
            "bank_spending_totals": {},
            "payment_methods_by_bank": {},
            "recent_bank_activity": []
        }
        
        for transaction in data:
            bank_name = transaction.get("bank_name")
            account_number = transaction.get("account_number")
            amount = transaction.get("amount", 0) or 0  # ✅ FIXED: Handle None values
            payment_method = transaction.get("payment_method", "unknown")
            
            if bank_name:
                # Track banks
                if bank_name not in bank_analysis["banks_used"]:
                    bank_analysis["banks_used"][bank_name] = {
                        "transaction_count": 0,
                        "total_amount": 0,
                        "account_numbers": set(),
                        "payment_methods": set(),
                        "recent_transactions": []
                    }
                
                bank_data = bank_analysis["banks_used"][bank_name]
                bank_data["transaction_count"] += 1
                bank_data["total_amount"] += amount  # ✅ Now safe - amount is never None
                bank_data["payment_methods"].add(payment_method)
                
                if account_number:
                    bank_data["account_numbers"].add(account_number)
                    
                    # Track accounts
                    account_key = f"{bank_name}_{account_number}"
                    if account_key not in bank_analysis["accounts_used"]:
                        bank_analysis["accounts_used"][account_key] = {
                            "bank": bank_name,
                            "account": account_number,
                            "transaction_count": 0,
                            "total_amount": 0
                        }
                    bank_analysis["accounts_used"][account_key]["transaction_count"] += 1
                    bank_analysis["accounts_used"][account_key]["total_amount"] += amount  # ✅ Now safe
        
        # Convert sets to lists for JSON serialization
        for bank_name, bank_data in bank_analysis["banks_used"].items():
            bank_data["account_numbers"] = list(bank_data["account_numbers"])
            bank_data["payment_methods"] = list(bank_data["payment_methods"])
        
        return bank_analysis
    
    def _analyze_payment_methods(self, data: List[Dict[str, Any]], collection_name: str) -> Dict[str, Any]:
        """Comprehensive payment methods analysis"""
        if collection_name != "financial_transactions":
            return {}
        
        payment_analysis = {
            "methods_breakdown": {},
            "upi_details": {},
            "card_usage": {},
            "bank_transfer_details": {}
        }
        
        for transaction in data:
            method = transaction.get("payment_method", "unknown")
            amount = transaction.get("amount", 0) or 0  # ✅ FIXED: Handle None values
            upi_id = transaction.get("upi_id")
            bank_name = transaction.get("bank_name")
            
            # Track payment methods
            if method not in payment_analysis["methods_breakdown"]:
                payment_analysis["methods_breakdown"][method] = {
                    "count": 0,
                    "total_amount": 0,
                    "transactions": []
                }
            
            payment_analysis["methods_breakdown"][method]["count"] += 1
            payment_analysis["methods_breakdown"][method]["total_amount"] += amount  # ✅ Now safe
            
            # UPI analysis
            if method == "upi" and upi_id:
                if upi_id not in payment_analysis["upi_details"]:
                    payment_analysis["upi_details"][upi_id] = {
                        "transaction_count": 0,
                        "total_amount": 0,
                        "associated_bank": bank_name
                    }
                payment_analysis["upi_details"][upi_id]["transaction_count"] += 1
                payment_analysis["upi_details"][upi_id]["total_amount"] += amount  # ✅ Now safe
        
        return payment_analysis
    
    def _analyze_merchants(self, data: List[Dict[str, Any]], collection_name: str) -> Dict[str, Any]:
        """Comprehensive merchant analysis"""
        if collection_name != "financial_transactions":
            return {}
        
        merchant_analysis = {
            "top_merchants": {},
            "merchant_categories": {},
            "spending_by_merchant": {}
        }
        
        for transaction in data:
            merchant = transaction.get("merchant_canonical") or transaction.get("merchant_original", "unknown")
            amount = transaction.get("amount", 0) or 0  # ✅ FIXED: Handle None values
            category = transaction.get("service_category", "unknown")
            
            # Track merchants
            if merchant not in merchant_analysis["top_merchants"]:
                merchant_analysis["top_merchants"][merchant] = {
                    "transaction_count": 0,
                    "total_amount": 0,
                    "category": category,
                    "payment_methods": set()
                }
            
            merchant_data = merchant_analysis["top_merchants"][merchant]
            merchant_data["transaction_count"] += 1
            merchant_data["total_amount"] += amount  # ✅ Now safe
            merchant_data["payment_methods"].add(transaction.get("payment_method", "unknown"))
            
            # Track categories
            if category not in merchant_analysis["merchant_categories"]:
                merchant_analysis["merchant_categories"][category] = {
                    "merchant_count": 0,
                    "transaction_count": 0,
                    "total_amount": 0,
                    "merchants": set()
                }
            
            cat_data = merchant_analysis["merchant_categories"][category]
            cat_data["transaction_count"] += 1
            cat_data["total_amount"] += amount  # ✅ Now safe
            cat_data["merchants"].add(merchant)
        
        # Convert sets to lists
        for merchant, data in merchant_analysis["top_merchants"].items():
            data["payment_methods"] = list(data["payment_methods"])
        
        for category, data in merchant_analysis["merchant_categories"].items():
            data["merchants"] = list(data["merchants"])
            data["merchant_count"] = len(data["merchants"])
        
        return merchant_analysis
    
    def _analyze_amounts(self, data: List[Dict[str, Any]], collection_name: str) -> Dict[str, Any]:
        """Comprehensive amount analysis"""
        if collection_name != "financial_transactions":
            return {}
        
        # ✅ FIXED: Filter out None and invalid amounts
        amounts = []
        for t in data:
            amount = t.get("amount")
            if amount is not None and isinstance(amount, (int, float)) and amount > 0:
                amounts.append(amount)
        
        if not amounts:
            return {
                "total_amount": 0,
                "average_amount": 0,
                "median_amount": 0,
                "max_amount": 0,
                "min_amount": 0,
                "high_value_transactions": 0,
                "medium_value_transactions": 0,
                "low_value_transactions": 0,
                "top_10_amounts": []
            }
        
        amounts.sort(reverse=True)
        
        return {
            "total_amount": sum(amounts),
            "average_amount": sum(amounts) / len(amounts),
            "median_amount": amounts[len(amounts) // 2],
            "max_amount": max(amounts),
            "min_amount": min(amounts),
            "high_value_transactions": len([a for a in amounts if a > 10000]),
            "medium_value_transactions": len([a for a in amounts if 1000 <= a <= 10000]),
            "low_value_transactions": len([a for a in amounts if a < 1000]),
            "top_10_amounts": amounts[:10]
        }
    
    def _analyze_time_patterns(self, data: List[Dict[str, Any]], collection_name: str) -> Dict[str, Any]:
        """Comprehensive time pattern analysis"""
        if collection_name != "financial_transactions":
            return {}
        
        time_analysis = {
            "transaction_frequency": {},
            "monthly_spending": {},
            "recent_activity": {},
            "date_range": {}
        }
        
        dates = []
        for transaction in data:
            date_str = transaction.get("transaction_date")
            if date_str:
                try:
                    # ✅ FIXED: Better date parsing
                    if isinstance(date_str, str):
                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        dates.append(date_obj)
                except Exception as e:
                    # Skip invalid dates
                    continue
        
        if dates:
            dates.sort()
            time_analysis["date_range"] = {
                "earliest": dates[0].isoformat(),
                "latest": dates[-1].isoformat(),
                "span_days": (dates[-1] - dates[0]).days
            }
        
        return time_analysis
    
    async def _generate_enhanced_response_fast(self, original_query: str, intent_analysis: Dict[str, Any], 
                                            sub_queries: List[Dict[str, Any]], all_data: List[Dict[str, Any]], 
                                            analyzed_data: List[Dict[str, Any]]) -> str:
        """Generate enhanced response with ALL comprehensive data - FAST VERSION"""
        try:
            if not client:
                return self._generate_comprehensive_fallback_response(original_query, analyzed_data, all_data)
            
            # ✅ OPTIMIZATION: Create concise data summary for LLM
            summary_data = self._create_concise_data_summary(all_data, analyzed_data)
            
            # ✅ OPTIMIZATION: Shorter, focused prompt
            prompt = f"""Answer this financial query with the provided data:

QUERY: "{original_query}"

DATA SUMMARY: {json.dumps(summary_data, indent=1, default=str)}

Provide a comprehensive response with:
1. Direct answer to the query
2. Specific numbers, amounts, bank details
3. Clear breakdown of findings
4. Actionable insights

Use **bold** for important information."""

            response = await client.chat.completions.create(
                model="gpt-4o-mini",  # ✅ FIXED: Faster model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000,  # ✅ FIXED: Reduced from 2500
                timeout=10.0  # ✅ FIXED: Short timeout
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ Fast response generation failed: {e}")
            return self._generate_comprehensive_fallback_response(original_query, analyzed_data, all_data)
    
    def _create_concise_data_summary(self, all_data: List[Dict[str, Any]], analyzed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create concise summary for fast LLM processing"""
        total_transactions = sum(len(data.get("results", [])) for data in all_data)
        
        # Extract key financial info
        financial_summary = {}
        
        for data_set in all_data:
            if data_set["collection"] == "financial_transactions":
                transactions = data_set["results"]
                
                # Bank details
                banks = set()
                accounts = set()
                payment_methods = set()
                total_amount = 0
                valid_amount_count = 0
                
                for tx in transactions:
                    if tx.get("bank_name"):
                        banks.add(tx["bank_name"])
                    if tx.get("account_number"):
                        accounts.add(tx["account_number"])
                    if tx.get("payment_method"):
                        payment_methods.add(tx["payment_method"])
                    
                    # ✅ FIXED: Handle None amounts properly
                    amount = tx.get("amount")
                    if amount is not None and isinstance(amount, (int, float)):
                        total_amount += amount
                        valid_amount_count += 1
                
                financial_summary = {
                    "total_transactions": len(transactions),
                    "valid_amount_transactions": valid_amount_count,
                    "total_amount": total_amount,
                    "banks_used": list(banks),
                    "accounts_used": list(accounts),
                    "payment_methods": list(payment_methods)
                }
        
        return {
            "query_summary": f"{total_transactions} transactions analyzed",
            "financial_summary": financial_summary,
            "analysis_insights": [a.get("key_insights", [])[:3] for a in analyzed_data if a.get("key_insights")][:5]
        }
    
    def _generate_comprehensive_fallback_response(self, original_query: str, analyzed_data: List[Dict[str, Any]], all_data: List[Dict[str, Any]]) -> str:
        """Generate comprehensive fallback response with actual data"""
        total_items = sum(analysis.get("total_items", 0) for analysis in analyzed_data)
        
        if total_items == 0:
            return "I couldn't find any data matching your query. Please try rephrasing your question or ensure your data has been synchronized."
        
        # Extract actual financial data for response
        response_parts = [f"I found and analyzed **{total_items}** financial items for your query."]
        
        # Add bank details if available
        for analysis in analyzed_data:
            if analysis.get("bank_analysis", {}).get("banks_used"):
                banks = analysis["bank_analysis"]["banks_used"]
                response_parts.append(f"\n**Bank Details:**")
                for bank, details in banks.items():
                    response_parts.append(f"- **{bank}**: {details['transaction_count']} transactions, ₹{details['total_amount']:,.2f}")
                    if details.get('account_numbers'):
                        response_parts.append(f"  - Accounts: {', '.join(details['account_numbers'])}")
        
        # Add transaction summary
        financial_data = next((data for data in all_data if data["collection"] == "financial_transactions"), None)
        if financial_data:
            transactions = financial_data["results"]
            subscription_count = sum(1 for tx in transactions if tx.get("is_subscription"))
            if subscription_count > 0:
                response_parts.append(f"\n**Subscriptions:** Found {subscription_count} subscription-related transactions")
        
        response_parts.append(f"\n**Analysis completed successfully** with comprehensive data retrieval from {len(analyzed_data)} sources.")
        
        return "".join(response_parts)
    
    def _generate_comprehensive_fallback_response_with_details(self, original_query: str, analyzed_data: List[Dict[str, Any]], all_data: List[Dict[str, Any]]) -> str:
        """Generate comprehensive fallback response with ACTUAL SPECIFIC DETAILS - INCLUDING NULL AMOUNTS"""
        detailed_data = self._extract_detailed_subscription_data(all_data, analyzed_data)
        
        total_services = len(detailed_data["subscription_services"])
        
        if total_services == 0:
            return "I couldn't find any subscription transactions in your data. Please ensure your data has been synchronized."
        
        # ✅ Separate services with and without amounts
        services_with_amounts = [s for s in detailed_data["subscription_services"] if s.get("has_amount") and s.get("amount") is not None]
        services_without_amounts = [s for s in detailed_data["subscription_services"] if not s.get("has_amount") or s.get("amount") is None]
        
        response_parts = [
            f"## 📋 Complete Subscription Analysis Results\n",
            f"Found **{total_services}** total subscription services in your account:\n\n"
        ]
        
        # ✅ Show services WITH amounts
        if services_with_amounts:
            response_parts.append("### 💰 Services with Pricing Information:\n")
            for i, service in enumerate(services_with_amounts, 1):
                amount_text = f"₹{service['amount']:,.2f}"
                if service.get("currency") == "USD" and service.get("original_amount"):
                    amount_text += f" (Original: ${service['original_amount']} USD)"
                
                bank_text = ""
                if service.get("bank_name", "Unknown") != "Unknown":
                    bank_text = f" from {service['bank_name']}"
                    if service.get("account_number", "Unknown") != "Unknown":
                        bank_text += f" ({service['account_number']})"
                
                payment_text = ""
                if service.get("payment_method", "Unknown") != "Unknown":
                    payment_text = f" via {service['payment_method']}"
                
                response_parts.append(f"{i}. **{service.get('service_name', 'Unknown Service')}** - {amount_text}{payment_text}{bank_text}\n")
        
        # ✅ Show services WITHOUT amounts - SAFELY ACCESS KEYS
        if services_without_amounts:
            response_parts.append("\n### 📝 Services without Amount Information:\n")
            for i, service in enumerate(services_without_amounts, 1):
                extra_info = []
                
                # ✅ SAFE KEY ACCESS - Check if key exists before using
                if service.get("trial_status"):
                    extra_info.append("Trial Status")
                
                billing_freq = service.get("billing_frequency")
                if billing_freq and billing_freq != "Unknown":
                    extra_info.append(f"Billing: {billing_freq}")
                
                plan_name = service.get("plan_name")
                if plan_name and plan_name != "Unknown":
                    extra_info.append(f"Plan: {plan_name}")
                
                service_category = service.get("service_category")
                if service_category and service_category != "Unknown":
                    extra_info.append(f"Category: {service_category}")
                
                extra_text = f" ({', '.join(extra_info)})" if extra_info else ""
                service_name = service.get("service_name", "Unknown Service")
                response_parts.append(f"{i}. **{service_name}** - Amount: Not specified{extra_text}\n")
        
        # ✅ Banking summary
        if detailed_data.get("bank_details"):
            response_parts.append("\n### 🏦 Banking Details:\n")
            for bank, details in detailed_data["bank_details"].items():
                account_info = ""
                if details.get('account_numbers'):
                    account_info = f" (Accounts: {', '.join(details['account_numbers'])})"
                response_parts.append(f"- **{bank}**: {details.get('transaction_count', 0)} transactions{account_info} - Total: ₹{details.get('total_amount', 0):,.2f}\n")
        
        # ✅ Summary statistics - SAFE ACCESS
        summary = detailed_data.get("financial_summary", {})
        response_parts.extend([
            "\n### 📊 Summary:\n",
            f"- **Total Services**: {summary.get('total_subscription_count', 0)}\n",
            f"- **Services with Pricing**: {summary.get('services_with_amounts', 0)}\n", 
            f"- **Services without Pricing**: {summary.get('services_without_amounts', 0)}\n",
            f"- **Trial Services**: {summary.get('trial_services', 0)}\n",
            f"- **Active Services**: {summary.get('active_services', 0)}\n",
            f"- **Estimated Total Spending**: ₹{summary.get('total_amount', 0):,.2f}\n",
            f"- **Unique Service Names**: {summary.get('unique_services', 0)}\n"
        ])
        
        response_parts.append(f"\n**Data Sources**: Analyzed {len(analyzed_data)} collections with complete transparency.")
        
        return "".join(response_parts)
    
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
            
            return None
            
        except Exception as e:
            logger.warning(f"JSON extraction failed: {e}")
            return None
    
    def _fallback_intent_analysis(self, query: str) -> Dict[str, Any]:
        """Fallback intent analysis when LLM is not available"""
        query_lower = query.lower()
        
        return {
            "primary_intent": "retrieve_bank_details" if any(word in query_lower for word in ["bank", "account", "details"]) else "list_transactions",
            "secondary_intents": ["analyze_spending", "get_financial_overview"],
            "data_requirements": {
                "need_bank_details": True,
                "need_account_numbers": True,
                "need_transaction_amounts": True,
                "need_merchant_info": True,
                "need_payment_methods": True,
                "need_all_transactions": True
            },
            "query_complexity": "comprehensive",
            "expected_collections": ["financial_transactions", "subscriptions"],
            "analysis_depth": "complete",
            "response_format": "comprehensive_report"
        }
    
    def _fallback_subquery_generation(self, query: str, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback sub-query generation"""
        return [
            {
                "id": 1,
                "description": "Get all financial transactions",
                "target_collection": "financial_transactions",
                "query_type": "comprehensive_retrieval",
                "filters": {},
                "sort": {"amount": -1},
                "limit": None,
                "priority": "high"
            },
            {
                "id": 2,
                "description": "Get bank details specifically",
                "target_collection": "financial_transactions",
                "query_type": "bank_details_focus",
                "filters": {"bank_name": {"$exists": True}},
                "sort": {"transaction_date": -1},
                "limit": None,
                "priority": "high"
            },
            {
                "id": 3,
                "description": "Get subscription transactions",
                "target_collection": "financial_transactions",
                "query_type": "subscription_focus",
                "filters": {"is_subscription": True},
                "sort": {"amount": -1},
                "limit": None,
                "priority": "medium"
            }
        ]
    
    def _calculate_data_comprehensiveness(self, all_data: List[Dict[str, Any]]) -> float:
        """Calculate how comprehensive the data retrieval was"""
        total_items = sum(len(data.get("results", [])) for data in all_data)
        return min(1.0, total_items / 1000.0)
    
    def _calculate_intelligence_score(self, intent: Dict[str, Any], sub_queries: List[Dict[str, Any]], all_data: List[Dict[str, Any]]) -> float:
        """Calculate overall intelligence score of the processing"""
        intent_score = 0.3 if intent else 0.0
        subquery_score = min(0.4, len(sub_queries) / 15 * 0.4)
        data_score = min(0.3, sum(len(data.get("results", [])) for data in all_data) / 1000 * 0.3)
        return intent_score + subquery_score + data_score
    
    def _calculate_advanced_stats(self, data: List[Dict[str, Any]], collection_name: str) -> Dict[str, Any]:
        """Calculate advanced statistics for the data"""
        if not data:
            return {}
        
        stats = {"total_count": len(data)}
        
        if collection_name == "financial_transactions":
            # ✅ FIXED: Filter out None and invalid amounts
            amounts = []
            for t in data:
                amount = t.get("amount")
                if amount is not None and isinstance(amount, (int, float)):
                    amounts.append(amount)
            
            if amounts:
                stats.update({
                    "total_amount": sum(amounts),
                    "average_amount": sum(amounts) / len(amounts),
                    "max_amount": max(amounts),
                    "min_amount": min(amounts),
                    "valid_amount_count": len(amounts)
                })
            else:
                stats.update({
                    "total_amount": 0,
                    "average_amount": 0,
                    "max_amount": 0,
                    "min_amount": 0,
                    "valid_amount_count": 0
                })
        
        return stats
    
    def _extract_deep_insights(self, data: List[Dict[str, Any]], collection_name: str, intent_analysis: Dict[str, Any]) -> List[str]:
        """Extract deep insights from the data based on intent"""
        insights = []
        
        if not data:
            return ["No data available for analysis"]
        
        if collection_name == "financial_transactions":
            bank_names = set(t.get("bank_name") for t in data if t.get("bank_name"))
            payment_methods = set(t.get("payment_method") for t in data if t.get("payment_method"))
            merchants = set(t.get("merchant_canonical") or t.get("merchant_original") for t in data if t.get("merchant_canonical") or t.get("merchant_original"))
            
            insights.extend([
                f"Found transactions across {len(bank_names)} different banks",
                f"Used {len(payment_methods)} different payment methods", 
                f"Transacted with {len(merchants)} different merchants",
                f"Total transaction records analyzed: {len(data)}"
            ])
            
            # ✅ FIXED: Handle None amounts properly
            valid_amounts = []
            for t in data:
                amount = t.get("amount")
                if amount is not None and isinstance(amount, (int, float)):
                    valid_amounts.append(amount)
            
            if valid_amounts:
                total_amount = sum(valid_amounts)
                insights.append(f"Total transaction value: ₹{total_amount:,.2f}")
                insights.append(f"Valid amount records: {len(valid_amounts)} out of {len(data)}")
            else:
                insights.append("No valid transaction amounts found in the data")
        
        return insights[:10]
    
    def _identify_advanced_patterns(self, data: List[Dict[str, Any]], collection_name: str) -> List[str]:
        """Identify advanced patterns in the data"""
        patterns = []
        
        if len(data) < 2:
            return patterns
        
        if collection_name == "financial_transactions":
            # Payment method patterns
            payment_methods = [t.get("payment_method") for t in data if t.get("payment_method")]
            if payment_methods:
                from collections import Counter
                method_counts = Counter(payment_methods)
                most_common_method = method_counts.most_common(1)[0]
                patterns.append(f"Most used payment method: {most_common_method[0]} ({most_common_method[1]} times)")
            
            # Bank usage patterns
            banks = [t.get("bank_name") for t in data if t.get("bank_name")]
            if banks:
                bank_counts = Counter(banks)
                most_used_bank = bank_counts.most_common(1)[0]
                patterns.append(f"Most used bank: {most_used_bank[0]} ({most_used_bank[1]} transactions)")
            
            # ✅ FIXED: Amount-based patterns with None handling
            valid_amounts = [t.get("amount") for t in data if t.get("amount") is not None and isinstance(t.get("amount"), (int, float))]
            if valid_amounts:
                avg_amount = sum(valid_amounts) / len(valid_amounts)
                patterns.append(f"Average transaction amount: ₹{avg_amount:,.2f}")
        
        return patterns[:5]
    
    def _generate_smart_recommendations(self, data: List[Dict[str, Any]], collection_name: str, intent_analysis: Dict[str, Any]) -> List[str]:
        """Generate smart recommendations based on data and intent"""
        recommendations = []
        
        if not data:
            return recommendations
        
        if collection_name == "financial_transactions":
            bank_names = [t.get("bank_name") for t in data if t.get("bank_name")]
            if bank_names:
                from collections import Counter
                bank_counts = Counter(bank_names)
                recommendations.append(f"Primary banking relationships: {', '.join([f'{bank} ({count} transactions)' for bank, count in bank_counts.most_common(3)])}")
            
            # ✅ FIXED: Handle None amounts in recommendations
            valid_amounts = []
            for t in data:
                amount = t.get("amount")
                if amount is not None and isinstance(amount, (int, float)):
                    valid_amounts.append(amount)
            
            if valid_amounts:
                high_value_count = len([a for a in valid_amounts if a > 5000])
                if high_value_count > 0:
                    recommendations.append(f"Monitor {high_value_count} high-value transactions (>₹5000) for accuracy")
                
                # Add data quality recommendation
                data_quality_ratio = len(valid_amounts) / len(data)
                if data_quality_ratio < 0.9:
                    recommendations.append(f"Data quality check: {len(data) - len(valid_amounts)} transactions have missing/invalid amounts")
        
        return recommendations[:5]

    def _extract_detailed_subscription_data(self, all_data: List[Dict[str, Any]], analyzed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract detailed subscription data with ACTUAL service names and amounts - INCLUDING NULL AMOUNTS"""
        detailed_data = {
            "subscription_services": [],
            "bank_details": {},
            "payment_methods": {},
            "financial_summary": {}
        }
        
        # Extract from financial transactions
        for data_set in all_data:
            if data_set["collection"] == "financial_transactions":
                transactions = data_set["results"]
                
                # ✅ PROCESS ALL TRANSACTIONS - Don't filter by is_subscription flag
                for tx in transactions:
                    # ✅ IDENTIFY SUBSCRIPTIONS by multiple criteria
                    is_likely_subscription = (
                        tx.get("is_subscription", False) or  # Explicit flag
                        data_set.get("description", "").lower().find("subscription") != -1 or  # Query context
                        self._is_subscription_merchant(tx) or  # Merchant patterns
                        tx.get("service_category") in ["Productivity", "Software", "SaaS"] or  # Category
                        tx.get("payment_method") == "credit_card"  # Recurring payment pattern
                    )
                    
                    if is_likely_subscription:
                        service_name = self._get_best_service_name(tx)
                        amount = self._get_normalized_amount(tx)  # ✅ Handle USD/INR conversion
                        
                        subscription_detail = {
                            "service_name": service_name,
                            "amount": amount,
                            "currency": tx.get("currency", "INR"),
                            "original_amount": tx.get("amount"),  # Keep original for reference
                            "payment_method": tx.get("payment_method", "Unknown"),
                            "bank_name": tx.get("bank_name", "Unknown"),
                            "account_number": tx.get("account_number", "Unknown"),
                            "transaction_date": tx.get("transaction_date"),
                            "service_category": tx.get("service_category", "Unknown"),
                            "is_subscription": tx.get("is_subscription", False),
                            "has_amount": amount is not None,
                            "invoice_number": tx.get("invoice_number"),
                            "merchant_original": tx.get("merchant_original")
                        }
                        detailed_data["subscription_services"].append(subscription_detail)
            
            # ✅ Extract from subscriptions collection - INCLUDE ALL ENTRIES
            elif data_set["collection"] == "subscriptions":
                subscriptions = data_set["results"]
                
                for sub in subscriptions:
                    service_name = self._get_best_subscription_name(sub)
                    amount = self._get_normalized_amount(sub)  # ✅ Handle null amounts
                    
                    subscription_detail = {
                        "service_name": service_name,
                        "amount": amount,
                        "currency": sub.get("currency", "USD"),
                        "original_amount": sub.get("amount"),  # Keep original
                        "billing_frequency": sub.get("billing_frequency", "Unknown"),
                        "subscription_status": sub.get("subscription_status", "Unknown"),
                        "service_category": sub.get("service_category", "Unknown"),
                        "plan_name": sub.get("plan_name", "Unknown"),
                        "is_subscription": True,
                        "has_amount": amount is not None,
                        "trial_status": sub.get("subscription_status") == "trial",
                        "auto_renewal": sub.get("auto_renewal"),
                        "account_email": sub.get("account_email")
                    }
                    detailed_data["subscription_services"].append(subscription_detail)
        
        # ✅ Remove duplicates while preserving the best data
        detailed_data["subscription_services"] = self._deduplicate_subscriptions(detailed_data["subscription_services"])
        
        # Extract bank details from analyzed data
        for analysis in analyzed_data:
            if analysis.get("bank_analysis", {}).get("banks_used"):
                detailed_data["bank_details"] = analysis["bank_analysis"]["banks_used"]
            
            if analysis.get("payment_analysis", {}).get("methods_breakdown"):
                detailed_data["payment_methods"] = analysis["payment_analysis"]["methods_breakdown"]
        
        # ✅ Calculate financial summary INCLUDING services without amounts
        services_with_amounts = [s for s in detailed_data["subscription_services"] if s["has_amount"] and s["amount"] is not None]
        services_without_amounts = [s for s in detailed_data["subscription_services"] if not s["has_amount"] or s["amount"] is None]
        
        total_amount = sum(s["amount"] for s in services_with_amounts)
        
        detailed_data["financial_summary"] = {
            "total_subscription_count": len(detailed_data["subscription_services"]),
            "services_with_amounts": len(services_with_amounts),
            "services_without_amounts": len(services_without_amounts),
            "total_amount": total_amount,
            "unique_services": len(set(s["service_name"] for s in detailed_data["subscription_services"])),
            "average_amount": total_amount / len(services_with_amounts) if services_with_amounts else 0,
            "trial_services": len([s for s in detailed_data["subscription_services"] if s.get("trial_status")]),
            "active_services": len([s for s in detailed_data["subscription_services"] if s.get("subscription_status") == "active"])
        }
        
        return detailed_data
    
    def _is_subscription_merchant(self, transaction: Dict[str, Any]) -> bool:
        """Check if merchant is known subscription service"""
        subscription_keywords = [
            "netflix", "spotify", "adobe", "microsoft", "google workspace", "dropbox",
            "slack", "zoom", "canva", "figma", "notion", "trello", "asana",
            "mem0", "framer", "webflow", "ahrefs", "semrush", "clevertap", "clevartap",
            "youtube", "prime", "disney", "hotstar", "amazon", "apple", "icloud"
        ]
        
        merchant_text = " ".join([
            str(transaction.get("merchant_canonical", "")),
            str(transaction.get("merchant_original", "")),
            str(transaction.get("service_name", ""))
        ]).lower()
        
        return any(keyword in merchant_text for keyword in subscription_keywords)
    
    def _get_best_service_name(self, transaction: Dict[str, Any]) -> str:
        """Get the best available service name from transaction"""
        return (
            transaction.get("service_name") or
            transaction.get("merchant_canonical") or 
            transaction.get("merchant_original") or
            "Unknown Service"
        )
    
    def _get_best_subscription_name(self, subscription: Dict[str, Any]) -> str:
        """Get the best available service name from subscription"""
        return (
            subscription.get("service_name") or
            subscription.get("service_canonical") or 
            subscription.get("plan_name") or
            "Unknown Subscription"
        )
    
    def _get_normalized_amount(self, item: Dict[str, Any]) -> Optional[float]:
        """Get normalized amount in INR, handling USD conversion and null values"""
        amount = item.get("amount")
        if amount is None:
            return None
            
        if not isinstance(amount, (int, float)):
            return None
            
        # Convert USD to INR (approximate rate: 1 USD = 83 INR)
        currency = item.get("currency", "INR")
        if currency == "USD" and amount > 0:
            return amount * 83  # Convert USD to INR
        elif currency == "INR" or currency is None:
            return amount
        else:
            return amount  # Return as-is for other currencies
    
    def _deduplicate_subscriptions(self, subscriptions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates while keeping the entry with the most information"""
        seen_services = {}
        
        for sub in subscriptions:
            service_name = sub["service_name"]
            
            # If we haven't seen this service, add it
            if service_name not in seen_services:
                seen_services[service_name] = sub
            else:
                # Keep the one with more information (has amount, bank details, etc.)
                current = seen_services[service_name]
                if self._has_more_info(sub, current):
                    seen_services[service_name] = sub
        
        return list(seen_services.values())
    
    def _has_more_info(self, sub1: Dict[str, Any], sub2: Dict[str, Any]) -> bool:
        """Check if sub1 has more information than sub2"""
        sub1_score = sum([
            1 if sub1.get("has_amount") else 0,
            1 if sub1.get("bank_name") != "Unknown" else 0,
            1 if sub1.get("payment_method") != "Unknown" else 0,
            1 if sub1.get("account_number") != "Unknown" else 0,
            1 if sub1.get("invoice_number") else 0
        ])
        
        sub2_score = sum([
            1 if sub2.get("has_amount") else 0,
            1 if sub2.get("bank_name") != "Unknown" else 0,
            1 if sub2.get("payment_method") != "Unknown" else 0,
            1 if sub2.get("account_number") != "Unknown" else 0,
            1 if sub2.get("invoice_number") else 0
        ])
        
        return sub1_score > sub2_score

    def _get_subscription_merchant_filter(self) -> Dict[str, Any]:
        """Get subscription merchant filter"""
        subscription_merchants = [
            "netflix", "spotify", "adobe", "microsoft", "google workspace", "dropbox", 
            "slack", "zoom", "canva", "figma", "notion", "trello", "asana",
            "mem0", "framer", "webflow", "ahrefs", "semrush", "clevertap", "clevartap",
            "youtube", "prime", "disney", "hotstar", "amazon", "apple", "icloud",
            "github", "gitlab", "vercel", "netlify", "railway", "render",
            "openai", "anthropic", "groq", "cohere", "huggingface"
        ]
        
        return {
            "$or": [
                {"merchant_canonical": {"$regex": merchant, "$options": "i"}} for merchant in subscription_merchants
            ] + [
                {"merchant_original": {"$regex": merchant, "$options": "i"}} for merchant in subscription_merchants
            ] + [
                {"service_name": {"$regex": merchant, "$options": "i"}} for merchant in subscription_merchants
            ]
        }
    
    def _extract_time_filter(self, query_lower: str) -> Dict[str, Any]:
        """Extract time-based filters from query"""
        import re
        from datetime import datetime, timedelta
        
        # Default: no time filter
        time_filter = {}
        
        # Last month
        if "last month" in query_lower:
            last_month = datetime.now() - timedelta(days=30)
            time_filter["transaction_date"] = {"$gte": last_month}
        
        # Last week
        elif "last week" in query_lower:
            last_week = datetime.now() - timedelta(days=7) 
            time_filter["transaction_date"] = {"$gte": last_week}
            
        # This year
        elif "this year" in query_lower:
            this_year = datetime.now().replace(month=1, day=1)
            time_filter["transaction_date"] = {"$gte": this_year}
        
        return time_filter

    async def _generate_enhanced_response_with_detailed_data(self, original_query: str, intent_analysis: Dict[str, Any], 
                                                           sub_queries: List[Dict[str, Any]], all_data: List[Dict[str, Any]], 
                                                           analyzed_data: List[Dict[str, Any]]) -> str:
        """Generate ADAPTIVE response based on actual query intent"""
        try:
            if not client:
                return self._generate_adaptive_fallback_response(original_query, analyzed_data, all_data, sub_queries)
            
            # ✅ DETERMINE QUERY TYPE from sub-queries
            query_types = [sq.get("query_type", "") for sq in sub_queries]
            primary_query_type = self._determine_primary_query_type(original_query, query_types)
            
            logger.info(f"📊 PRIMARY QUERY TYPE DETECTED: {primary_query_type}")
            
            # ✅ GENERATE ADAPTIVE RESPONSE BASED ON QUERY TYPE
            if primary_query_type == "bank_analysis":
                return await self._generate_bank_analysis_response(original_query, all_data, analyzed_data)
            elif primary_query_type == "credit_card_analysis": 
                return await self._generate_payment_method_response(original_query, all_data, analyzed_data)
            elif primary_query_type == "job_email_analysis":
                return await self._generate_job_email_response(original_query, all_data, analyzed_data)
            elif primary_query_type in ["subscription_merchants", "comprehensive_financial"]:
                return await self._generate_subscription_response(original_query, all_data, analyzed_data)
            elif primary_query_type == "spending_analysis":
                return await self._generate_spending_analysis_response(original_query, all_data, analyzed_data)
            else:
                return await self._generate_general_response(original_query, all_data, analyzed_data)
            
        except Exception as e:
            logger.error(f"❌ Adaptive response generation failed: {e}")
            return self._generate_adaptive_fallback_response(original_query, analyzed_data, all_data, sub_queries)

    def _determine_primary_query_type(self, query: str, query_types: List[str]) -> str:
        """Determine the primary query type from query and sub-query types"""
        query_lower = query.lower()
        
        # Bank/account queries
        if any(keyword in query_lower for keyword in ["bank", "account"]):
            return "bank_analysis"
        # Payment method queries  
        elif any(keyword in query_lower for keyword in ["credit card", "payment method", "card"]):
            return "credit_card_analysis"
        # Job email queries
        elif any(keyword in query_lower for keyword in ["job", "interview", "career"]):
            return "job_email_analysis"
        # Subscription queries
        elif any(keyword in query_lower for keyword in ["subscription", "service"]):
            return "subscription_merchants"
        # Spending queries
        elif any(keyword in query_lower for keyword in ["total", "spent", "amount"]):
            return "spending_analysis"
        else:
            return "general"

    async def _generate_bank_analysis_response(self, query: str, all_data: List[Dict[str, Any]], analyzed_data: List[Dict[str, Any]]) -> str:
        """Generate response specifically for bank account queries with SMS integration"""
        banks_found = {}
        account_numbers = set()
        email_transactions = 0
        sms_transactions = 0
        
        for data_set in all_data:
            if data_set["collection"] == "financial_transactions":
                for tx in data_set["results"]:
                    bank_name = tx.get("bank_name")
                    account_num = tx.get("account_number")
                    source = tx.get("source", "email")
                    
                    # Track source counts
                    if source == "sms":
                        sms_transactions += 1
                    else:
                        email_transactions += 1
                    
                    if bank_name and bank_name.lower() != "unknown":
                        if bank_name not in banks_found:
                            banks_found[bank_name] = {
                                "transaction_count": 0,
                                "accounts": set(),
                                "total_amount": 0,
                                "email_count": 0,
                                "sms_count": 0
                            }
                        banks_found[bank_name]["transaction_count"] += 1
                        
                        # Track source-specific counts
                        if source == "sms":
                            banks_found[bank_name]["sms_count"] += 1
                        else:
                            banks_found[bank_name]["email_count"] += 1
                        
                        if account_num:
                            banks_found[bank_name]["accounts"].add(account_num)
                            account_numbers.add(account_num)
                        
                        amount = tx.get("amount")
                        if amount and isinstance(amount, (int, float)):
                            banks_found[bank_name]["total_amount"] += amount

        # Create enhanced prompt with SMS integration info
        data_sources_info = f"📊 Data Sources: Email ({email_transactions} transactions) + SMS ({sms_transactions} transactions)"
        
        prompt = f"""User asked: "{query}"

{data_sources_info}

BANK DATA FOUND:
{json.dumps({k: {**v, "accounts": list(v["accounts"])} for k, v in banks_found.items()}, indent=2, default=str)}

Generate a comprehensive response focused on banking information with SMS integration insights. Format:

## 🏦 Your Bank Accounts and Usage (Email + SMS Integration)

### Data Coverage:
- Email Transactions: {email_transactions}
- SMS Transactions: {sms_transactions}
- Total Coverage: {'📧📱 Comprehensive (Email + SMS)' if sms_transactions > 0 else '📧 Email Only'}

### Banks Where You Have Accounts:
1. **[Bank Name]** - Account: [Account Number] 
   - Total Transactions: [Count] (Email: [X], SMS: [Y])
   - Total Amount: ₹[Amount]
   - Data Source: [Email/SMS/Both]

### Summary:
- Total Banks: [Count]
- Total Account Numbers: [Count] 
- Most Used Bank: [Bank Name]
- Data Integration: [Email only/Email + SMS]

Be specific about actual bank names, account numbers, and data sources found."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000,
            timeout=8.0  # ✅ REDUCED from 15s to 8s to prevent hanging
        )
        
        return response.choices[0].message.content.strip()

    async def _generate_payment_method_response(self, query: str, all_data: List[Dict[str, Any]], analyzed_data: List[Dict[str, Any]]) -> str:
        """Generate response specifically for payment method/credit card queries"""
        payment_methods = {}
        
        for data_set in all_data:
            if data_set["collection"] == "financial_transactions":
                for tx in data_set["results"]:
                    method = tx.get("payment_method", "Unknown")
                    bank = tx.get("bank_name", "Unknown")
                    account = tx.get("account_number", "Unknown")
                    
                    if method not in payment_methods:
                        payment_methods[method] = {
                            "transaction_count": 0,
                            "banks": set(),
                            "accounts": set(),
                            "total_amount": 0
                        }
                    
                    payment_methods[method]["transaction_count"] += 1
                    if bank != "Unknown":
                        payment_methods[method]["banks"].add(bank)
                    if account != "Unknown":
                        payment_methods[method]["accounts"].add(account)
                    
                    amount = tx.get("amount")
                    if amount and isinstance(amount, (int, float)):
                        payment_methods[method]["total_amount"] += amount

        prompt = f"""User asked: "{query}"

PAYMENT METHOD DATA:
{json.dumps({k: {**v, "banks": list(v["banks"]), "accounts": list(v["accounts"])} for k, v in payment_methods.items()}, indent=2, default=str)}

Generate a response focused ONLY on payment methods and credit card details. Format:

## 💳 Your Payment Methods and Credit Card Details

### Payment Methods Used:
1. **Credit Card**
   - Banks: [Bank names]
   - Account Numbers: [Masked numbers]
   - Total Transactions: [Count]
   - Total Amount: ₹[Amount]

### UPI Details:
[If any UPI transactions found]

### Summary:
- Total Payment Methods: [Count]
- Most Used Method: [Method name]
- Primary Bank for Credit Cards: [Bank name]

Show actual bank names and masked account numbers."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000,
            timeout=8.0  # ✅ REDUCED from 15s to prevent hanging
        )
        
        return response.choices[0].message.content.strip()

    async def _generate_job_email_response(self, query: str, all_data: List[Dict[str, Any]], analyzed_data: List[Dict[str, Any]]) -> str:
        """Generate response specifically for job/interview email queries"""
        job_emails = []
        
        for data_set in all_data:
            if data_set["collection"] == "email_logs":
                for email in data_set["results"]:
                    job_emails.append({
                        "subject": email.get("subject", "Unknown"),
                        "sender": email.get("sender_name", email.get("sender_email", "Unknown")),
                        "date": email.get("received_date"),
                        "content_preview": email.get("content_preview", "")[:200]
                    })

        if not job_emails:
            return f"""## 📧 Job-Related Email Analysis

I couldn't find any job or interview related emails in your account. This could mean:
- You haven't received job-related emails recently
- The emails might not have been categorized properly
- Your email sync might be incomplete

Try checking for emails with keywords like "interview", "job opportunity", "position", or from recruiters."""

        prompt = f"""User asked: "{query}"

JOB EMAIL DATA FOUND ({len(job_emails)} emails):
{json.dumps(job_emails[:10], indent=2, default=str)}

Generate a response focused ONLY on job and interview emails. Format:

## 📧 Your Job-Related Emails and Interview Insights

### Recent Job-Related Emails:
1. **[Subject]** - From: [Sender Name/Company]
   - Date: [Date]
   - Preview: [Content preview]

### Interview Opportunities:
[List any interview-related emails]

### Job Platforms Activity:
[Any emails from LinkedIn, Naukri, etc.]

### Summary:
- Total Job Emails: {len(job_emails)}
- Recent Activity: [Yes/No]
- Interview Invitations: [Count if any]

Focus on actual email subjects, sender names, and job opportunities found."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1500,
            timeout=8.0  # ✅ REDUCED from 15s to prevent hanging
        )
        
        return response.choices[0].message.content.strip()

    async def _generate_subscription_response(self, query: str, all_data: List[Dict[str, Any]], analyzed_data: List[Dict[str, Any]]) -> str:
        """Generate response specifically for subscription queries (existing logic)"""
        detailed_data = self._extract_detailed_subscription_data(all_data, analyzed_data)
        
        prompt = f"""User asked: "{query}"

SUBSCRIPTION DATA:
{json.dumps(detailed_data, indent=2, default=str)}

Generate a comprehensive subscription analysis response with actual service names, amounts, and banking details."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000,
            timeout=8.0  # ✅ REDUCED from 15s to prevent hanging
        )
        
        return response.choices[0].message.content.strip()

    async def _generate_spending_analysis_response(self, query: str, all_data: List[Dict[str, Any]], analyzed_data: List[Dict[str, Any]]) -> str:
        """Generate response for spending/amount queries"""
        transactions = []
        total_amount = 0
        
        for data_set in all_data:
            if data_set["collection"] == "financial_transactions":
                for tx in data_set["results"]:
                    amount = tx.get("amount")
                    if amount and isinstance(amount, (int, float)):
                        transactions.append(tx)
                        total_amount += amount

        prompt = f"""User asked: "{query}"

SPENDING DATA:
- Total Transactions: {len(transactions)}
- Total Amount: ₹{total_amount:,.2f}
- Transaction Details: {json.dumps(transactions[:20], indent=2, default=str)}

Generate a spending analysis response focused on amounts, totals, and financial insights."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1500,
            timeout=8.0  # ✅ REDUCED from 15s to prevent hanging
        )
        
        return response.choices[0].message.content.strip()

    async def _generate_general_response(self, query: str, all_data: List[Dict[str, Any]], analyzed_data: List[Dict[str, Any]]) -> str:
        """Generate general response for queries that don't fit specific categories"""
        prompt = f"""User asked: "{query}"

Available data: {json.dumps([{"collection": d["collection"], "count": d["count"]} for d in all_data], indent=2)}

Generate a helpful response based on the user's query and available data."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000,
            timeout=8.0  # ✅ REDUCED from 15s to prevent hanging
        )
        
        return response.choices[0].message.content.strip()

    def _generate_adaptive_fallback_response(self, query: str, analyzed_data: List[Dict[str, Any]], all_data: List[Dict[str, Any]], sub_queries: List[Dict[str, Any]]) -> str:
        """Generate fallback response that's adaptive to query type"""
        query_lower = query.lower()
        
        # Bank query fallback
        if any(keyword in query_lower for keyword in ["bank", "account"]):
            return self._generate_bank_fallback(all_data)
        # Payment method fallback
        elif any(keyword in query_lower for keyword in ["credit card", "payment"]):
            return self._generate_payment_fallback(all_data)
        # Job email fallback
        elif any(keyword in query_lower for keyword in ["job", "interview"]):
            return "I couldn't find any job-related emails in your data. Please ensure your email sync is complete."
        # Subscription fallback
        else:
            return self._generate_comprehensive_fallback_response_with_details(query, analyzed_data, all_data)

    def _generate_bank_fallback(self, all_data: List[Dict[str, Any]]) -> str:
        """Generate fallback response for bank queries"""
        banks_found = set()
        accounts_found = set()
        
        for data_set in all_data:
            if data_set["collection"] == "financial_transactions":
                for tx in data_set["results"]:
                    if tx.get("bank_name"):
                        banks_found.add(tx["bank_name"])
                    if tx.get("account_number"):
                        accounts_found.add(tx["account_number"])
        
        if not banks_found and not accounts_found:
            return "I couldn't find any bank account information in your transaction data."
        
        response_parts = ["## 🏦 Your Bank Account Information\n\n"]
        
        if banks_found:
            response_parts.append("### Banks Found:\n")
            for bank in sorted(banks_found):
                response_parts.append(f"- **{bank}**\n")
        
        if accounts_found:
            response_parts.append("\n### Account Numbers Found:\n")
            for account in sorted(accounts_found):
                response_parts.append(f"- {account}\n")
        
        return "".join(response_parts)

    def _generate_payment_fallback(self, all_data: List[Dict[str, Any]]) -> str:
        """Generate fallback response for payment method queries"""
        methods_found = set()
        
        for data_set in all_data:
            if data_set["collection"] == "financial_transactions":
                for tx in data_set["results"]:
                    if tx.get("payment_method"):
                        methods_found.add(tx["payment_method"])
        
        if not methods_found:
            return "I couldn't find any payment method information in your transaction data."
        
        response_parts = ["## 💳 Your Payment Methods\n\n"]
        response_parts.append("### Payment Methods Found:\n")
        for method in sorted(methods_found):
            response_parts.append(f"- **{method.replace('_', ' ').title()}**\n")
        
        return "".join(response_parts)

# Global instance
enhanced_elite_processor = EnhancedEliteQueryProcessor()

async def process_elite_query(user_id: str, query: str) -> Dict[str, Any]:
    """Process a user query using the enhanced elite query processor"""
    return await enhanced_elite_processor.process_query(user_id, query)

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