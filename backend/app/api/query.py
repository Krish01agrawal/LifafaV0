from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from app.services.database_service import DatabaseService
from app.services.llm_service import llm_service
from app.services.cache_service import cache

logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    user_id: str
    query: str
    include_raw_data: Optional[bool] = False
    max_results: Optional[int] = 50

class QueryResponse(BaseModel):
    user_id: str
    query: str
    response: str
    data_points: List[Dict[str, Any]]
    query_intent: Dict[str, Any]
    response_time_ms: int
    created_at: datetime

class AnalyticsRequest(BaseModel):
    user_id: str
    time_period: str  # "last_month", "last_3_months", "2024-06", etc.
    categories: Optional[List[str]] = None
    metrics: Optional[List[str]] = None

class AnalyticsResponse(BaseModel):
    user_id: str
    time_period: str
    summary: Dict[str, Any]
    breakdowns: List[Dict[str, Any]]
    insights: List[str]
    created_at: datetime

@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Ask a natural language question about email data."""
    try:
        start_time = datetime.utcnow()
        
        logger.info(f"Processing query for user {request.user_id}: {request.query}")
        
        # Check cache first
        cache_key = f"query:{request.user_id}:{hash(request.query)}"
        cached_response = cache.get(cache_key)
        if cached_response:
            logger.info("Returning cached response")
            return QueryResponse(**cached_response)
        
        # Step 1: Understand query intent
        query_intent = await llm_service.understand_query_intent(request.query)
        
        # Step 2: Execute sub-queries
        data_points = await _execute_sub_queries(
            request.user_id, 
            query_intent, 
            request.max_results
        )
        
        # Step 3: Synthesize response
        response = await llm_service.synthesize_response(request.query, data_points)
        
        # Calculate response time
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Create response
        query_response = QueryResponse(
            user_id=request.user_id,
            query=request.query,
            response=response,
            data_points=data_points if request.include_raw_data else [],
            query_intent=query_intent,
            response_time_ms=int(response_time),
            created_at=datetime.utcnow()
        )
        
        # Cache response
        cache.set(cache_key, query_response.dict(), ttl=1800)  # 30 minutes
        
        # Log query
        await _log_query(request.user_id, request.query, query_intent, response_time)
        
        logger.info(f"Query processed successfully in {response_time:.2f}ms")
        
        return query_response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@router.post("/analytics", response_model=AnalyticsResponse)
async def get_analytics(request: AnalyticsRequest):
    """Get comprehensive analytics for a time period."""
    try:
        logger.info(f"Getting analytics for user {request.user_id}, period: {request.time_period}")
        
        # Check cache
        cache_key = f"analytics:{request.user_id}:{request.time_period}"
        cached_analytics = cache.get(cache_key)
        if cached_analytics:
            return AnalyticsResponse(**cached_analytics)
        
        # Get data for the time period
        data = await _get_analytics_data(
            request.user_id, 
            request.time_period, 
            request.categories
        )
        
        # Generate insights
        insights = await _generate_insights(data, request.time_period)
        
        # Create analytics response
        analytics_response = AnalyticsResponse(
            user_id=request.user_id,
            time_period=request.time_period,
            summary=data["summary"],
            breakdowns=data["breakdowns"],
            insights=insights,
            created_at=datetime.utcnow()
        )
        
        # Cache analytics
        cache.set(cache_key, analytics_response.dict(), ttl=3600)  # 1 hour
        
        return analytics_response
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

@router.get("/search/{user_id}")
async def search_transactions(
    user_id: str,
    query: str,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 20
):
    """Search transactions with filters."""
    try:
        db = DatabaseService.get_database()
        
        # Build search filter
        search_filter = {"user_id": user_id}
        
        if category:
            search_filter["service_category"] = category
        
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = datetime.fromisoformat(start_date)
            if end_date:
                date_filter["$lte"] = datetime.fromisoformat(end_date)
            search_filter["transaction_date"] = date_filter
        
        # Text search
        if query:
            search_filter["$text"] = {"$search": query}
        
        # Execute search
        transactions = await db.financial_transactions.find(
            search_filter,
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit).to_list(length=None)
        
        return {
            "user_id": user_id,
            "query": query,
            "results": transactions,
            "total": len(transactions)
        }
        
    except Exception as e:
        logger.error(f"Error searching transactions: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/summary/{user_id}")
async def get_summary(user_id: str, time_period: str = "last_month"):
    """Get quick summary of user's data."""
    try:
        db = DatabaseService.get_database()
        
        # Get summary stats
        total_transactions = await db.financial_transactions.count_documents({"user_id": user_id})
        total_amount = await _get_total_amount(user_id, time_period)
        top_merchants = await _get_top_merchants(user_id, time_period)
        category_breakdown = await _get_category_breakdown(user_id, time_period)
        
        return {
            "user_id": user_id,
            "time_period": time_period,
            "total_transactions": total_transactions,
            "total_amount": total_amount,
            "top_merchants": top_merchants,
            "category_breakdown": category_breakdown
        }
        
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=f"Summary failed: {str(e)}")

