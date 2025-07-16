"""
MongoDB Query Optimizer for Comprehensive Financial Data
=======================================================

Enhanced query optimization for detailed financial transaction data
with efficient sub-query generation and indexing strategies.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

# Database
from .db import financial_transactions_collection, categorized_emails_collection
from .models.financial import TransactionType, PaymentMethod, ServiceCategory, PaymentStatus

# Configure logging
logger = logging.getLogger(__name__)

class QueryOptimizationLevel(str, Enum):
    """Query optimization levels"""
    BASIC = "basic"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class OptimizedQuery:
    """Optimized MongoDB query with performance metrics"""
    query: Dict[str, Any]
    collection: str
    expected_results: int
    optimization_level: QueryOptimizationLevel
    performance_score: float
    suggested_indexes: List[str]
    execution_plan: Optional[Dict[str, Any]] = None

class ComprehensiveQueryBuilder:
    """Advanced query builder for comprehensive financial data"""
    
    def __init__(self):
        self.setup_query_patterns()
        self.setup_optimization_rules()
    
    def setup_query_patterns(self):
        """Setup common query patterns for efficient retrieval"""
        self.query_patterns = {
            # Transaction type patterns
            "subscription_transactions": {
                "is_subscription": True,
                "subscription_details.is_subscription": True
            },
            "upi_transactions": {
                "payment_method": "upi",
                "upi_details": {"$exists": True}
            },
            "bank_transactions": {
                "bank_details.bank_name": {"$exists": True}
            },
            "high_value_transactions": {
                "amount": {"$gte": 1000}
            },
            "recent_transactions": {
                "transaction_date": {"$gte": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")}
            },
            
            # Merchant patterns
            "food_delivery": {
                "merchant_details.canonical_name": {"$in": ["swiggy", "zomato", "blinkit", "grofers"]}
            },
            "streaming_services": {
                "merchant_details.canonical_name": {"$in": ["netflix", "prime", "hotstar", "spotify"]}
            },
            "ecommerce": {
                "merchant_details.canonical_name": {"$in": ["amazon", "flipkart", "myntra"]}
            },
            "banking": {
                "merchant_details.canonical_name": {"$in": ["hdfc", "icici", "sbi", "axis"]}
            },
            
            # Category patterns
            "entertainment": {
                "service_category": "entertainment"
            },
            "utilities": {
                "service_category": "utilities"
            },
            "telecom": {
                "service_category": "telecom"
            },
            "investment": {
                "service_category": "investment"
            }
        }
    
    def setup_optimization_rules(self):
        """Setup optimization rules for query performance"""
        self.optimization_rules = {
            "index_priority": [
                "user_id",
                "transaction_date",
                "amount",
                "payment_method",
                "service_category",
                "is_subscription",
                "merchant_details.canonical_name"
            ],
            "compound_indexes": [
                ["user_id", "transaction_date"],
                ["user_id", "payment_method"],
                ["user_id", "service_category"],
                ["user_id", "is_subscription"],
                ["user_id", "amount"],
                ["user_id", "merchant_details.canonical_name"]
            ],
            "text_indexes": [
                "merchant_details.canonical_name",
                "description",
                "email_metadata.subject"
            ]
        }
    
    def build_comprehensive_query(self, 
                                user_id: str,
                                filters: Dict[str, Any],
                                optimization_level: QueryOptimizationLevel = QueryOptimizationLevel.ADVANCED) -> OptimizedQuery:
        """Build comprehensive MongoDB query with optimization"""
        
        # Start with base query
        query = {"user_id": user_id}
        
        # Apply filters
        query = self._apply_filters(query, filters)
        
        # Optimize query based on level
        if optimization_level == QueryOptimizationLevel.EXPERT:
            query = self._apply_expert_optimizations(query, filters)
        elif optimization_level == QueryOptimizationLevel.ADVANCED:
            query = self._apply_advanced_optimizations(query, filters)
        
        # Calculate performance metrics
        performance_score = self._calculate_performance_score(query, filters)
        expected_results = self._estimate_result_count(query, filters)
        suggested_indexes = self._suggest_indexes(query, filters)
        
        return OptimizedQuery(
            query=query,
            collection="financial_transactions",
            expected_results=expected_results,
            optimization_level=optimization_level,
            performance_score=performance_score,
            suggested_indexes=suggested_indexes
        )
    
    def _apply_filters(self, base_query: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Apply comprehensive filters to base query"""
        
        # Date range filters
        if filters.get("date_range"):
            date_range = filters["date_range"]
            if date_range.get("start_date") and date_range.get("end_date"):
                base_query["transaction_date"] = {
                    "$gte": date_range["start_date"],
                    "$lte": date_range["end_date"]
                }
        
        # Amount range filters
        if filters.get("amount_range"):
            amount_range = filters["amount_range"]
            if amount_range.get("min_amount") is not None or amount_range.get("max_amount") is not None:
                amount_query = {}
                if amount_range.get("min_amount") is not None:
                    amount_query["$gte"] = amount_range["min_amount"]
                if amount_range.get("max_amount") is not None:
                    amount_query["$lte"] = amount_range["max_amount"]
                base_query["amount"] = amount_query
        
        # Transaction type filters
        if filters.get("transaction_types"):
            base_query["transaction_type"] = {"$in": filters["transaction_types"]}
        
        # Payment method filters
        if filters.get("payment_methods"):
            base_query["payment_method"] = {"$in": filters["payment_methods"]}
        
        # Merchant filters
        if filters.get("merchants"):
            base_query["merchant_details.canonical_name"] = {"$in": filters["merchants"]}
        
        # Category filters
        if filters.get("categories"):
            base_query["service_category"] = {"$in": filters["categories"]}
        
        # Subscription filters
        if filters.get("is_subscription") is not None:
            base_query["is_subscription"] = filters["is_subscription"]
        
        # Confidence filters
        if filters.get("confidence_min"):
            base_query["confidence_score"] = {"$gte": filters["confidence_min"]}
        
        # UPI specific filters
        if filters.get("upi_only"):
            base_query["payment_method"] = "upi"
            base_query["upi_details"] = {"$exists": True}
        
        # Bank specific filters
        if filters.get("bank_name"):
            base_query["bank_details.bank_name"] = filters["bank_name"]
        
        # Subscription product filters
        if filters.get("subscription_products"):
            base_query["subscription_details.product_name"] = {"$in": filters["subscription_products"]}
        
        return base_query
    
    def _apply_advanced_optimizations(self, query: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Apply advanced query optimizations"""
        
        # Use compound index patterns
        if "transaction_date" in query and "amount" in query:
            # Ensure date comes before amount for compound index efficiency
            pass
        
        # Add projection for better performance
        if not filters.get("include_full_data"):
            query["$project"] = {
                "id": 1,
                "amount": 1,
                "transaction_type": 1,
                "merchant": 1,
                "transaction_date": 1,
                "payment_method": 1,
                "is_subscription": 1,
                "confidence_score": 1
            }
        
        return query
    
    def _apply_expert_optimizations(self, query: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Apply expert-level query optimizations"""
        
        # Use aggregation pipeline for complex queries
        if filters.get("complex_analysis"):
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$merchant_details.canonical_name",
                    "total_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1},
                    "avg_amount": {"$avg": "$amount"}
                }},
                {"$sort": {"total_amount": -1}}
            ]
            query = {"$pipeline": pipeline}
        
        return query
    
    def _calculate_performance_score(self, query: Dict[str, Any], filters: Dict[str, Any]) -> float:
        """Calculate query performance score (0-1)"""
        score = 1.0
        
        # Penalize complex queries
        if len(query) > 5:
            score -= 0.1
        
        # Penalize text searches
        if any("$text" in str(v) for v in query.values()):
            score -= 0.2
        
        # Penalize large date ranges
        if "transaction_date" in query:
            date_query = query["transaction_date"]
            if isinstance(date_query, dict) and "$gte" in date_query and "$lte" in date_query:
                # Calculate date range size
                pass
        
        # Bonus for indexed fields
        indexed_fields = ["user_id", "transaction_date", "amount", "payment_method"]
        for field in indexed_fields:
            if field in query:
                score += 0.05
        
        return max(0.0, min(1.0, score))
    
    def _estimate_result_count(self, query: Dict[str, Any], filters: Dict[str, Any]) -> int:
        """Estimate number of results for the query"""
        # This would ideally use MongoDB's explain() or statistics
        # For now, return a reasonable estimate
        base_estimate = 100
        
        # Adjust based on filters
        if filters.get("date_range"):
            base_estimate *= 0.5  # Date range reduces results
        
        if filters.get("amount_range"):
            base_estimate *= 0.7  # Amount range reduces results
        
        if filters.get("merchants"):
            base_estimate *= 0.3  # Specific merchants reduce results
        
        if filters.get("is_subscription"):
            base_estimate *= 0.4  # Subscriptions are subset
        
        return int(base_estimate)
    
    def _suggest_indexes(self, query: Dict[str, Any], filters: Dict[str, Any]) -> List[str]:
        """Suggest optimal indexes for the query"""
        suggested = []
        
        # Always suggest user_id index
        suggested.append("user_id")
        
        # Suggest based on query fields
        if "transaction_date" in query:
            suggested.append("user_id_transaction_date")
        
        if "amount" in query:
            suggested.append("user_id_amount")
        
        if "payment_method" in query:
            suggested.append("user_id_payment_method")
        
        if "service_category" in query:
            suggested.append("user_id_service_category")
        
        if "is_subscription" in query:
            suggested.append("user_id_is_subscription")
        
        if "merchant_details.canonical_name" in query:
            suggested.append("user_id_merchant_canonical")
        
        return suggested

