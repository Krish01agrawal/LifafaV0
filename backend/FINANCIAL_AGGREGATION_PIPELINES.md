# 🚀 **Financial Aggregation Pipelines Documentation**

## **Overview**

This document provides comprehensive documentation for **30 MongoDB aggregation pipelines** implemented in the Pluto Money platform. These pipelines transform raw financial transaction data into actionable insights and analytics.

## **📊 Pipeline Categories**

### **1. Basic Financial Queries (1-10)**
- Monthly spending trends
- Top merchants analysis
- Category breakdowns
- Subscription analysis
- Daily/Weekly patterns

### **2. Advanced Financial Queries (11-20)**
- Subscription trends
- Travel bookings
- Spending growth analysis
- Automatic payments
- Security analysis

### **3. Complex Financial Analytics (21-30)**
- Time-of-day patterns
- Recurring payments
- Merchant efficiency
- Bank transactions
- UPI analysis
- Credit card rewards
- Spending velocity
- Merchant loyalty
- Seasonality trends
- Financial anomalies

---

## **🔧 API Endpoints**

### **Base URL**: `/analytics`

### **Basic Financial Queries**

#### **1. Monthly Spending Trends**
```http
GET /analytics/monthly-spending-trends?months=12
```
**Purpose**: Show total spending by month for the last 12 months
**Parameters**:
- `months` (int): Number of months to analyze (default: 12)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "month": "2024-01",
      "total_spending": 45000,
      "transaction_count": 45,
      "avg_amount": 1000,
      "max_amount": 5000,
      "min_amount": 50
    }
  ]
}
```

#### **2. Top Merchants Analysis**
```http
GET /analytics/top-merchants?limit=15
```
**Purpose**: Find top merchants by total spending
**Parameters**:
- `limit` (int): Number of merchants to return (default: 15)

#### **3. Category Breakdown**
```http
GET /analytics/category-breakdown
```
**Purpose**: Show spending breakdown by category with percentages

#### **4. Subscription Analysis**
```http
GET /analytics/subscriptions
```
**Purpose**: Find all subscription payments with renewal dates

#### **5. Daily Spending Patterns**
```http
GET /analytics/daily-spending-patterns?days=90
```
**Purpose**: Show daily spending for the last 90 days

#### **6. High Value Transactions**
```http
GET /analytics/high-value-transactions?min_amount=2000
```
**Purpose**: Find all transactions above specified amount

#### **7. Payment Method Breakdown**
```http
GET /analytics/payment-method-breakdown
```
**Purpose**: Show UPI vs Card vs Net Banking breakdown

#### **8. Refund Analysis**
```http
GET /analytics/refunds
```
**Purpose**: Find all refund transactions with original details

#### **9. Weekly Spending Patterns**
```http
GET /analytics/weekly-spending-patterns
```
**Purpose**: Show spending by day of week

#### **10. Food Delivery Analysis**
```http
GET /analytics/food-delivery-analysis
```
**Purpose**: Find all food delivery transactions with restaurant analysis

### **Advanced Financial Queries**

#### **11. Subscription Trends**
```http
GET /analytics/subscription-trends
```
**Purpose**: Show monthly subscription costs with trend analysis

#### **12. Travel Bookings**
```http
GET /analytics/travel-bookings
```
**Purpose**: Find all travel bookings with cost analysis

#### **13. Spending Trends with Growth**
```http
GET /analytics/spending-trends-with-growth
```
**Purpose**: Show spending trends with month-over-month growth

#### **14. Automatic Payments**
```http
GET /analytics/automatic-payments
```
**Purpose**: Find all automatic payments with renewal analysis

#### **15. Payment Method Security**
```http
GET /analytics/payment-method-security
```
**Purpose**: Show spending by payment method with security analysis

#### **16. Promotional Emails**
```http
GET /analytics/promotional-emails
```
**Purpose**: Find all promotional emails with discount analysis

#### **17. Job Applications**
```http
GET /analytics/job-applications
```
**Purpose**: Show job application status with company analysis

#### **18. Date Range Analysis**
```http
GET /analytics/date-range-analysis?start_date=2024-01-01&end_date=2024-12-31
```
**Purpose**: Find all transactions from specific date range

#### **19. Monthly Comparison**
```http
GET /analytics/monthly-comparison?current_month=2024-02-01&previous_month=2024-01-01
```
**Purpose**: Show spending comparison with previous month

#### **20. High Value Categories**
```http
GET /analytics/high-value-categories?min_amount=5000
```
**Purpose**: Find high-value transactions by category with risk analysis

### **Complex Financial Analytics**

#### **21. Time of Day Patterns**
```http
GET /analytics/time-of-day-patterns
```
**Purpose**: Show spending patterns by time of day

#### **22. Recurring Payments**
```http
GET /analytics/recurring-payments
```
**Purpose**: Find all recurring payment patterns

#### **23. Merchant Efficiency**
```http
GET /analytics/merchant-efficiency
```
**Purpose**: Show spending efficiency by merchant category

#### **24. Bank Transactions**
```http
GET /analytics/bank-transactions
```
**Purpose**: Find all bank transaction patterns

#### **25. UPI Analysis**
```http
GET /analytics/upi-analysis
```
**Purpose**: Show UPI transaction analysis with receiver patterns

#### **26. Credit Card Rewards**
```http
GET /analytics/credit-card-rewards
```
**Purpose**: Find all credit card spending with reward analysis

#### **27. Spending Velocity**
```http
GET /analytics/spending-velocity
```
**Purpose**: Show spending velocity and acceleration patterns

#### **28. Merchant Loyalty**
```http
GET /analytics/merchant-loyalty
```
**Purpose**: Find all merchant loyalty patterns

#### **29. Seasonality Trends**
```http
GET /analytics/seasonality-trends
```
**Purpose**: Show spending seasonality and trends

#### **30. Financial Anomalies**
```http
GET /analytics/financial-anomalies
```
**Purpose**: Find all financial anomalies and unusual spending patterns

### **Utility Endpoints**

#### **All Analytics**
```http
GET /analytics/all-analytics
```
**Purpose**: Get all analytics for a user in parallel

#### **Analytics Summary**
```http
GET /analytics/summary
```
**Purpose**: Get a summary of key analytics

#### **Health Check**
```http
GET /analytics/health
```
**Purpose**: Health check for analytics service

---

## **📈 MongoDB Aggregation Pipeline Examples**

### **Example 1: Monthly Spending Trends**
```javascript
db.financial_transactions.aggregate([
  {
    "$match": {
      "user_id": "user_123",
      "date": {
        "$gte": new Date("2024-01-01"),
        "$lte": new Date("2024-12-31")
      }
    }
  },
  {
    "$group": {
      "_id": {
        "year": { "$year": "$date" },
        "month": { "$month": "$date" }
      },
      "total_spending": { "$sum": "$amount" },
      "transaction_count": { "$sum": 1 },
      "avg_amount": { "$avg": "$amount" },
      "max_amount": { "$max": "$amount" },
      "min_amount": { "$min": "$amount" }
    }
  },
  {
    "$sort": { "_id.year": 1, "_id.month": 1 }
  }
])
```

### **Example 2: Top Merchants Analysis**
```javascript
db.financial_transactions.aggregate([
  {
    "$match": { "user_id": "user_123" }
  },
  {
    "$group": {
      "_id": "$merchant_canonical",
      "total_spending": { "$sum": "$amount" },
      "transaction_count": { "$sum": 1 },
      "avg_amount": { "$avg": "$amount" },
      "last_transaction": { "$max": "$date" },
      "first_transaction": { "$min": "$date" }
    }
  },
  {
    "$sort": { "total_spending": -1 }
  },
  {
    "$limit": 15
  }
])
```

### **Example 3: Category Breakdown with Percentages**
```javascript
db.financial_transactions.aggregate([
  {
    "$match": { "user_id": "user_123" }
  },
  {
    "$group": {
      "_id": "$service_category",
      "total_spending": { "$sum": "$amount" },
      "transaction_count": { "$sum": 1 }
    }
  },
  {
    "$group": {
      "_id": null,
      "categories": { "$push": "$$ROOT" },
      "grand_total": { "$sum": "$total_spending" }
    }
  },
  {
    "$unwind": "$categories"
  },
  {
    "$project": {
      "category": "$categories._id",
      "total_spending": "$categories.total_spending",
      "percentage": {
        "$multiply": [
          { "$divide": ["$categories.total_spending", "$grand_total"] },
          100
        ]
      }
    }
  }
])
```

---

## **🔍 Data Schema Requirements**

### **Financial Transactions Collection**
```javascript
{
  "_id": ObjectId,
  "user_id": "string",
  "date": Date,
  "amount": Number,
  "merchant_canonical": "string",
  "service_category": "string",
  "payment_method": "string",
  "transaction_type": "string",
  "is_subscription": Boolean,
  "is_automatic_payment": Boolean,
  "is_recurring": Boolean,
  "description": "string",
  "upi_details": {
    "receiver": {
      "upi_id": "string",
      "name": "string",
      "upi_app": "string"
    }
  },
  "bank_details": {
    "bank_name": "string"
  },
  "card_details": {
    "card_network": "string"
  },
  "subscription_details": {
    "next_renewal_date": Date,
    "subscription_frequency": "string"
  },
  "subscription_product": "string",
  "transaction_reference": "string"
}
```

### **Travel Bookings Collection**
```javascript
{
  "_id": ObjectId,
  "user_id": "string",
  "booking_type": "string",
  "total_amount": Number,
  "service_provider": "string",
  "to_location": {
    "city": "string"
  }
}
```

### **Promotional Emails Collection**
```javascript
{
  "_id": ObjectId,
  "user_id": "string",
  "merchant_canonical": "string",
  "discount_amount": Number,
  "valid_until": Date,
  "promotion_type": "string"
}
```

### **Job Communications Collection**
```javascript
{
  "_id": ObjectId,
  "user_id": "string",
  "application_status": "string",
  "company_name": "string",
  "salary_offered": Number,
  "updated_at": Date
}
```

---

## **⚡ Performance Optimization**

### **Indexes Required**
```javascript
// Financial transactions indexes
db.financial_transactions.createIndex({ "user_id": 1, "date": -1 })
db.financial_transactions.createIndex({ "user_id": 1, "merchant_canonical": 1 })
db.financial_transactions.createIndex({ "user_id": 1, "service_category": 1 })
db.financial_transactions.createIndex({ "user_id": 1, "payment_method": 1 })
db.financial_transactions.createIndex({ "user_id": 1, "amount": -1 })
db.financial_transactions.createIndex({ "user_id": 1, "is_subscription": 1 })