async def _execute_sub_queries(user_id: str, query_intent: Dict[str, Any], max_results: int) -> List[Dict[str, Any]]:
    """Execute sub-queries based on query intent."""
    try:
        db = DatabaseService.get_database()
        data_points = []
        
        categories = query_intent.get("categories", ["finance"])
        time_period = query_intent.get("time_period", "all_time")
        
        # Build date filter
        date_filter = _build_date_filter(time_period)
        
        for category in categories:
            if category == "finance":
                # Query financial transactions
                pipeline = [
                    {"$match": {"user_id": user_id}},
                    {"$match": date_filter}
                ]
                
                # Add aggregations based on metrics
                metrics = query_intent.get("metrics", [])
                if "total_amount" in metrics:
                    pipeline.append({
                        "$group": {
                            "_id": None,
                            "total_amount": {"$sum": "$amount"},
                            "transaction_count": {"$sum": 1}
                        }
                    })
                elif "breakdown_by_merchant" in metrics:
                    pipeline.append({
                        "$group": {
                            "_id": "$merchant_canonical",
                            "total_amount": {"$sum": "$amount"},
                            "transaction_count": {"$sum": 1}
                        }
                    })
                    pipeline.append({"$sort": {"total_amount": -1}})
                    pipeline.append({"$limit": max_results})
                else:
                    # Default: get recent transactions
                    pipeline.append({"$sort": {"transaction_date": -1}})
                    pipeline.append({"$limit": max_results})
                
                results = await db.financial_transactions.aggregate(pipeline).to_list(length=None)
                data_points.extend(results)
            
            elif category == "travel":
                # Query travel bookings
                pipeline = [
                    {"$match": {"user_id": user_id}},
                    {"$match": date_filter},
                    {"$sort": {"travel_date": -1}},
                    {"$limit": max_results}
                ]
                
                results = await db.travel_bookings.aggregate(pipeline).to_list(length=None)
                data_points.extend(results)
            
            elif category == "job":
                # Query job communications
                pipeline = [
                    {"$match": {"user_id": user_id}},
                    {"$match": date_filter},
                    {"$sort": {"application_date": -1}},
                    {"$limit": max_results}
                ]
                
                results = await db.job_communications.aggregate(pipeline).to_list(length=None)
                data_points.extend(results)
        
        return data_points
        
    except Exception as e:
        logger.error(f"Error executing sub-queries: {e}")
        return []