class SubQueryGenerator:
    """Generate optimized sub-queries for comprehensive data retrieval"""
    
    def __init__(self):
        self.query_builder = ComprehensiveQueryBuilder()
    
    def generate_sub_queries(self, user_id: str, intent_analysis: Dict[str, Any]) -> List[OptimizedQuery]:
        """Generate comprehensive sub-queries based on intent analysis"""
        
        sub_queries = []
        
        # Generate queries based on intent
        primary_intent = intent_analysis.get("primary_intent", "general")
        
        if primary_intent == "spending_analysis":
            sub_queries.extend(self._generate_spending_analysis_queries(user_id, intent_analysis))
        elif primary_intent == "subscription_analysis":
            sub_queries.extend(self._generate_subscription_analysis_queries(user_id, intent_analysis))
        elif primary_intent == "merchant_analysis":
            sub_queries.extend(self._generate_merchant_analysis_queries(user_id, intent_analysis))
        elif primary_intent == "payment_method_analysis":
            sub_queries.extend(self._generate_payment_method_analysis_queries(user_id, intent_analysis))
        else:
            sub_queries.extend(self._generate_general_analysis_queries(user_id, intent_analysis))
        
        return sub_queries
    
    def _generate_spending_analysis_queries(self, user_id: str, intent_analysis: Dict[str, Any]) -> List[OptimizedQuery]:
        """Generate queries for spending analysis"""
        queries = []
        
        # Overall spending
        queries.append(self.query_builder.build_comprehensive_query(
            user_id=user_id,
            filters={"transaction_types": ["debit", "payment", "bill"]},
            optimization_level=QueryOptimizationLevel.ADVANCED
        ))
        
        # Category-wise spending
        categories = intent_analysis.get("categories", [])
        for category in categories:
            queries.append(self.query_builder.build_comprehensive_query(
                user_id=user_id,
                filters={
                    "categories": [category],
                    "transaction_types": ["debit", "payment", "bill"]
                }
            ))
        
        # High-value transactions
        queries.append(self.query_builder.build_comprehensive_query(
            user_id=user_id,
            filters={"amount_range": {"min_amount": 1000}},
            optimization_level=QueryOptimizationLevel.ADVANCED
        ))
        
        return queries
    
    def _generate_subscription_analysis_queries(self, user_id: str, intent_analysis: Dict[str, Any]) -> List[OptimizedQuery]:
        """Generate queries for subscription analysis"""
        queries = []
        
        # All subscriptions
        queries.append(self.query_builder.build_comprehensive_query(
            user_id=user_id,
            filters={"is_subscription": True},
            optimization_level=QueryOptimizationLevel.ADVANCED
        ))
        
        # Subscription by category
        subscription_categories = ["ott", "cloud_storage", "entertainment", "utilities"]
        for category in subscription_categories:
            queries.append(self.query_builder.build_comprehensive_query(
                user_id=user_id,
                filters={
                    "is_subscription": True,
                    "categories": [category]
                }
            ))
        
        # Recurring payments
        queries.append(self.query_builder.build_comprehensive_query(
            user_id=user_id,
            filters={
                "is_subscription": True,
                "subscription_details.is_automatic_payment": True
            }
        ))
        
        return queries
    
    def _generate_merchant_analysis_queries(self, user_id: str, intent_analysis: Dict[str, Any]) -> List[OptimizedQuery]:
        """Generate queries for merchant analysis"""
        queries = []
        
        # Top merchants
        merchants = intent_analysis.get("merchants", [])
        for merchant in merchants:
            queries.append(self.query_builder.build_comprehensive_query(
                user_id=user_id,
                filters={"merchants": [merchant]}
            ))
        
        # Food delivery merchants
        queries.append(self.query_builder.build_comprehensive_query(
            user_id=user_id,
            filters={"merchants": ["swiggy", "zomato", "blinkit", "grofers"]}
        ))
        
        # E-commerce merchants
        queries.append(self.query_builder.build_comprehensive_query(
            user_id=user_id,
            filters={"merchants": ["amazon", "flipkart", "myntra"]}
        ))
        
        return queries
    
    def _generate_payment_method_analysis_queries(self, user_id: str, intent_analysis: Dict[str, Any]) -> List[OptimizedQuery]:
        """Generate queries for payment method analysis"""
        queries = []
        
        # UPI transactions
        queries.append(self.query_builder.build_comprehensive_query(
            user_id=user_id,
            filters={"payment_methods": ["upi"]},
            optimization_level=QueryOptimizationLevel.ADVANCED
        ))
        
        # Card transactions
        queries.append(self.query_builder.build_comprehensive_query(
            user_id=user_id,
            filters={"payment_methods": ["credit_card", "debit_card"]}
        ))
        
        # Bank transfers
        queries.append(self.query_builder.build_comprehensive_query(
            user_id=user_id,
            filters={"payment_methods": ["bank_transfer", "net_banking"]}
        ))
        
        return queries
    
    def _generate_general_analysis_queries(self, user_id: str, intent_analysis: Dict[str, Any]) -> List[OptimizedQuery]:
        """Generate general analysis queries"""
        queries = []
        
        # Recent transactions
        queries.append(self.query_builder.build_comprehensive_query(
            user_id=user_id,
            filters={"date_range": {
                "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                "end_date": datetime.now().strftime("%Y-%m-%d")
            }}
        ))
        
        # All transactions
        queries.append(self.query_builder.build_comprehensive_query(
            user_id=user_id,
            filters={}
        ))
        
        return queries