// Other collections
db.travel_bookings.createIndex({ "user_id": 1, "booking_type": 1 })
db.promotional_emails.createIndex({ "user_id": 1, "valid_until": 1 })
db.job_communications.createIndex({ "user_id": 1, "application_status": 1 })
```

### **Query Optimization Tips**
1. **Use compound indexes** for frequently queried combinations
2. **Limit aggregation stages** to essential operations
3. **Use `$match` early** to reduce document count
4. **Project only needed fields** to reduce memory usage
5. **Use `$limit`** for large result sets

---

## **🚀 Usage Examples**

### **Python Client Example**
```python
import aiohttp
import asyncio

async def get_financial_analytics():
    async with aiohttp.ClientSession() as session:
        # Get monthly spending trends
        async with session.get(
            "http://localhost:8000/analytics/monthly-spending-trends",
            headers={"Authorization": "Bearer YOUR_TOKEN"}
        ) as response:
            monthly_data = await response.json()
            print("Monthly spending:", monthly_data)
        
        # Get top merchants
        async with session.get(
            "http://localhost:8000/analytics/top-merchants?limit=10",
            headers={"Authorization": "Bearer YOUR_TOKEN"}
        ) as response:
            merchants_data = await response.json()
            print("Top merchants:", merchants_data)

# Run the example
asyncio.run(get_financial_analytics())
```

### **JavaScript/Node.js Example**
```javascript
const axios = require('axios');

