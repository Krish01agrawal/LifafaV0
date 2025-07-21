"""
Financial Analytics API
======================

REST API endpoints for financial analytics and aggregation pipelines.
Provides 30 different financial analysis queries.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

from ..services.financial_aggregation_service import FinancialAggregationService
from ..core.dependencies import get_current_user, get_database
from ..models.auth import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Financial Analytics"])

def get_aggregation_service(db=Depends(get_database)) -> FinancialAggregationService:
    """Get financial aggregation service instance."""
    return FinancialAggregationService(db)

# ============================================================================
# BASIC FINANCIAL QUERIES (1-10)
# ============================================================================

@router.get("/monthly-spending-trends")
async def get_monthly_spending_trends(
    months: int = Query(12, description="Number of months to analyze"),
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 1: Show me total spending by month for the last 12 months"""
    try:
        result = await service.get_monthly_spending_trends(current_user.id, months)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in monthly spending trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-merchants")
async def get_top_merchants_analysis(
    limit: int = Query(15, description="Number of top merchants to return"),
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 2: What are my top 15 merchants by total spending?"""
    try:
        result = await service.get_top_merchants_analysis(current_user.id, limit)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in top merchants analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/category-breakdown")
async def get_category_breakdown_with_percentages(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 3: Show me spending breakdown by category with percentages"""
    try:
        result = await service.get_category_breakdown_with_percentages(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in category breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subscriptions")
async def get_subscription_analysis(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 4: Find all my subscription payments with renewal dates"""
    try:
        result = await service.get_subscription_analysis(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in subscription analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/daily-spending-patterns")
async def get_daily_spending_patterns(
    days: int = Query(90, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 5: Show me daily spending for the last 90 days"""
    try:
        result = await service.get_daily_spending_patterns(current_user.id, days)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in daily spending patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/high-value-transactions")
async def get_high_value_transactions(
    min_amount: float = Query(2000, description="Minimum transaction amount"),
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 6: Find all transactions above ₹2000 with details"""
    try:
        result = await service.get_high_value_transactions(current_user.id, min_amount)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in high value transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment-method-breakdown")
async def get_payment_method_breakdown(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 7: Show me UPI vs Card vs Net Banking payment breakdown"""
    try:
        result = await service.get_payment_method_breakdown(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in payment method breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/refunds")
async def get_refund_analysis(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 8: Find all refund transactions with original transaction details"""
    try:
        result = await service.get_refund_analysis(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in refund analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly-spending-patterns")
async def get_weekly_spending_patterns(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 9: Show me spending by day of week with patterns"""
    try:
        result = await service.get_weekly_spending_patterns(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in weekly spending patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/food-delivery-analysis")
async def get_food_delivery_analysis(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 10: Find all food delivery transactions with restaurant analysis"""
    try:
        result = await service.get_food_delivery_analysis(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in food delivery analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ADVANCED FINANCIAL QUERIES (11-20)
# ============================================================================

@router.get("/subscription-trends")
async def get_subscription_trend_analysis(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 11: Show me monthly subscription costs with trend analysis"""
    try:
        result = await service.get_subscription_trend_analysis(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in subscription trend analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/travel-bookings")
async def get_travel_booking_analysis(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 12: Find all travel bookings with cost analysis"""
    try:
        result = await service.get_travel_booking_analysis(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in travel booking analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/spending-trends-with-growth")
async def get_spending_trends_with_growth(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 13: Show me spending trends with month-over-month growth"""
    try:
        result = await service.get_spending_trends_with_growth(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in spending trends with growth: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/automatic-payments")
async def get_automatic_payments_analysis(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 14: Find all automatic payments with renewal analysis"""
    try:
        result = await service.get_automatic_payments_analysis(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in automatic payments analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment-method-security")
async def get_payment_method_security_analysis(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 15: Show me spending by payment method with security analysis"""
    try:
        result = await service.get_payment_method_security_analysis(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in payment method security analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/promotional-emails")
async def get_promotional_emails_analysis(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 16: Find all promotional emails with discount analysis"""
    try:
        result = await service.get_promotional_emails_analysis(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in promotional emails analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/job-applications")
async def get_job_application_status(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 17: Show me job application status with company analysis"""
    try:
        result = await service.get_job_application_status(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in job application status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/date-range-analysis")
async def get_date_range_analysis(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 18: Find all transactions from specific date range with category breakdown"""
    try:
        result = await service.get_date_range_analysis(current_user.id, start_date, end_date)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in date range analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly-comparison")
async def get_monthly_comparison(
    current_month: str = Query(..., description="Current month (YYYY-MM-DD)"),
    previous_month: str = Query(..., description="Previous month (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 19: Show me spending comparison with previous month"""
    try:
        result = await service.get_monthly_comparison(current_user.id, current_month, previous_month)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in monthly comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/high-value-categories")
async def get_high_value_categories(
    min_amount: float = Query(5000, description="Minimum transaction amount"),
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 20: Find all high-value transactions by category with risk analysis"""
    try:
        result = await service.get_high_value_categories(current_user.id, min_amount)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in high value categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# COMPLEX FINANCIAL ANALYTICS (21-30)
# ============================================================================

@router.get("/time-of-day-patterns")
async def get_time_of_day_patterns(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 21: Show me spending patterns by time of day"""
    try:
        result = await service.get_time_of_day_patterns(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in time of day patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recurring-payments")
async def get_recurring_payment_patterns(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 22: Find all recurring payment patterns"""
    try:
        result = await service.get_recurring_payment_patterns(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in recurring payment patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/merchant-efficiency")
async def get_merchant_efficiency_analysis(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 23: Show me spending efficiency by merchant category"""
    try:
        result = await service.get_merchant_efficiency_analysis(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in merchant efficiency analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bank-transactions")
async def get_bank_transaction_patterns(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 24: Find all bank transaction patterns"""
    try:
        result = await service.get_bank_transaction_patterns(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in bank transaction patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upi-analysis")
async def get_upi_transaction_analysis(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 25: Show me UPI transaction analysis with receiver patterns"""
    try:
        result = await service.get_upi_transaction_analysis(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in UPI transaction analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/credit-card-rewards")
async def get_credit_card_rewards_analysis(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 26: Find all credit card spending with reward analysis"""
    try:
        result = await service.get_credit_card_rewards_analysis(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in credit card rewards analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/spending-velocity")
async def get_spending_velocity_analysis(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 27: Show me spending velocity and acceleration patterns"""
    try:
        result = await service.get_spending_velocity_analysis(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in spending velocity analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/merchant-loyalty")
async def get_merchant_loyalty_patterns(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 28: Find all merchant loyalty patterns"""
    try:
        result = await service.get_merchant_loyalty_patterns(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in merchant loyalty patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/seasonality-trends")
async def get_seasonality_trends(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 29: Show me spending seasonality and trends"""
    try:
        result = await service.get_seasonality_trends(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in seasonality trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/financial-anomalies")
async def get_financial_anomalies(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Query 30: Find all financial anomalies and unusual spending patterns"""
    try:
        result = await service.get_financial_anomalies(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in financial anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/all-analytics")
async def get_all_analytics(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Get all analytics for a user in parallel"""
    try:
        result = await service.get_all_analytics(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in all analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    service: FinancialAggregationService = Depends(get_aggregation_service)
) -> Dict[str, Any]:
    """Get a summary of key analytics"""
    try:
        result = await service.get_analytics_summary(current_user.id)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def analytics_health_check() -> Dict[str, Any]:
    """Health check for analytics service"""
    return {
        "status": "healthy",
        "service": "financial_analytics",
        "endpoints": 32,
        "version": "1.0.0"
    } 