# Convenience functions
async def optimize_database_indexes():
    """Create optimal indexes for comprehensive financial data"""
    try:
        # Create compound indexes for efficient queries
        indexes = [
            [("user_id", 1), ("transaction_date", -1)],
            [("user_id", 1), ("payment_method", 1)],
            [("user_id", 1), ("service_category", 1)],
            [("user_id", 1), ("is_subscription", 1)],
            [("user_id", 1), ("amount", -1)],
            [("user_id", 1), ("merchant_details.canonical_name", 1)],
            [("user_id", 1), ("confidence_score", -1)],
            [("user_id", 1), ("transaction_type", 1)],
            [("user_id", 1), ("bank_details.bank_name", 1)],
            [("user_id", 1), ("subscription_details.product_name", 1)]
        ]
        
        for index in indexes:
            await financial_transactions_collection.create_index(index)
        
        logger.info(f"✅ Created {len(indexes)} optimized indexes for financial transactions")
        
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}")

async def get_query_performance_stats():
    """Get query performance statistics"""
    try:
        # This would use MongoDB's explain() and stats commands
        # For now, return basic stats
        total_transactions = await financial_transactions_collection.count_documents({})
        
        return {
            "total_transactions": total_transactions,
            "indexes_created": True,
            "optimization_level": "advanced"
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting performance stats: {e}")
        return {"error": str(e)} 