async function getFinancialAnalytics() {
  const token = 'YOUR_JWT_TOKEN';
  const baseURL = 'http://localhost:8000/analytics';
  
  try {
    // Get all analytics in parallel
    const [monthlyTrends, topMerchants, categoryBreakdown] = await Promise.all([
      axios.get(`${baseURL}/monthly-spending-trends`, {
        headers: { Authorization: `Bearer ${token}` }
      }),
      axios.get(`${baseURL}/top-merchants?limit=10`, {
        headers: { Authorization: `Bearer ${token}` }
      }),
      axios.get(`${baseURL}/category-breakdown`, {
        headers: { Authorization: `Bearer ${token}` }
      })
    ]);
    
    console.log('Monthly trends:', monthlyTrends.data);
    console.log('Top merchants:', topMerchants.data);
    console.log('Category breakdown:', categoryBreakdown.data);
    
  } catch (error) {
    console.error('Error fetching analytics:', error);
  }
}

getFinancialAnalytics();
```

### **cURL Examples**
```bash
# Get monthly spending trends
curl -X GET "http://localhost:8000/analytics/monthly-spending-trends?months=6" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get top merchants
curl -X GET "http://localhost:8000/analytics/top-merchants?limit=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get all analytics
curl -X GET "http://localhost:8000/analytics/all-analytics" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## **📊 Business Intelligence Use Cases**

