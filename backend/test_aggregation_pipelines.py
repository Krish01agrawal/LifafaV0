#!/usr/bin/env python3
"""
Test Script for Financial Aggregation Pipelines
===============================================

This script tests all 30 aggregation pipelines with sample data to ensure
they work correctly and return expected results.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.financial_aggregation_service import FinancialAggregationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AggregationPipelineTester:
    """Test class for financial aggregation pipelines."""
    
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017"):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client.pluto_money
        self.service = FinancialAggregationService(self.db)
        self.test_user_id = "test_user_123"
    
    async def setup_test_data(self):
        """Create sample test data for all collections."""
        logger.info("Setting up test data...")
        
        # Clear existing test data
        await self.db.financial_transactions.delete_many({"user_id": self.test_user_id})
        await self.db.travel_bookings.delete_many({"user_id": self.test_user_id})
        await self.db.promotional_emails.delete_many({"user_id": self.test_user_id})
        await self.db.job_communications.delete_many({"user_id": self.test_user_id})
        
        # Create sample financial transactions
        transactions = []
        base_date = datetime.now() - timedelta(days=365)
        
        # Sample transaction data
        sample_transactions = [
            # Food delivery transactions
            {"merchant": "Swiggy", "category": "food", "amount": 500, "payment_method": "upi"},
            {"merchant": "Zomato", "category": "food", "amount": 800, "payment_method": "credit_card"},
            {"merchant": "Swiggy", "category": "food", "amount": 600, "payment_method": "upi"},
            
            # Subscription transactions
            {"merchant": "Netflix", "category": "entertainment", "amount": 999, "payment_method": "credit_card", "is_subscription": True},
            {"merchant": "Spotify", "category": "entertainment", "amount": 199, "payment_method": "debit_card", "is_subscription": True},
            {"merchant": "Amazon Prime", "category": "entertainment", "amount": 1499, "payment_method": "credit_card", "is_subscription": True},
            
            # Travel transactions
            {"merchant": "MakeMyTrip", "category": "travel", "amount": 15000, "payment_method": "credit_card"},
            {"merchant": "IRCTC", "category": "travel", "amount": 2500, "payment_method": "net_banking"},
            {"merchant": "Uber", "category": "transport", "amount": 300, "payment_method": "upi"},
            
            # Shopping transactions
            {"merchant": "Amazon", "category": "shopping", "amount": 2500, "payment_method": "credit_card"},
            {"merchant": "Flipkart", "category": "shopping", "amount": 1800, "payment_method": "upi"},
            {"merchant": "Myntra", "category": "shopping", "amount": 1200, "payment_method": "debit_card"},
            
            # High value transactions
            {"merchant": "Apple Store", "category": "electronics", "amount": 85000, "payment_method": "credit_card"},
            {"merchant": "Samsung", "category": "electronics", "amount": 45000, "payment_method": "net_banking"},
            
            # Refund transactions
            {"merchant": "Amazon", "category": "shopping", "amount": -1200, "payment_method": "credit_card", "transaction_type": "refund"},
        ]
        
        for i, sample in enumerate(sample_transactions):
            transaction_date = base_date + timedelta(days=i*3)
            transaction = {
                "_id": ObjectId(),
                "user_id": self.test_user_id,
                "date": transaction_date,
                "amount": sample["amount"],
                "merchant_canonical": sample["merchant"],
                "service_category": sample["category"],
                "payment_method": sample["payment_method"],
                "transaction_type": sample.get("transaction_type", "purchase"),
                "is_subscription": sample.get("is_subscription", False),
                "is_automatic_payment": sample.get("is_subscription", False),
                "is_recurring": sample.get("is_subscription", False),
                "description": f"Payment to {sample['merchant']}",
                "upi_details": {
                    "receiver": {
                        "upi_id": f"{sample['merchant'].lower()}@upi",
                        "name": sample["merchant"],
                        "upi_app": "gpay"
                    }
                } if sample["payment_method"] == "upi" else None,
                "bank_details": {
                    "bank_name": "HDFC Bank"
                } if sample["payment_method"] == "net_banking" else None,
                "card_details": {
                    "card_network": "visa"
                } if sample["payment_method"] == "credit_card" else None,
                "subscription_details": {
                    "next_renewal_date": transaction_date + timedelta(days=30),
                    "subscription_frequency": "monthly"
                } if sample.get("is_subscription") else None,
                "subscription_product": f"{sample['merchant']} Premium" if sample.get("is_subscription") else None,
                "transaction_reference": f"TXN_{i:06d}"
            }
            transactions.append(transaction)
        
        # Insert transactions
        if transactions:
            await self.db.financial_transactions.insert_many(transactions)
            logger.info(f"Inserted {len(transactions)} financial transactions")
        
        # Create sample travel bookings
        travel_bookings = [
            {
                "user_id": self.test_user_id,
                "booking_type": "flight",
                "total_amount": 15000,
                "service_provider": "MakeMyTrip",
                "to_location": {"city": "Mumbai"}
            },
            {
                "user_id": self.test_user_id,
                "booking_type": "hotel",
                "total_amount": 8000,
                "service_provider": "Booking.com",
                "to_location": {"city": "Delhi"}
            }
        ]
        
        await self.db.travel_bookings.insert_many(travel_bookings)
        logger.info(f"Inserted {len(travel_bookings)} travel bookings")
        
        # Create sample promotional emails
        promotional_emails = [
            {
                "user_id": self.test_user_id,
                "merchant_canonical": "Amazon",
                "discount_amount": 500,
                "valid_until": datetime.now() + timedelta(days=7),
                "promotion_type": "discount"
            },
            {
                "user_id": self.test_user_id,
                "merchant_canonical": "Flipkart",
                "discount_amount": 300,
                "valid_until": datetime.now() - timedelta(days=1),
                "promotion_type": "cashback"
            }
        ]
        
        await self.db.promotional_emails.insert_many(promotional_emails)
        logger.info(f"Inserted {len(promotional_emails)} promotional emails")
        
        # Create sample job communications
        job_communications = [
            {
                "user_id": self.test_user_id,
                "application_status": "applied",
                "company_name": "Google",
                "salary_offered": 2500000,
                "updated_at": datetime.now() - timedelta(days=5)
            },
            {
                "user_id": self.test_user_id,
                "application_status": "interview",
                "company_name": "Microsoft",
                "salary_offered": 2000000,
                "updated_at": datetime.now() - timedelta(days=2)
            }
        ]
        
        await self.db.job_communications.insert_many(job_communications)
        logger.info(f"Inserted {len(job_communications)} job communications")
        
        logger.info("Test data setup completed!")
    
    async def test_basic_queries(self):
        """Test basic financial queries (1-10)."""
        logger.info("Testing basic financial queries...")
        
        tests = [
            ("Monthly Spending Trends", self.service.get_monthly_spending_trends),
            ("Top Merchants Analysis", self.service.get_top_merchants_analysis),
            ("Category Breakdown", self.service.get_category_breakdown_with_percentages),
            ("Subscription Analysis", self.service.get_subscription_analysis),
            ("Daily Spending Patterns", self.service.get_daily_spending_patterns),
            ("High Value Transactions", self.service.get_high_value_transactions),
            ("Payment Method Breakdown", self.service.get_payment_method_breakdown),
            ("Refund Analysis", self.service.get_refund_analysis),
            ("Weekly Spending Patterns", self.service.get_weekly_spending_patterns),
            ("Food Delivery Analysis", self.service.get_food_delivery_analysis),
        ]
        
        for test_name, test_func in tests:
            try:
                result = await test_func(self.test_user_id)
                if result["success"]:
                    logger.info(f"✅ {test_name}: PASSED")
                    logger.debug(f"   Data points: {len(result.get('data', []))}")
                else:
                    logger.error(f"❌ {test_name}: FAILED - {result.get('error')}")
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {str(e)}")
    
    async def test_advanced_queries(self):
        """Test advanced financial queries (11-20)."""
        logger.info("Testing advanced financial queries...")
        
        tests = [
            ("Subscription Trends", self.service.get_subscription_trend_analysis),
            ("Travel Bookings", self.service.get_travel_booking_analysis),
            ("Spending Trends with Growth", self.service.get_spending_trends_with_growth),
            ("Automatic Payments", self.service.get_automatic_payments_analysis),
            ("Payment Method Security", self.service.get_payment_method_security_analysis),
            ("Promotional Emails", self.service.get_promotional_emails_analysis),
            ("Job Applications", self.service.get_job_application_status),
            ("Date Range Analysis", lambda uid: self.service.get_date_range_analysis(uid, "2024-01-01", "2024-12-31")),
            ("Monthly Comparison", lambda uid: self.service.get_monthly_comparison(uid, "2024-02-01", "2024-01-01")),
            ("High Value Categories", self.service.get_high_value_categories),
        ]
        
        for test_name, test_func in tests:
            try:
                result = await test_func(self.test_user_id)
                if result["success"]:
                    logger.info(f"✅ {test_name}: PASSED")
                    logger.debug(f"   Data points: {len(result.get('data', []))}")
                else:
                    logger.error(f"❌ {test_name}: FAILED - {result.get('error')}")
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {str(e)}")
    
    async def test_complex_analytics(self):
        """Test complex financial analytics (21-30)."""
        logger.info("Testing complex financial analytics...")
        
        tests = [
            ("Time of Day Patterns", self.service.get_time_of_day_patterns),
            ("Recurring Payments", self.service.get_recurring_payment_patterns),
            ("Merchant Efficiency", self.service.get_merchant_efficiency_analysis),
            ("Bank Transactions", self.service.get_bank_transaction_patterns),
            ("UPI Analysis", self.service.get_upi_transaction_analysis),
            ("Credit Card Rewards", self.service.get_credit_card_rewards_analysis),
            ("Spending Velocity", self.service.get_spending_velocity_analysis),
            ("Merchant Loyalty", self.service.get_merchant_loyalty_patterns),
            ("Seasonality Trends", self.service.get_seasonality_trends),
            ("Financial Anomalies", self.service.get_financial_anomalies),
        ]
        
        for test_name, test_func in tests:
            try:
                result = await test_func(self.test_user_id)
                if result["success"]:
                    logger.info(f"✅ {test_name}: PASSED")
                    logger.debug(f"   Data points: {len(result.get('data', []))}")
                else:
                    logger.error(f"❌ {test_name}: FAILED - {result.get('error')}")
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {str(e)}")
    
    async def test_utility_methods(self):
        """Test utility methods."""
        logger.info("Testing utility methods...")
        
        tests = [
            ("All Analytics", self.service.get_all_analytics),
            ("Analytics Summary", self.service.get_analytics_summary),
        ]
        
        for test_name, test_func in tests:
            try:
                result = await test_func(self.test_user_id)
                if result["success"]:
                    logger.info(f"✅ {test_name}: PASSED")
                    if test_name == "All Analytics":
                        analytics_count = len(result.get('analytics', {}))
                        logger.info(f"   Analytics returned: {analytics_count}")
                    elif test_name == "Analytics Summary":
                        summary = result.get('summary', {})
                        logger.info(f"   Total transactions: {summary.get('total_transactions', 0)}")
                        logger.info(f"   Total spending: {summary.get('total_spending', 0)}")
                else:
                    logger.error(f"❌ {test_name}: FAILED - {result.get('error')}")
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {str(e)}")
    
    async def run_all_tests(self):
        """Run all tests."""
        logger.info("=" * 60)
        logger.info("STARTING AGGREGATION PIPELINE TESTS")
        logger.info("=" * 60)
        
        try:
            # Setup test data
            await self.setup_test_data()
            
            # Run tests
            await self.test_basic_queries()
            await self.test_advanced_queries()
            await self.test_complex_analytics()
            await self.test_utility_methods()
            
            logger.info("=" * 60)
            logger.info("ALL TESTS COMPLETED")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}")
        finally:
            # Cleanup
            await self.client.close()
    
    async def cleanup_test_data(self):
        """Clean up test data."""
        logger.info("Cleaning up test data...")
        
        await self.db.financial_transactions.delete_many({"user_id": self.test_user_id})
        await self.db.travel_bookings.delete_many({"user_id": self.test_user_id})
        await self.db.promotional_emails.delete_many({"user_id": self.test_user_id})
        await self.db.job_communications.delete_many({"user_id": self.test_user_id})
        
        logger.info("Test data cleanup completed!")

async def main():
    """Main function to run the tests."""
    # You can change the MongoDB URI here
    mongo_uri = "mongodb://localhost:27017"
    
    tester = AggregationPipelineTester(mongo_uri)
    
    try:
        await tester.run_all_tests()
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        await tester.cleanup_test_data()

if __name__ == "__main__":
    asyncio.run(main()) 