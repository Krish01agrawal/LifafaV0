# Enhanced Email Processing System

## Overview

The Enhanced Email Processing System is a comprehensive solution for processing, categorizing, and extracting structured data from Gmail emails. It implements a sophisticated multi-layered architecture with specialized collections for different types of email data.

## 🏗️ System Architecture

### Database Collections

The system uses **15 specialized MongoDB collections** for optimal data organization and query performance:

#### Core Collections
- **`users`** - User accounts and authentication data
- **`user_sessions`** - User session management and security
- **`email_logs`** - Raw email data from Gmail sync
- **`emails`** - Processed and filtered email data
- **`categorized_emails`** - Categorized email data with metadata

#### Specialized Data Collections
- **`financial_transactions`** - Comprehensive financial transaction data
- **`subscriptions`** - Subscription tracking and management
- **`travel_bookings`** - Travel booking and itinerary data
- **`job_communications`** - Job-related communications and applications
- **`promotional_emails`** - Promotional offers and marketing data

#### System Collections
- **`email_queue`** - Email processing queue management
- **`extraction_failures`** - Failed extraction tracking and retry
- **`query_logs`** - Query analytics and performance tracking
- **`user_analytics`** - User analytics and insights
- **`chats`** - Chat conversation data

## 📊 Data Models

### Enhanced Pydantic Models

The system uses comprehensive Pydantic models with detailed schemas:

#### User Models
```python
class User(BaseModel):
    user_id: str
    email: str
    name: Optional[str]
    preferences: UserPreferences
    sync_status: SyncStatus
    categorization_status: CategorizationStatus
    # ... comprehensive user data
```

#### Email Models
```python
class EmailLog(BaseModel):
    id: str
    user_id: str
    gmail_id: str
    subject: str
    from_: str
    body: Optional[str]
    received_date: datetime
    importance_score: float
    financial: bool
    # ... comprehensive email data
```

#### Financial Transaction Models
```python
class FinancialTransaction(BaseModel):
    id: str
    user_id: str
    amount: float
    currency: str
    merchant: str
    merchant_canonical: str
    payment_method: PaymentMethod
    transaction_type: TransactionType
    upi_details: UPIDetails
    bank_details: BankDetails
    subscription_details: SubscriptionDetails
    # ... comprehensive financial data
```

## 🎯 Email Categorization System

### Primary Categories (20 categories)

1. **finance** - Bills, payments, transactions, banking, credit cards, loans, investments, UPI transactions, bank alerts
2. **travel** - Flights, hotels, bookings, transportation, vacation packages, travel insurance, car rentals
3. **job** - Job applications, interviews, work communications, career opportunities, recruitment, HR updates
4. **promotion** - Offers, discounts, marketing emails, sales, deals, coupons, cashback, referral programs
5. **subscription** - Service subscriptions, renewals, memberships, streaming services, software licenses, cloud services
6. **shopping** - Online purchases, order confirmations, delivery updates, e-commerce, retail, marketplace
7. **social** - Social media notifications, friend requests, community updates, Reddit, LinkedIn, Facebook
8. **health** - Medical appointments, health insurance, fitness, wellness, pharmacy, healthcare services
9. **education** - Course enrollments, academic updates, learning platforms, online courses, certifications
10. **entertainment** - Movie tickets, event bookings, gaming, streaming, concerts, shows, sports
11. **utilities** - Electricity, water, gas, internet, phone bills, municipal services, broadband
12. **insurance** - Policy updates, claims, coverage information, health insurance, car insurance, life insurance
13. **real_estate** - Property listings, rent payments, mortgage updates, real estate services, property management
14. **food** - Food delivery, restaurant bookings, grocery orders, meal plans, food subscriptions
15. **transport** - Ride-sharing, public transport, fuel, parking, vehicle services, logistics
16. **technology** - Software updates, tech support, IT services, cybersecurity, digital services
17. **finance_investment** - Investment updates, stock alerts, mutual funds, trading, financial planning
18. **government** - Government services, tax updates, official communications, public services
19. **charity** - Donations, fundraising, NGO updates, social causes, volunteer opportunities
20. **other** - Everything else not covered above

### Subcategories and Specialized Processing

Each category has specialized extraction and storage logic:

- **Financial Transactions**: UPI details, bank information, subscription detection
- **Subscriptions**: Billing cycles, renewal dates, payment methods
- **Travel Bookings**: Flight details, hotel information, passenger data
- **Job Communications**: Application status, interview details, salary information
- **Promotional Emails**: Discount codes, validity periods, terms and conditions

## 🔧 Technical Features

### Enhanced Database Indexing

Optimized MongoDB indexes for performance:

```python
# User indexes
await db.users.create_index([("user_id", ASCENDING)], unique=True)
await db.users.create_index([("email", ASCENDING)], unique=True)
await db.users.create_index([("last_sync_date", DESCENDING)])

# Email indexes
await db.email_logs.create_index([("user_id", ASCENDING), ("gmail_id", ASCENDING)], unique=True)
await db.email_logs.create_index([("user_id", ASCENDING), ("received_date", DESCENDING)])

# Financial transaction indexes
await db.financial_transactions.create_index([("user_id", ASCENDING), ("date", DESCENDING)])
await db.financial_transactions.create_index([("user_id", ASCENDING), ("merchant_canonical", ASCENDING)])
```

### Parallel Processing

Batch processing with parallel execution:

```python
# Process emails in parallel
tasks = [
    enhanced_processor.process_email_comprehensive(email, user_id)
    for email in emails
]
batch_results = await asyncio.gather(*tasks, return_exceptions=True)
```

### Comprehensive Error Handling

Robust error handling with failure tracking:

```python
class ExtractionFailure(BaseModel):
    email_id: str
    user_id: str
    failure_type: str
    failure_stage: str
    error_message: str
    attempts: int
    is_resolved: bool
    # ... comprehensive error tracking
```

## 🌐 API Endpoints

### Enhanced Processing Endpoints

```
POST /enhanced/process-email
POST /enhanced/process-batch
GET /enhanced/database-stats
GET /enhanced/user/{user_id}/analytics
GET /enhanced/collections/{collection_name}
GET /enhanced/financial-transactions/{user_id}
GET /enhanced/subscriptions/{user_id}
```

### Example Usage

```python
# Process single email
response = await client.post("/enhanced/process-email", json={
    "email_data": email_data,
    "user_id": "user_123"
})

# Get financial transactions
response = await client.get("/enhanced/financial-transactions/user_123", params={
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "category": "subscription"
})
```

## 📈 Analytics and Insights

### User Analytics

Comprehensive analytics tracking:

```python
class UserAnalytics(BaseModel):
    user_id: str
    date: str
    emails_synced: int
    emails_categorized: int
    emails_extracted: int
    financial_transactions: int
    subscriptions: int
    travel_bookings: int
    job_communications: int
    promotional_emails: int
    total_spending: float
    top_categories: List[TopCategory]
    top_merchants: List[TopMerchant]
    payment_methods: List[PaymentMethodCount]
```

### Query Analytics

Track query performance and user behavior:

```python
class QueryLog(BaseModel):
    user_id: str
    query_text: str
    query_intent: Optional[str]
    results_count: int
    processing_time_ms: int
    success: bool
    ai_model_used: Optional[str]
    user_satisfaction: Optional[int]
```

## 🚀 Getting Started

### 1. Installation

```bash
cd backend
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Start MongoDB
docker-compose up -d mongodb

# Initialize database indexes
python -m app.services.database_service
```

### 3. Run the Application

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Run Demo

```bash
# Run the enhanced system demo
python demo_enhanced_system.py
```

## 📊 Database Schema Examples

### Financial Transaction Example

```json
{
  "_id": "transaction_123",
  "user_id": "user_456",
  "email_id": "email_789",
  "amount": 499.00,
  "currency": "INR",
  "transaction_type": "subscription",
  "merchant": "Netflix",
  "merchant_canonical": "Netflix",
  "payment_method": "upi",
  "upi_details": {
    "transaction_flow": {
      "direction": "outgoing",
      "description": "Money sent from your account"
    },
    "receiver": {
      "upi_id": "netflix@upi",
      "name": "Netflix",
      "upi_app": "netflix"
    }
  },
  "subscription_details": {
    "is_subscription": true,
    "product_name": "Netflix Premium",
    "billing_frequency": "monthly",
    "next_renewal_date": "2024-12-15T00:00:00Z"
  },
  "confidence_score": 0.95,
  "extraction_confidence": 0.98,
  "created_at": "2024-11-15T14:30:25Z"
}
```

### Subscription Example

```json
{
  "_id": "subscription_123",
  "user_id": "user_456",
  "email_id": "email_789",
  "service_name": "Amazon Prime",
  "service_canonical": "Amazon Prime",
  "service_category": "streaming_services",
  "subscription_type": "premium",
  "amount": 1499.00,
  "currency": "INR",
  "billing_frequency": "yearly",
  "next_billing_date": "2024-12-15T00:00:00Z",
  "is_automatic_payment": true,
  "payment_method": "credit_card",
  "status": "active",
  "confidence_score": 0.98,
  "created_at": "2024-11-15T14:30:25Z"
}
```

## 🔍 Query Examples

### Get Financial Transactions

```python
# Get all transactions for a user
transactions = await financial_transactions_collection.find({
    "user_id": "user_123"
}).to_list(length=None)

# Get transactions by category
subscriptions = await financial_transactions_collection.find({
    "user_id": "user_123",
    "primary_category": "subscription"
}).to_list(length=None)

# Get transactions by date range
recent_transactions = await financial_transactions_collection.find({
    "user_id": "user_123",
    "date": {
        "$gte": datetime(2024, 1, 1),
        "$lte": datetime(2024, 12, 31)
    }
}).to_list(length=None)
```

### Get User Analytics

```python
# Get today's analytics
today = datetime.now().strftime("%Y-%m-%d")
analytics = await user_analytics_collection.find_one({
    "user_id": "user_123",
    "date": today
})
```

## 🎯 Key Benefits

1. **Comprehensive Data Extraction**: Extract structured data from all email types
2. **Specialized Collections**: Optimized storage for different data types
3. **Advanced Analytics**: Real-time insights and reporting
4. **Scalable Architecture**: Handle large volumes of email data
5. **Robust Error Handling**: Comprehensive failure tracking and retry
6. **Performance Optimized**: Efficient indexing and parallel processing
7. **Extensible Design**: Easy to add new categories and extraction logic

## 🔮 Future Enhancements

- **Machine Learning Models**: Enhanced categorization with custom ML models
- **Real-time Processing**: WebSocket-based real-time email processing
- **Advanced Analytics**: Predictive analytics and spending insights
- **Multi-language Support**: Support for multiple languages
- **Mobile API**: Optimized API for mobile applications
- **Data Export**: Export capabilities for external analysis

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 