def _build_date_filter(time_period: str) -> Dict[str, Any]:
    """Build date filter based on time period."""
    now = datetime.utcnow()
    
    if time_period == "last_month":
        start_date = now.replace(day=1) - timedelta(days=1)
        start_date = start_date.replace(day=1)
    elif time_period == "last_3_months":
        start_date = now - timedelta(days=90)
    elif time_period == "last_6_months":
        start_date = now - timedelta(days=180)
    elif time_period.startswith("2024-"):
        # Specific month
        year, month = time_period.split("-")
        start_date = datetime(int(year), int(month), 1)
        end_date = start_date.replace(month=start_date.month + 1) - timedelta(days=1)
        return {
            "transaction_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
    else:
        # All time
        return {}
    
    return {"transaction_date": {"$gte": start_date}}

async def _get_analytics_data(user_id: str, time_period: str, categories: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get comprehensive analytics data."""
    try:
        db = DatabaseService.get_database()
        date_filter = _build_date_filter(time_period)
        
        if not categories:
            categories = ["finance", "travel", "job"]
        
        summary = {}
        breakdowns = []
        
        for category in categories:
            if category == "finance":
                # Financial summary
                pipeline = [
                    {"$match": {"user_id": user_id}},
                    {"$match": date_filter},
                    {
                        "$group": {
                            "_id": None,
                            "total_amount": {"$sum": "$amount"},
                            "transaction_count": {"$sum": 1},
                            "avg_amount": {"$avg": "$amount"}
                        }
                    }
                ]
                
                result = await db.financial_transactions.aggregate(pipeline).to_list(length=None)
                if result:
                    summary["finance"] = result[0]
                
                # Category breakdown
                category_pipeline = [
                    {"$match": {"user_id": user_id}},
                    {"$match": date_filter},
                    {
                        "$group": {
                            "_id": "$service_category",
                            "total_amount": {"$sum": "$amount"},
                            "transaction_count": {"$sum": 1}
                        }
                    },
                    {"$sort": {"total_amount": -1}}
                ]
                
                category_results = await db.financial_transactions.aggregate(category_pipeline).to_list(length=None)
                breakdowns.append({
                    "category": "finance",
                    "breakdown": category_results
                })
        
        return {
            "summary": summary,
            "breakdowns": breakdowns
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics data: {e}")
        return {"summary": {}, "breakdowns": []}

async def _generate_insights(data: Dict[str, Any], time_period: str) -> List[str]:
    """Generate insights from analytics data."""
    try:
        insights = []
        
        # Generate insights based on data
        if "finance" in data["summary"]:
            finance_data = data["summary"]["finance"]
            
            if finance_data["total_amount"] > 50000:
                insights.append(f"High spending detected: ₹{finance_data['total_amount']:,.2f} in {time_period}")
            
            if finance_data["avg_amount"] > 2000:
                insights.append(f"Average transaction amount is ₹{finance_data['avg_amount']:,.2f}")
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return []

async def _log_query(user_id: str, query: str, intent: Dict[str, Any], response_time: float):
    """Log query for analytics."""
    try:
        db = DatabaseService.get_database()
        
        await db.query_logs.insert_one({
            "user_id": user_id,
            "query_text": query,
            "intent_json": intent,
            "response_time_ms": response_time,
            "created_at": datetime.utcnow()
        })
        
    except Exception as e:
        logger.error(f"Error logging query: {e}")

async def _get_total_amount(user_id: str, time_period: str) -> float:
    """Get total amount for time period."""
    try:
        db = DatabaseService.get_database()
        date_filter = _build_date_filter(time_period)
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$match": date_filter},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        
        result = await db.financial_transactions.aggregate(pipeline).to_list(length=None)
        return result[0]["total"] if result else 0.0
        
    except Exception as e:
        logger.error(f"Error getting total amount: {e}")
        return 0.0

async def _get_top_merchants(user_id: str, time_period: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get top merchants by spending."""
    try:
        db = DatabaseService.get_database()
        date_filter = _build_date_filter(time_period)
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$match": date_filter},
            {
                "$group": {
                    "_id": "$merchant_canonical",
                    "total_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1}
                }
            },
            {"$sort": {"total_amount": -1}},
            {"$limit": limit}
        ]
        
        return await db.financial_transactions.aggregate(pipeline).to_list(length=None)
        
    except Exception as e:
        logger.error(f"Error getting top merchants: {e}")
        return []

async def _get_category_breakdown(user_id: str, time_period: str) -> List[Dict[str, Any]]:
    """Get spending breakdown by category."""
    try:
        db = DatabaseService.get_database()
        date_filter = _build_date_filter(time_period)
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$match": date_filter},
            {
                "$group": {
                    "_id": "$service_category",
                    "total_amount": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1}
                }
            },
            {"$sort": {"total_amount": -1}}
        ]
        
        return await db.financial_transactions.aggregate(pipeline).to_list(length=None)
        
    except Exception as e:
        logger.error(f"Error getting category breakdown: {e}")
        return [] 