### **1. Personal Finance Management**
- Track monthly spending trends
- Identify top spending categories
- Monitor subscription costs
- Analyze payment method usage

### **2. Budget Planning**
- Category-wise spending breakdown
- Monthly comparison analysis
- Seasonal spending patterns
- High-value transaction alerts

### **3. Investment Insights**
- Spending velocity analysis
- Merchant loyalty patterns
- Credit card reward optimization
- Financial anomaly detection

### **4. Risk Management**
- Unusual spending patterns
- High-value transaction monitoring
- Payment method security analysis
- Subscription cost tracking

### **5. Business Intelligence**
- Customer spending behavior
- Merchant performance analysis
- Payment method preferences
- Seasonal trend analysis

---

## **🔧 Implementation Notes**

### **Service Architecture**
- **Service Layer**: `FinancialAggregationService`
- **API Layer**: `financial_analytics.py`
- **Database**: MongoDB with aggregation pipelines
- **Authentication**: JWT-based user authentication
- **Error Handling**: Comprehensive error handling and logging

### **Performance Considerations**
- **Parallel Processing**: Use `asyncio.gather()` for multiple queries
- **Caching**: Implement Redis caching for frequently accessed data
- **Pagination**: Add pagination for large result sets
- **Rate Limiting**: Implement rate limiting for API endpoints

### **Monitoring & Logging**
- **Query Performance**: Monitor aggregation pipeline execution times
- **Error Tracking**: Log all aggregation errors with context
- **Usage Analytics**: Track API endpoint usage patterns
- **Data Quality**: Monitor data completeness and accuracy

---

## **🎯 Next Steps**

### **Immediate Enhancements**
1. **Add caching layer** for frequently accessed analytics
2. **Implement pagination** for large result sets
3. **Add data validation** for input parameters
4. **Create dashboard endpoints** for frontend integration

### **Future Features**
1. **Real-time analytics** with WebSocket support
2. **Predictive analytics** using machine learning
3. **Custom aggregation pipelines** for specific business needs
4. **Export functionality** for analytics data
5. **Alert system** for financial anomalies

### **Integration Points**
1. **Frontend Dashboard**: React/Vue.js integration
2. **Mobile App**: REST API consumption
3. **Third-party Tools**: BI tool integration
4. **Webhooks**: Real-time notifications

---

## **📞 Support & Documentation**

For questions, issues, or feature requests:
- **GitHub Issues**: Create issues in the repository
- **Documentation**: Refer to this document and API docs
- **Code Examples**: Check the `/examples` directory
- **Testing**: Use the provided test scripts

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Maintainer**: Pluto Money Development Team 