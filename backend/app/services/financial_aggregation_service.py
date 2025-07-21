"""
Financial Aggregation Service
============================

Comprehensive service for financial data aggregation and analytics.
Implements 30 different aggregation pipelines for financial insights.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class FinancialAggregationService:
    """Service for financial data aggregation and analytics."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.financial_transactions
    
    # ============================================================================
    # BASIC FINANCIAL QUERIES (1-10)
    # ============================================================================
    
    async def get_monthly_spending_trends(self, user_id: str, months: int = 12) -> Dict[str, Any]:
        """Query 1: Show me total spending by month for the last 12 months"""
        try:
            start_date = datetime.now() - timedelta(days=months * 30)
            
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "date": {
                            "$gte": start_date,
                            "$lte": datetime.now()
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"}
                        },
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "max_amount": {"$max": "$amount"},
                        "min_amount": {"$min": "$amount"}
                    }
                },
                {
                    "$sort": {"_id.year": 1, "_id.month": 1}
                },
                {
                    "$project": {
                        "month": {
                            "$concat": [
                                {"$toString": "$_id.year"},
                                "-",
                                {"$toString": "$_id.month"}
                            ]
                        },
                        "total_spending": 1,
                        "transaction_count": 1,
                        "avg_amount": 1,
                        "max_amount": 1,
                        "min_amount": 1
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_monthly_spending_trends: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_top_merchants_analysis(self, user_id: str, limit: int = 15) -> Dict[str, Any]:
        """Query 2: What are my top 15 merchants by total spending?"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": "$merchant_canonical",
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "last_transaction": {"$max": "$date"},
                        "first_transaction": {"$min": "$date"},
                        "categories": {"$addToSet": "$service_category"}
                    }
                },
                {
                    "$sort": {"total_spending": -1}
                },
                {
                    "$limit": limit
                },
                {
                    "$project": {
                        "merchant": "$_id",
                        "total_spending": 1,
                        "transaction_count": 1,
                        "avg_amount": 1,
                        "last_transaction": 1,
                        "first_transaction": 1,
                        "categories": 1,
                        "spending_frequency": {
                            "$divide": [
                                {"$subtract": ["$last_transaction", "$first_transaction"]},
                                {"$multiply": [1000 * 60 * 60 * 24, "$transaction_count"]}
                            ]
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_top_merchants_analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_category_breakdown_with_percentages(self, user_id: str) -> Dict[str, Any]:
        """Query 3: Show me spending breakdown by category with percentages"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": "$service_category",
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "merchants": {"$addToSet": "$merchant_canonical"},
                        "payment_methods": {"$addToSet": "$payment_method"}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "categories": {"$push": "$$ROOT"},
                        "grand_total": {"$sum": "$total_spending"}
                    }
                },
                {
                    "$unwind": "$categories"
                },
                {
                    "$project": {
                        "category": "$categories._id",
                        "total_spending": "$categories.total_spending",
                        "transaction_count": "$categories.transaction_count",
                        "avg_amount": "$categories.avg_amount",
                        "unique_merchants": {"$size": "$categories.merchants"},
                        "payment_methods": "$categories.payment_methods",
                        "percentage": {
                            "$multiply": [
                                {"$divide": ["$categories.total_spending", "$grand_total"]},
                                100
                            ]
                        }
                    }
                },
                {
                    "$sort": {"total_spending": -1}
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_category_breakdown_with_percentages: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_subscription_analysis(self, user_id: str) -> Dict[str, Any]:
        """Query 4: Find all my subscription payments with renewal dates"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "is_subscription": True
                    }
                },
                {
                    "$group": {
                        "_id": "$merchant_canonical",
                        "total_subscription_cost": {"$sum": "$amount"},
                        "subscription_count": {"$sum": 1},
                        "last_payment": {"$max": "$date"},
                        "next_renewal": {"$first": "$subscription_details.next_renewal_date"},
                        "product_name": {"$first": "$subscription_product"},
                        "billing_frequency": {"$first": "$subscription_details.subscription_frequency"},
                        "avg_monthly_cost": {
                            "$avg": {
                                "$cond": [
                                    {"$eq": ["$subscription_details.subscription_frequency", "monthly"]},
                                    "$amount",
                                    {"$divide": ["$amount", 12]}
                                ]
                            }
                        }
                    }
                },
                {
                    "$sort": {"total_subscription_cost": -1}
                },
                {
                    "$project": {
                        "service": "$_id",
                        "total_cost": "$total_subscription_cost",
                        "subscription_count": 1,
                        "last_payment": 1,
                        "next_renewal": 1,
                        "product_name": 1,
                        "billing_frequency": 1,
                        "avg_monthly_cost": 1,
                        "days_until_renewal": {
                            "$ceil": {
                                "$divide": [
                                    {"$subtract": ["$next_renewal", datetime.now()]},
                                    1000 * 60 * 60 * 24
                                ]
                            }
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_subscription_analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_daily_spending_patterns(self, user_id: str, days: int = 90) -> Dict[str, Any]:
        """Query 5: Show me daily spending for the last 90 days"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "date": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"},
                            "day": {"$dayOfMonth": "$date"}
                        },
                        "daily_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "categories": {"$addToSet": "$service_category"},
                        "merchants": {"$addToSet": "$merchant_canonical"}
                    }
                },
                {
                    "$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}
                },
                {
                    "$project": {
                        "date": {
                            "$dateFromParts": {
                                "year": "$_id.year",
                                "month": "$_id.month",
                                "day": "$_id.day"
                            }
                        },
                        "daily_spending": 1,
                        "transaction_count": 1,
                        "categories": 1,
                        "merchants": 1,
                        "avg_transaction": {"$divide": ["$daily_spending", "$transaction_count"]}
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_daily_spending_patterns: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_high_value_transactions(self, user_id: str, min_amount: float = 2000) -> Dict[str, Any]:
        """Query 6: Find all transactions above ₹2000 with details"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "amount": {"$gte": min_amount}
                    }
                },
                {
                    "$sort": {"amount": -1}
                },
                {
                    "$project": {
                        "date": 1,
                        "amount": 1,
                        "merchant": "$merchant_canonical",
                        "category": "$service_category",
                        "payment_method": 1,
                        "description": 1,
                        "transaction_type": 1,
                        "is_subscription": 1,
                        "upi_details": 1,
                        "bank_details": 1
                    }
                },
                {
                    "$group": {
                        "_id": "$category",
                        "high_value_transactions": {"$sum": 1},
                        "total_amount": {"$sum": "$amount"},
                        "avg_amount": {"$avg": "$amount"},
                        "transactions": {
                            "$push": {
                                "date": "$date",
                                "amount": "$amount",
                                "merchant": "$merchant",
                                "payment_method": "$payment_method",
                                "description": "$description"
                            }
                        }
                    }
                },
                {
                    "$sort": {"total_amount": -1}
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_high_value_transactions: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_payment_method_breakdown(self, user_id: str) -> Dict[str, Any]:
        """Query 7: Show me UPI vs Card vs Net Banking payment breakdown"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": "$payment_method",
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "max_amount": {"$max": "$amount"},
                        "min_amount": {"$min": "$amount"},
                        "merchants": {"$addToSet": "$merchant_canonical"},
                        "categories": {"$addToSet": "$service_category"}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "methods": {"$push": "$$ROOT"},
                        "grand_total": {"$sum": "$total_spending"}
                    }
                },
                {
                    "$unwind": "$methods"
                },
                {
                    "$project": {
                        "payment_method": "$methods._id",
                        "total_spending": "$methods.total_spending",
                        "transaction_count": "$methods.transaction_count",
                        "avg_amount": "$methods.avg_amount",
                        "max_amount": "$methods.max_amount",
                        "min_amount": "$methods.min_amount",
                        "unique_merchants": {"$size": "$methods.merchants"},
                        "categories": "$methods.categories",
                        "percentage": {
                            "$multiply": [
                                {"$divide": ["$methods.total_spending", "$grand_total"]},
                                100
                            ]
                        }
                    }
                },
                {
                    "$sort": {"total_spending": -1}
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_payment_method_breakdown: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_refund_analysis(self, user_id: str) -> Dict[str, Any]:
        """Query 8: Find all refund transactions with original transaction details"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "transaction_type": "refund"
                    }
                },
                {
                    "$lookup": {
                        "from": "financial_transactions",
                        "localField": "transaction_reference",
                        "foreignField": "transaction_id",
                        "as": "original_transaction"
                    }
                },
                {
                    "$unwind": {"path": "$original_transaction", "preserveNullAndEmptyArrays": True}
                },
                {
                    "$sort": {"date": -1}
                },
                {
                    "$project": {
                        "refund_date": "$date",
                        "refund_amount": "$amount",
                        "original_amount": "$original_transaction.amount",
                        "merchant": "$merchant_canonical",
                        "original_merchant": "$original_transaction.merchant_canonical",
                        "refund_reason": "$description",
                        "original_transaction_date": "$original_transaction.date",
                        "payment_method": 1,
                        "upi_details": 1
                    }
                },
                {
                    "$group": {
                        "_id": "$merchant",
                        "refund_count": {"$sum": 1},
                        "total_refunded": {"$sum": "$refund_amount"},
                        "avg_refund": {"$avg": "$refund_amount"},
                        "refunds": {
                            "$push": {
                                "refund_date": "$refund_date",
                                "refund_amount": "$refund_amount",
                                "original_amount": "$original_amount",
                                "refund_reason": "$refund_reason"
                            }
                        }
                    }
                },
                {
                    "$sort": {"total_refunded": -1}
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_refund_analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_weekly_spending_patterns(self, user_id: str) -> Dict[str, Any]:
        """Query 9: Show me spending by day of week with patterns"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": {"$dayOfWeek": "$date"},
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "categories": {"$addToSet": "$service_category"},
                        "merchants": {"$addToSet": "$merchant_canonical"}
                    }
                },
                {
                    "$project": {
                        "day_of_week": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$eq": ["$_id", 1]}, "then": "Sunday"},
                                    {"case": {"$eq": ["$_id", 2]}, "then": "Monday"},
                                    {"case": {"$eq": ["$_id", 3]}, "then": "Tuesday"},
                                    {"case": {"$eq": ["$_id", 4]}, "then": "Wednesday"},
                                    {"case": {"$eq": ["$_id", 5]}, "then": "Thursday"},
                                    {"case": {"$eq": ["$_id", 6]}, "then": "Friday"},
                                    {"case": {"$eq": ["$_id", 7]}, "then": "Saturday"}
                                ]
                            }
                        },
                        "total_spending": 1,
                        "transaction_count": 1,
                        "avg_amount": 1,
                        "categories": 1,
                        "merchants": 1,
                        "spending_per_transaction": {"$divide": ["$total_spending", "$transaction_count"]}
                    }
                },
                {
                    "$sort": {"_id": 1}
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_weekly_spending_patterns: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_food_delivery_analysis(self, user_id: str) -> Dict[str, Any]:
        """Query 10: Find all food delivery transactions with restaurant analysis"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "service_category": "food"
                    }
                },
                {
                    "$group": {
                        "_id": "$merchant_canonical",
                        "total_spending": {"$sum": "$amount"},
                        "order_count": {"$sum": 1},
                        "avg_order_value": {"$avg": "$amount"},
                        "max_order": {"$max": "$amount"},
                        "min_order": {"$min": "$amount"},
                        "last_order": {"$max": "$date"},
                        "first_order": {"$min": "$date"},
                        "payment_methods": {"$addToSet": "$payment_method"}
                    }
                },
                {
                    "$sort": {"total_spending": -1}
                },
                {
                    "$project": {
                        "restaurant": "$_id",
                        "total_spending": 1,
                        "order_count": 1,
                        "avg_order_value": 1,
                        "max_order": 1,
                        "min_order": 1,
                        "last_order": 1,
                        "first_order": 1,
                        "payment_methods": 1,
                        "days_since_last_order": {
                            "$ceil": {
                                "$divide": [
                                    {"$subtract": [datetime.now(), "$last_order"]},
                                    1000 * 60 * 60 * 24
                                ]
                            }
                        },
                        "customer_lifetime": {
                            "$ceil": {
                                "$divide": [
                                    {"$subtract": ["$last_order", "$first_order"]},
                                    1000 * 60 * 60 * 24
                                ]
                            }
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_food_delivery_analysis: {e}")
            return {"success": False, "error": str(e)} 
    # ============================================================================
    # ADVANCED FINANCIAL QUERIES (11-20)
    # ============================================================================
    
    async def get_subscription_trend_analysis(self, user_id: str) -> Dict[str, Any]:
        """Query 11: Show me monthly subscription costs with trend analysis"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "is_subscription": True
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"}
                        },
                        "subscription_cost": {"$sum": "$amount"},
                        "subscription_count": {"$sum": 1},
                        "services": {"$addToSet": "$merchant_canonical"},
                        "new_subscriptions": {
                            "$sum": {
                                "$cond": [
                                    {"$eq": ["$transaction_type", "subscription"]},
                                    1,
                                    0
                                ]
                            }
                        }
                    }
                },
                {
                    "$sort": {"_id.year": 1, "_id.month": 1}
                },
                {
                    "$group": {
                        "_id": None,
                        "months": {
                            "$push": {
                                "month": {
                                    "$concat": [
                                        {"$toString": "$_id.year"},
                                        "-",
                                        {"$toString": "$_id.month"}
                                    ]
                                },
                                "subscription_cost": "$subscription_cost",
                                "subscription_count": "$subscription_count",
                                "services": "$services",
                                "new_subscriptions": "$new_subscriptions"
                            }
                        }
                    }
                },
                {
                    "$unwind": {"path": "$months", "includeArrayIndex": "monthIndex"}
                },
                {
                    "$project": {
                        "month": "$months.month",
                        "subscription_cost": "$months.subscription_cost",
                        "subscription_count": "$months.subscription_count",
                        "services": "$months.services",
                        "new_subscriptions": "$months.new_subscriptions",
                        "month_index": {"$add": ["$monthIndex", 1]},
                        "cost_change": {
                            "$subtract": [
                                "$months.subscription_cost",
                                {"$arrayElemAt": ["$months.subscription_cost", {"$subtract": ["$monthIndex", 1]}]}
                            ]
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_subscription_trend_analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_travel_booking_analysis(self, user_id: str) -> Dict[str, Any]:
        """Query 12: Find all travel bookings with cost analysis"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": "$booking_type",
                        "total_spending": {"$sum": "$total_amount"},
                        "booking_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$total_amount"},
                        "max_amount": {"$max": "$total_amount"},
                        "min_amount": {"$min": "$total_amount"},
                        "providers": {"$addToSet": "$service_provider"},
                        "destinations": {"$addToSet": "$to_location.city"}
                    }
                },
                {
                    "$sort": {"total_spending": -1}
                },
                {
                    "$project": {
                        "travel_type": "$_id",
                        "total_spending": 1,
                        "booking_count": 1,
                        "avg_amount": 1,
                        "max_amount": 1,
                        "min_amount": 1,
                        "providers": 1,
                        "destinations": 1,
                        "avg_cost_per_booking": {"$divide": ["$total_spending", "$booking_count"]}
                    }
                }
            ]
            
            result = await self.db.travel_bookings.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_travel_booking_analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_spending_trends_with_growth(self, user_id: str) -> Dict[str, Any]:
        """Query 13: Show me spending trends with month-over-month growth"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"}
                        },
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "categories": {"$addToSet": "$service_category"},
                        "merchants": {"$addToSet": "$merchant_canonical"}
                    }
                },
                {
                    "$sort": {"_id.year": 1, "_id.month": 1}
                },
                {
                    "$group": {
                        "_id": None,
                        "months": {
                            "$push": {
                                "month": {
                                    "$concat": [
                                        {"$toString": "$_id.year"},
                                        "-",
                                        {"$toString": "$_id.month"}
                                    ]
                                },
                                "total_spending": "$total_spending",
                                "transaction_count": "$transaction_count",
                                "avg_amount": "$avg_amount",
                                "categories": "$categories",
                                "merchants": "$merchants"
                            }
                        }
                    }
                },
                {
                    "$unwind": {"path": "$months", "includeArrayIndex": "monthIndex"}
                },
                {
                    "$project": {
                        "month": "$months.month",
                        "total_spending": "$months.total_spending",
                        "transaction_count": "$months.transaction_count",
                        "avg_amount": "$months.avg_amount",
                        "categories": "$months.categories",
                        "merchants": "$months.merchants",
                        "month_index": {"$add": ["$monthIndex", 1]},
                        "spending_growth": {
                            "$cond": [
                                {"$gt": ["$monthIndex", 0]},
                                {
                                    "$multiply": [
                                        {
                                            "$divide": [
                                                {"$subtract": ["$months.total_spending", {"$arrayElemAt": ["$months.total_spending", {"$subtract": ["$monthIndex", 1]}]}]},
                                                {"$arrayElemAt": ["$months.total_spending", {"$subtract": ["$monthIndex", 1]}]}
                                            ]
                                        },
                                        100
                                    ]
                                },
                                0
                            ]
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_spending_trends_with_growth: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_automatic_payments_analysis(self, user_id: str) -> Dict[str, Any]:
        """Query 14: Find all automatic payments with renewal analysis"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "is_automatic_payment": True
                    }
                },
                {
                    "$group": {
                        "_id": "$merchant_canonical",
                        "total_auto_payments": {"$sum": "$amount"},
                        "payment_count": {"$sum": 1},
                        "last_payment": {"$max": "$date"},
                        "next_payment": {"$first": "$subscription_details.next_renewal_date"},
                        "avg_amount": {"$avg": "$amount"},
                        "billing_frequency": {"$first": "$subscription_details.subscription_frequency"},
                        "product_name": {"$first": "$subscription_product"}
                    }
                },
                {
                    "$sort": {"total_auto_payments": -1}
                },
                {
                    "$project": {
                        "service": "$_id",
                        "total_auto_payments": 1,
                        "payment_count": 1,
                        "last_payment": 1,
                        "next_payment": 1,
                        "avg_amount": 1,
                        "billing_frequency": 1,
                        "product_name": 1,
                        "days_until_renewal": {
                            "$ceil": {
                                "$divide": [
                                    {"$subtract": ["$next_payment", datetime.now()]},
                                    1000 * 60 * 60 * 24
                                ]
                            }
                        },
                        "monthly_cost": {
                            "$cond": [
                                {"$eq": ["$billing_frequency", "monthly"]},
                                "$avg_amount",
                                {"$divide": ["$avg_amount", 12]}
                            ]
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_automatic_payments_analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_payment_method_security_analysis(self, user_id: str) -> Dict[str, Any]:
        """Query 15: Show me spending by payment method with security analysis"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": "$payment_method",
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "max_amount": {"$max": "$amount"},
                        "min_amount": {"$min": "$amount"},
                        "merchants": {"$addToSet": "$merchant_canonical"},
                        "categories": {"$addToSet": "$service_category"}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "methods": {"$push": "$$ROOT"},
                        "grand_total": {"$sum": "$total_spending"}
                    }
                },
                {
                    "$unwind": "$methods"
                },
                {
                    "$project": {
                        "payment_method": "$methods._id",
                        "total_spending": "$methods.total_spending",
                        "transaction_count": "$methods.transaction_count",
                        "avg_amount": "$methods.avg_amount",
                        "max_amount": "$methods.max_amount",
                        "min_amount": "$methods.min_amount",
                        "unique_merchants": {"$size": "$methods.merchants"},
                        "categories": "$methods.categories",
                        "percentage": {
                            "$multiply": [
                                {"$divide": ["$methods.total_spending", "$grand_total"]},
                                100
                            ]
                        },
                        "security_score": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$eq": ["$methods._id", "upi"]}, "then": 85},
                                    {"case": {"$eq": ["$methods._id", "credit_card"]}, "then": 90},
                                    {"case": {"$eq": ["$methods._id", "debit_card"]}, "then": 80},
                                    {"case": {"$eq": ["$methods._id", "net_banking"]}, "then": 95}
                                ],
                                "default": 70
                            }
                        }
                    }
                },
                {
                    "$sort": {"total_spending": -1}
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_payment_method_security_analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_promotional_emails_analysis(self, user_id: str) -> Dict[str, Any]:
        """Query 16: Find all promotional emails with discount analysis"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": "$merchant_canonical",
                        "offer_count": {"$sum": 1},
                        "total_discount": {"$sum": "$discount_amount"},
                        "avg_discount": {"$avg": "$discount_amount"},
                        "max_discount": {"$max": "$discount_amount"},
                        "valid_offers": {
                            "$sum": {
                                "$cond": [
                                    {"$gt": ["$valid_until", datetime.now()]},
                                    1,
                                    0
                                ]
                            }
                        },
                        "expired_offers": {
                            "$sum": {
                                "$cond": [
                                    {"$lt": ["$valid_until", datetime.now()]},
                                    1,
                                    0
                                ]
                            }
                        },
                        "promotion_types": {"$addToSet": "$promotion_type"}
                    }
                },
                {
                    "$sort": {"offer_count": -1}
                },
                {
                    "$project": {
                        "merchant": "$_id",
                        "offer_count": 1,
                        "total_discount": 1,
                        "avg_discount": 1,
                        "max_discount": 1,
                        "valid_offers": 1,
                        "expired_offers": 1,
                        "promotion_types": 1,
                        "discount_utilization_rate": {
                            "$multiply": [
                                {"$divide": ["$valid_offers", "$offer_count"]},
                                100
                            ]
                        }
                    }
                }
            ]
            
            result = await self.db.promotional_emails.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_promotional_emails_analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_job_application_status(self, user_id: str) -> Dict[str, Any]:
        """Query 17: Show me job application status with company analysis"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": "$application_status",
                        "application_count": {"$sum": 1},
                        "companies": {"$addToSet": "$company_name"},
                        "latest_update": {"$max": "$updated_at"},
                        "avg_salary": {"$avg": "$salary_offered"},
                        "max_salary": {"$max": "$salary_offered"},
                        "min_salary": {"$min": "$salary_offered"}
                    }
                },
                {
                    "$sort": {"application_count": -1}
                },
                {
                    "$project": {
                        "status": "$_id",
                        "application_count": 1,
                        "companies": 1,
                        "latest_update": 1,
                        "avg_salary": 1,
                        "max_salary": 1,
                        "min_salary": 1,
                        "unique_companies": {"$size": "$companies"}
                    }
                }
            ]
            
            result = await self.db.job_communications.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_job_application_status: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_date_range_analysis(self, user_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Query 18: Find all transactions from specific date range with category breakdown"""
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "date": {
                            "$gte": start_dt,
                            "$lte": end_dt
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"},
                            "day": {"$dayOfMonth": "$date"}
                        },
                        "daily_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "categories": {
                            "$push": {
                                "category": "$service_category",
                                "amount": "$amount",
                                "merchant": "$merchant_canonical"
                            }
                        },
                        "merchants": {"$addToSet": "$merchant_canonical"}
                    }
                },
                {
                    "$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}
                },
                {
                    "$project": {
                        "date": {
                            "$dateFromParts": {
                                "year": "$_id.year",
                                "month": "$_id.month",
                                "day": "$_id.day"
                            }
                        },
                        "daily_spending": 1,
                        "transaction_count": 1,
                        "categories": 1,
                        "merchants": 1,
                        "avg_transaction": {"$divide": ["$daily_spending", "$transaction_count"]}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "days": {"$push": "$$ROOT"},
                        "total_period_spending": {"$sum": "$daily_spending"},
                        "total_transactions": {"$sum": "$transaction_count"}
                    }
                },
                {
                    "$unwind": "$days"
                },
                {
                    "$project": {
                        "date": "$days.date",
                        "daily_spending": "$days.daily_spending",
                        "transaction_count": "$days.transaction_count",
                        "categories": "$days.categories",
                        "merchants": "$days.merchants",
                        "avg_transaction": "$days.avg_transaction",
                        "total_period_spending": "$total_period_spending",
                        "total_transactions": "$total_transactions",
                        "daily_percentage": {
                            "$multiply": [
                                {"$divide": ["$days.daily_spending", "$total_period_spending"]},
                                100
                            ]
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_date_range_analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_monthly_comparison(self, user_id: str, current_month: str, previous_month: str) -> Dict[str, Any]:
        """Query 19: Show me spending comparison with previous month"""
        try:
            current_dt = datetime.fromisoformat(current_month)
            previous_dt = datetime.fromisoformat(previous_month)
            
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "date": {
                            "$gte": previous_dt,
                            "$lte": current_dt
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"}
                        },
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "categories": {"$addToSet": "$service_category"},
                        "merchants": {"$addToSet": "$merchant_canonical"}
                    }
                },
                {
                    "$sort": {"_id.year": 1, "_id.month": 1}
                },
                {
                    "$group": {
                        "_id": None,
                        "months": {
                            "$push": {
                                "month": {
                                    "$concat": [
                                        {"$toString": "$_id.year"},
                                        "-",
                                        {"$toString": "$_id.month"}
                                    ]
                                },
                                "total_spending": "$total_spending",
                                "transaction_count": "$transaction_count",
                                "avg_amount": "$avg_amount",
                                "categories": "$categories",
                                "merchants": "$merchants"
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "current_month": {"$arrayElemAt": ["$months", 1]},
                        "previous_month": {"$arrayElemAt": ["$months", 0]},
                        "spending_change": {
                            "$subtract": [
                                {"$arrayElemAt": ["$months.total_spending", 1]},
                                {"$arrayElemAt": ["$months.total_spending", 0]}
                            ]
                        },
                        "spending_change_percentage": {
                            "$multiply": [
                                {
                                    "$divide": [
                                        {
                                            "$subtract": [
                                                {"$arrayElemAt": ["$months.total_spending", 1]},
                                                {"$arrayElemAt": ["$months.total_spending", 0]}
                                            ]
                                        },
                                        {"$arrayElemAt": ["$months.total_spending", 0]}
                                    ]
                                },
                                100
                            ]
                        },
                        "transaction_change": {
                            "$subtract": [
                                {"$arrayElemAt": ["$months.transaction_count", 1]},
                                {"$arrayElemAt": ["$months.transaction_count", 0]}
                            ]
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_monthly_comparison: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_high_value_categories(self, user_id: str, min_amount: float = 5000) -> Dict[str, Any]:
        """Query 20: Find all high-value transactions by category with risk analysis"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "amount": {"$gte": min_amount}
                    }
                },
                {
                    "$group": {
                        "_id": "$service_category",
                        "high_value_transactions": {"$sum": 1},
                        "total_amount": {"$sum": "$amount"},
                        "avg_amount": {"$avg": "$amount"},
                        "max_amount": {"$max": "$amount"},
                        "min_amount": {"$min": "$amount"},
                        "merchants": {"$addToSet": "$merchant_canonical"},
                        "payment_methods": {"$addToSet": "$payment_method"},
                        "transactions": {
                            "$push": {
                                "date": "$date",
                                "amount": "$amount",
                                "merchant": "$merchant_canonical",
                                "payment_method": "$payment_method",
                                "description": "$description",
                                "is_subscription": "$is_subscription"
                            }
                        }
                    }
                },
                {
                    "$sort": {"total_amount": -1}
                },
                {
                    "$project": {
                        "category": "$_id",
                        "high_value_transactions": 1,
                        "total_amount": 1,
                        "avg_amount": 1,
                        "max_amount": 1,
                        "min_amount": 1,
                        "unique_merchants": {"$size": "$merchants"},
                        "payment_methods": 1,
                        "transactions": 1,
                        "risk_score": {
                            "$add": [
                                {"$multiply": [{"$divide": ["$high_value_transactions", 10]}, 30]},
                                {"$multiply": [{"$divide": ["$avg_amount", 10000]}, 40]},
                                {"$multiply": [{"$size": "$merchants"}, 5]}
                            ]
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_high_value_categories: {e}")
            return {"success": False, "error": str(e)} 
    # ============================================================================
    # COMPLEX FINANCIAL ANALYTICS (21-30)
    # ============================================================================
    
    async def get_time_of_day_patterns(self, user_id: str) -> Dict[str, Any]:
        """Query 21: Show me spending patterns by time of day"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": {"$hour": "$date"},
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "categories": {"$addToSet": "$service_category"},
                        "merchants": {"$addToSet": "$merchant_canonical"}
                    }
                },
                {
                    "$sort": {"_id": 1}
                },
                {
                    "$project": {
                        "hour": "$_id",
                        "total_spending": 1,
                        "transaction_count": 1,
                        "avg_amount": 1,
                        "categories": 1,
                        "merchants": 1,
                        "time_period": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$lt": ["$_id", 6]}, "then": "Early Morning (12-6 AM)"},
                                    {"case": {"$lt": ["$_id", 12]}, "then": "Morning (6-12 PM)"},
                                    {"case": {"$lt": ["$_id", 18]}, "then": "Afternoon (12-6 PM)"},
                                    {"case": {"$lt": ["$_id", 24]}, "then": "Evening (6-12 AM)"}
                                ]
                            }
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$time_period",
                        "total_spending": {"$sum": "$total_spending"},
                        "transaction_count": {"$sum": "$transaction_count"},
                        "avg_amount": {"$avg": "$avg_amount"},
                        "hours": {"$push": "$$ROOT"}
                    }
                },
                {
                    "$sort": {"total_spending": -1}
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_time_of_day_patterns: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_recurring_payment_patterns(self, user_id: str) -> Dict[str, Any]:
        """Query 22: Find all recurring payment patterns"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "is_recurring": True
                    }
                },
                {
                    "$group": {
                        "_id": "$merchant_canonical",
                        "total_recurring": {"$sum": "$amount"},
                        "payment_count": {"$sum": 1},
                        "first_payment": {"$min": "$date"},
                        "last_payment": {"$max": "$date"},
                        "avg_amount": {"$avg": "$amount"},
                        "payment_frequency": {"$first": "$subscription_details.subscription_frequency"},
                        "next_payment": {"$first": "$subscription_details.next_renewal_date"}
                    }
                },
                {
                    "$sort": {"total_recurring": -1}
                },
                {
                    "$project": {
                        "merchant": "$_id",
                        "total_recurring": 1,
                        "payment_count": 1,
                        "first_payment": 1,
                        "last_payment": 1,
                        "avg_amount": 1,
                        "payment_frequency": 1,
                        "next_payment": 1,
                        "customer_lifetime_days": {
                            "$ceil": {
                                "$divide": [
                                    {"$subtract": ["$last_payment", "$first_payment"]},
                                    1000 * 60 * 60 * 24
                                ]
                            }
                        },
                        "days_until_next": {
                            "$ceil": {
                                "$divide": [
                                    {"$subtract": ["$next_payment", datetime.now()]},
                                    1000 * 60 * 60 * 24
                                ]
                            }
                        },
                        "monthly_recurring_revenue": {
                            "$cond": [
                                {"$eq": ["$payment_frequency", "monthly"]},
                                "$avg_amount",
                                {"$divide": ["$avg_amount", 12]}
                            ]
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_recurring_payment_patterns: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_merchant_efficiency_analysis(self, user_id: str) -> Dict[str, Any]:
        """Query 23: Show me spending efficiency by merchant category"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": "$service_category",
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "merchants": {"$addToSet": "$merchant_canonical"},
                        "payment_methods": {"$addToSet": "$payment_method"},
                        "subscription_spending": {
                            "$sum": {
                                "$cond": [
                                    {"$eq": ["$is_subscription", True]},
                                    "$amount",
                                    0
                                ]
                            }
                        },
                        "one_time_spending": {
                            "$sum": {
                                "$cond": [
                                    {"$eq": ["$is_subscription", False]},
                                    "$amount",
                                    0
                                ]
                            }
                        }
                    }
                },
                {
                    "$sort": {"total_spending": -1}
                },
                {
                    "$project": {
                        "category": "$_id",
                        "total_spending": 1,
                        "transaction_count": 1,
                        "avg_amount": 1,
                        "unique_merchants": {"$size": "$merchants"},
                        "payment_methods": 1,
                        "subscription_spending": 1,
                        "one_time_spending": 1,
                        "subscription_percentage": {
                            "$multiply": [
                                {"$divide": ["$subscription_spending", "$total_spending"]},
                                100
                            ]
                        },
                        "efficiency_score": {
                            "$add": [
                                {"$multiply": [{"$divide": ["$total_spending", "$transaction_count"]}, 0.4]},
                                {"$multiply": [{"$size": "$merchants"}, 0.3]},
                                {"$multiply": [{"$divide": ["$subscription_spending", "$total_spending"]}, 0.3]}
                            ]
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_merchant_efficiency_analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_bank_transaction_patterns(self, user_id: str) -> Dict[str, Any]:
        """Query 24: Find all bank transaction patterns"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "$or": [
                            {"bank_details.bank_name": {"$exists": True}},
                            {"payment_method": {"$in": ["net_banking", "bank_transfer"]}}
                        ]
                    }
                },
                {
                    "$group": {
                        "_id": "$bank_details.bank_name",
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "max_amount": {"$max": "$amount"},
                        "min_amount": {"$min": "$amount"},
                        "transaction_types": {"$addToSet": "$transaction_type"},
                        "merchants": {"$addToSet": "$merchant_canonical"},
                        "last_transaction": {"$max": "$date"}
                    }
                },
                {
                    "$sort": {"total_spending": -1}
                },
                {
                    "$project": {
                        "bank": "$_id",
                        "total_spending": 1,
                        "transaction_count": 1,
                        "avg_amount": 1,
                        "max_amount": 1,
                        "min_amount": 1,
                        "transaction_types": 1,
                        "merchants": 1,
                        "last_transaction": 1,
                        "days_since_last": {
                            "$ceil": {
                                "$divide": [
                                    {"$subtract": [datetime.now(), "$last_transaction"]},
                                    1000 * 60 * 60 * 24
                                ]
                            }
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_bank_transaction_patterns: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_upi_transaction_analysis(self, user_id: str) -> Dict[str, Any]:
        """Query 25: Show me UPI transaction analysis with receiver patterns"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "payment_method": "upi"
                    }
                },
                {
                    "$group": {
                        "_id": "$upi_details.receiver.upi_id",
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "receiver_name": {"$first": "$upi_details.receiver.name"},
                        "upi_app": {"$first": "$upi_details.receiver.upi_app"},
                        "merchant_canonical": {"$first": "$merchant_canonical"},
                        "categories": {"$addToSet": "$service_category"},
                        "last_transaction": {"$max": "$date"}
                    }
                },
                {
                    "$sort": {"total_spending": -1}
                },
                {
                    "$project": {
                        "upi_id": "$_id",
                        "receiver_name": 1,
                        "upi_app": 1,
                        "merchant_canonical": 1,
                        "total_spending": 1,
                        "transaction_count": 1,
                        "avg_amount": 1,
                        "categories": 1,
                        "last_transaction": 1,
                        "days_since_last": {
                            "$ceil": {
                                "$divide": [
                                    {"$subtract": [datetime.now(), "$last_transaction"]},
                                    1000 * 60 * 60 * 24
                                ]
                            }
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_upi_transaction_analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_credit_card_rewards_analysis(self, user_id: str) -> Dict[str, Any]:
        """Query 26: Find all credit card spending with reward analysis"""
        try:
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "payment_method": "credit_card"
                    }
                },
                {
                    "$group": {
                        "_id": "$card_details.card_network",
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "max_amount": {"$max": "$amount"},
                        "min_amount": {"$min": "$amount"},
                        "merchants": {"$addToSet": "$merchant_canonical"},
                        "categories": {"$addToSet": "$service_category"},
                        "estimated_rewards": {
                            "$sum": {
                                "$multiply": [
                                    "$amount",
                                    {
                                        "$switch": {
                                            "branches": [
                                                {"case": {"$eq": ["$service_category", "food"]}, "then": 0.05},
                                                {"case": {"$eq": ["$service_category", "travel"]}, "then": 0.03},
                                                {"case": {"$eq": ["$service_category", "shopping"]}, "then": 0.02}
                                            ],
                                            "default": 0.01
                                        }
                                    }
                                ]
                            }
                        }
                    }
                },
                {
                    "$sort": {"total_spending": -1}
                },
                {
                    "$project": {
                        "card_network": "$_id",
                        "total_spending": 1,
                        "transaction_count": 1,
                        "avg_amount": 1,
                        "max_amount": 1,
                        "min_amount": 1,
                        "unique_merchants": {"$size": "$merchants"},
                        "categories": 1,
                        "estimated_rewards": 1,
                        "reward_rate": {
                            "$multiply": [
                                {"$divide": ["$estimated_rewards", "$total_spending"]},
                                100
                            ]
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_credit_card_rewards_analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_spending_velocity_analysis(self, user_id: str) -> Dict[str, Any]:
        """Query 27: Show me spending velocity and acceleration patterns"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"},
                            "week": {"$week": "$date"}
                        },
                        "weekly_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"}
                    }
                },
                {
                    "$sort": {"_id.year": 1, "_id.month": 1, "_id.week": 1}
                },
                {
                    "$group": {
                        "_id": {
                            "year": "$_id.year",
                            "month": "$_id.month"
                        },
                        "weeks": {
                            "$push": {
                                "week": "$_id.week",
                                "weekly_spending": "$weekly_spending",
                                "transaction_count": "$transaction_count",
                                "avg_amount": "$avg_amount"
                            }
                        }
                    }
                },
                {
                    "$unwind": {"path": "$weeks", "includeArrayIndex": "weekIndex"}
                },
                {
                    "$project": {
                        "year": "$_id.year",
                        "month": "$_id.month",
                        "week": "$weeks.week",
                        "weekly_spending": "$weeks.weekly_spending",
                        "transaction_count": "$weeks.transaction_count",
                        "avg_amount": "$weeks.avg_amount",
                        "week_index": {"$add": ["$weekIndex", 1]},
                        "spending_velocity": {
                            "$cond": [
                                {"$gt": ["$weekIndex", 0]},
                                {
                                    "$divide": [
                                        {"$subtract": ["$weeks.weekly_spending", {"$arrayElemAt": ["$weeks.weekly_spending", {"$subtract": ["$weekIndex", 1]}]}]},
                                        7
                                    ]
                                },
                                0
                            ]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": "$year",
                            "month": "$month"
                        },
                        "weeks": {"$push": "$$ROOT"},
                        "total_monthly_spending": {"$sum": "$weekly_spending"},
                        "avg_weekly_spending": {"$avg": "$weekly_spending"}
                    }
                },
                {
                    "$unwind": "$weeks"
                },
                {
                    "$project": {
                        "year": "$weeks.year",
                        "month": "$weeks.month",
                        "week": "$weeks.week",
                        "weekly_spending": "$weeks.weekly_spending",
                        "spending_velocity": "$weeks.spending_velocity",
                        "total_monthly_spending": "$total_monthly_spending",
                        "avg_weekly_spending": "$avg_weekly_spending",
                        "velocity_vs_average": {
                            "$subtract": ["$weeks.spending_velocity", {"$divide": ["$avg_weekly_spending", 7]}]
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_spending_velocity_analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_merchant_loyalty_patterns(self, user_id: str) -> Dict[str, Any]:
        """Query 28: Find all merchant loyalty patterns"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": "$merchant_canonical",
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "first_transaction": {"$min": "$date"},
                        "last_transaction": {"$max": "$date"},
                        "categories": {"$addToSet": "$service_category"},
                        "payment_methods": {"$addToSet": "$payment_method"},
                        "subscription_payments": {
                            "$sum": {
                                "$cond": [
                                    {"$eq": ["$is_subscription", True]},
                                    1,
                                    0
                                ]
                            }
                        }
                    }
                },
                {
                    "$sort": {"total_spending": -1}
                },
                {
                    "$project": {
                        "merchant": "$_id",
                        "total_spending": 1,
                        "transaction_count": 1,
                        "avg_amount": 1,
                        "first_transaction": 1,
                        "last_transaction": 1,
                        "categories": 1,
                        "payment_methods": 1,
                        "subscription_payments": 1,
                        "customer_lifetime_days": {
                            "$ceil": {
                                "$divide": [
                                    {"$subtract": ["$last_transaction", "$first_transaction"]},
                                    1000 * 60 * 60 * 24
                                ]
                            }
                        },
                        "days_since_last": {
                            "$ceil": {
                                "$divide": [
                                    {"$subtract": [datetime.now(), "$last_transaction"]},
                                    1000 * 60 * 60 * 24
                                ]
                            }
                        },
                        "loyalty_score": {
                            "$add": [
                                {"$multiply": [{"$divide": ["$transaction_count", 10]}, 30]},
                                {"$multiply": [{"$divide": ["$total_spending", 10000]}, 40]},
                                {"$multiply": [{"$divide": ["$subscription_payments", "$transaction_count"]}, 30]}
                            ]
                        },
                        "frequency_score": {
                            "$divide": [
                                {"$multiply": ["$transaction_count", 30]},
                                {
                                    "$max": [
                                        {"$ceil": {"$divide": [{"$subtract": ["$last_transaction", "$first_transaction"]}, 1000 * 60 * 60 * 24]}},
                                        1
                                    ]
                                }
                            ]
                        }
                    }
                },
                {
                    "$match": {
                        "$or": [
                            {"loyalty_score": {"$gte": 70}},
                            {"frequency_score": {"$gte": 2}}
                        ]
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_merchant_loyalty_patterns: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_seasonality_trends(self, user_id: str) -> Dict[str, Any]:
        """Query 29: Show me spending seasonality and trends"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$date"},
                            "month": {"$month": "$date"}
                        },
                        "total_spending": {"$sum": "$amount"},
                        "transaction_count": {"$sum": 1},
                        "avg_amount": {"$avg": "$amount"},
                        "categories": {"$addToSet": "$service_category"},
                        "merchants": {"$addToSet": "$merchant_canonical"}
                    }
                },
                {
                    "$sort": {"_id.year": 1, "_id.month": 1}
                },
                {
                    "$group": {
                        "_id": "$_id.month",
                        "months": {
                            "$push": {
                                "year": "$_id.year",
                                "total_spending": "$total_spending",
                                "transaction_count": "$transaction_count",
                                "avg_amount": "$avg_amount",
                                "categories": "$categories",
                                "merchants": "$merchants"
                            }
                        }
                    }
                },
                {
                    "$unwind": "$months"
                },
                {
                    "$group": {
                        "_id": {
                            "month": "$_id",
                            "year": "$months.year"
                        },
                        "total_spending": "$months.total_spending",
                        "transaction_count": "$months.transaction_count",
                        "avg_amount": "$months.avg_amount",
                        "categories": "$months.categories",
                        "merchants": "$months.merchants"
                    }
                },
                {
                    "$group": {
                        "_id": "$_id.month",
                        "monthly_data": {
                            "$push": {
                                "year": "$_id.year",
                                "total_spending": "$total_spending",
                                "transaction_count": "$transaction_count",
                                "avg_amount": "$avg_amount"
                            }
                        },
                        "avg_monthly_spending": {"$avg": "$total_spending"},
                        "avg_transaction_count": {"$avg": "$transaction_count"},
                        "avg_transaction_amount": {"$avg": "$avg_amount"}
                    }
                },
                {
                    "$sort": {"_id": 1}
                },
                {
                    "$project": {
                        "month": "$_id",
                        "month_name": {
                            "$switch": {
                                "branches": [
                                    {"case": {"$eq": ["$_id", 1]}, "then": "January"},
                                    {"case": {"$eq": ["$_id", 2]}, "then": "February"},
                                    {"case": {"$eq": ["$_id", 3]}, "then": "March"},
                                    {"case": {"$eq": ["$_id", 4]}, "then": "April"},
                                    {"case": {"$eq": ["$_id", 5]}, "then": "May"},
                                    {"case": {"$eq": ["$_id", 6]}, "then": "June"},
                                    {"case": {"$eq": ["$_id", 7]}, "then": "July"},
                                    {"case": {"$eq": ["$_id", 8]}, "then": "August"},
                                    {"case": {"$eq": ["$_id", 9]}, "then": "September"},
                                    {"case": {"$eq": ["$_id", 10]}, "then": "October"},
                                    {"case": {"$eq": ["$_id", 11]}, "then": "November"},
                                    {"case": {"$eq": ["$_id", 12]}, "then": "December"}
                                ]
                            }
                        },
                        "monthly_data": 1,
                        "avg_monthly_spending": 1,
                        "avg_transaction_count": 1,
                        "avg_transaction_amount": 1,
                        "seasonality_score": {
                            "$divide": [
                                "$avg_monthly_spending",
                                {
                                    "$avg": {
                                        "$map": {
                                            "input": "$monthly_data",
                                            "as": "data",
                                            "in": "$$data.total_spending"
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_seasonality_trends: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_financial_anomalies(self, user_id: str) -> Dict[str, Any]:
        """Query 30: Find all financial anomalies and unusual spending patterns"""
        try:
            pipeline = [
                {
                    "$match": {"user_id": user_id}
                },
                {
                    "$group": {
                        "_id": "$service_category",
                        "transactions": {
                            "$push": {
                                "amount": "$amount",
                                "date": "$date",
                                "merchant": "$merchant_canonical",
                                "payment_method": "$payment_method",
                                "description": "$description"
                            }
                        },
                        "avg_amount": {"$avg": "$amount"},
                        "std_dev": {"$stdDevPop": "$amount"},
                        "min_amount": {"$min": "$amount"},
                        "max_amount": {"$max": "$amount"},
                        "transaction_count": {"$sum": 1}
                    }
                },
                {
                    "$unwind": "$transactions"
                },
                {
                    "$project": {
                        "category": "$_id",
                        "amount": "$transactions.amount",
                        "date": "$transactions.date",
                        "merchant": "$transactions.merchant",
                        "payment_method": "$transactions.payment_method",
                        "description": "$transactions.description",
                        "avg_amount": "$avg_amount",
                        "std_dev": "$std_dev",
                        "min_amount": "$min_amount",
                        "max_amount": "$max_amount",
                        "transaction_count": "$transaction_count",
                        "z_score": {
                            "$divide": [
                                {"$subtract": ["$transactions.amount", "$avg_amount"]},
                                "$std_dev"
                            ]
                        },
                        "is_anomaly": {
                            "$or": [
                                {"$gt": [{"$abs": {"$divide": [{"$subtract": ["$transactions.amount", "$avg_amount"]}, "$std_dev"]}}, 2]},
                                {"$gt": ["$transactions.amount", {"$multiply": ["$avg_amount", 3]}]},
                                {"$lt": ["$transactions.amount", {"$divide": ["$avg_amount", 3]}]}
                            ]
                        }
                    }
                },
                {
                    "$match": {"is_anomaly": True}
                },
                {
                    "$sort": {"z_score": -1}
                },
                {
                    "$group": {
                        "_id": "$category",
                        "anomalies": {
                            "$push": {
                                "amount": "$amount",
                                "date": "$date",
                                "merchant": "$merchant",
                                "payment_method": "$payment_method",
                                "description": "$description",
                                "z_score": "$z_score",
                                "avg_amount": "$avg_amount"
                            }
                        },
                        "anomaly_count": {"$sum": 1},
                        "total_anomaly_amount": {"$sum": "$amount"}
                    }
                },
                {
                    "$sort": {"total_anomaly_amount": -1}
                },
                {
                    "$project": {
                        "category": "$_id",
                        "anomalies": 1,
                        "anomaly_count": 1,
                        "total_anomaly_amount": 1,
                        "avg_anomaly_amount": {"$divide": ["$total_anomaly_amount", "$anomaly_count"]}
                    }
                }
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=None)
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"Error in get_financial_anomalies: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def get_all_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get all analytics for a user in parallel"""
        try:
            tasks = [
                self.get_monthly_spending_trends(user_id),
                self.get_top_merchants_analysis(user_id),
                self.get_category_breakdown_with_percentages(user_id),
                self.get_subscription_analysis(user_id),
                self.get_daily_spending_patterns(user_id),
                self.get_high_value_transactions(user_id),
                self.get_payment_method_breakdown(user_id),
                self.get_refund_analysis(user_id),
                self.get_weekly_spending_patterns(user_id),
                self.get_food_delivery_analysis(user_id),
                self.get_subscription_trend_analysis(user_id),
                self.get_spending_trends_with_growth(user_id),
                self.get_automatic_payments_analysis(user_id),
                self.get_payment_method_security_analysis(user_id),
                self.get_high_value_categories(user_id),
                self.get_time_of_day_patterns(user_id),
                self.get_recurring_payment_patterns(user_id),
                self.get_merchant_efficiency_analysis(user_id),
                self.get_bank_transaction_patterns(user_id),
                self.get_upi_transaction_analysis(user_id),
                self.get_credit_card_rewards_analysis(user_id),
                self.get_merchant_loyalty_patterns(user_id),
                self.get_seasonality_trends(user_id),
                self.get_financial_anomalies(user_id)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            analytics = {}
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error in analytics task {i}: {result}")
                    analytics[f"query_{i+1}"] = {"success": False, "error": str(result)}
                else:
                    analytics[f"query_{i+1}"] = result
            
            return {"success": True, "analytics": analytics}
            
        except Exception as e:
            logger.error(f"Error in get_all_analytics: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_analytics_summary(self, user_id: str) -> Dict[str, Any]:
        """Get a summary of key analytics"""
        try:
            # Get basic stats
            total_transactions = await self.collection.count_documents({"user_id": user_id})
            total_spending = await self.collection.aggregate([
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]).to_list(length=1)
            
            total_spending = total_spending[0]["total"] if total_spending else 0
            
            # Get top categories
            top_categories = await self.collection.aggregate([
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$service_category", "total": {"$sum": "$amount"}}},
                {"$sort": {"total": -1}},
                {"$limit": 5}
            ]).to_list(length=None)
            
            # Get top merchants
            top_merchants = await self.collection.aggregate([
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$merchant_canonical", "total": {"$sum": "$amount"}}},
                {"$sort": {"total": -1}},
                {"$limit": 5}
            ]).to_list(length=None)
            
            return {
                "success": True,
                "summary": {
                    "total_transactions": total_transactions,
                    "total_spending": total_spending,
                    "avg_transaction": total_spending / total_transactions if total_transactions > 0 else 0,
                    "top_categories": top_categories,
                    "top_merchants": top_merchants
                }
            }
            
        except Exception as e:
            logger.error(f"Error in get_analytics_summary: {e}")
            return {"success": False, "error": str(e)} 