# Pluto Money - GenAI Email Intelligence Platform

A comprehensive Generative AI-powered email intelligence platform that transforms 6 months of Gmail data into structured, queryable insights across multiple categories using LLMs, MongoDB, and advanced data processing.

## 🚀 Features

### Core Capabilities
- **Gmail Integration**: Secure OAuth2 authentication and email fetching
- **Multi-Category Classification**: Finance, Travel, Job, Promotional emails
- **LLM-Powered Extraction**: Structured data extraction with 30+ fields per email
- **Natural Language Queries**: Ask questions in plain English
- **Real-time Analytics**: Comprehensive insights and breakdowns
- **Cost-Optimized Architecture**: In-memory caching, batch processing, efficient LLM usage

### Data Categories
- **Financial Transactions**: Bills, payments, subscriptions, income, refunds
- **Travel Bookings**: Flights, hotels, trains, car rentals
- **Job Communications**: Applications, interviews, offers, networking
- **Promotional Emails**: Discounts, offers, sales, coupons

## 🏗️ Architecture

### System Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   Background    │
│   (React/Vue)   │◄──►│   Backend       │◄──►│   Workers       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   MongoDB       │    │   In-Memory     │
                       │   Collections   │    │   Cache         │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   OpenAI LLM    │
                       │   Services      │
                       └─────────────────┘
```

### Data Flow
1. **User Authentication**: Google OAuth2 → JWT tokens
2. **Email Fetching**: Gmail API → Raw email storage
3. **Classification**: LLM-based email categorization
4. **Extraction**: Structured data extraction per category
5. **Storage**: MongoDB collections with comprehensive indexing
6. **Querying**: Natural language → Intent analysis → Sub-queries → Synthesis

## 📦 Installation

### Prerequisites
- Python 3.9+
- MongoDB 5.0+
- Google Cloud Console project with Gmail API enabled
- OpenAI API key

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd LifafaV0/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
cp env.example .env
# Edit .env with your actual values
```

5. **Database setup**
```bash
# Start MongoDB (if not running)
mongod

# Create database and collections (automatic on first run)
```

6. **Run the application**
```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Database name | `pluto_money` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Required |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `EMAIL_BATCH_SIZE` | Emails per processing batch | `16` |
| `CACHE_MAX_SIZE` | In-memory cache size | `1000` |

### Google Cloud Setup

1. Create a project in Google Cloud Console
2. Enable Gmail API
3. Create OAuth2 credentials
4. Add authorized redirect URIs
5. Download credentials and update `.env`

## 📚 API Documentation

### Authentication Endpoints
- `POST /auth/google` - Google OAuth authentication
- `GET /auth/profile` - Get user profile
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout user

### Email Sync Endpoints
- `POST /sync/gmail` - Start Gmail synchronization
- `GET /sync/status/{user_id}` - Get sync status
- `POST /sync/retry/{user_id}` - Retry failed emails
- `DELETE /sync/cancel/{user_id}` - Cancel sync

### Query Endpoints
- `POST /query/ask` - Ask natural language questions
- `POST /query/analytics` - Get comprehensive analytics
- `GET /query/search/{user_id}` - Search transactions
- `GET /query/summary/{user_id}` - Get quick summary

### Health Endpoints
- `GET /health/` - Basic health check
- `GET /health/detailed` - Detailed component status
- `GET /health/ready` - Readiness check
- `GET /health/live` - Liveness check

## 🗄️ Database Schema

### Collections

#### `users`
```json
{
  "_id": "ObjectId",
  "email": "user@gmail.com",
  "name": "User Name",
  "google_auth_token": {...},
  "gmail_sync_status": "completed",
  "email_count": 10000,
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

#### `email_logs`
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "gmail_id": "string",
  "email_subject": "Subject",
  "email_body": "Body content",
  "body_hash": "SHA256",
  "classification_status": "extracted",
  "email_category": "finance",
  "created_at": "ISODate"
}
```

#### `financial_transactions`
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "email_id": "ObjectId",
  "transaction_type": "payment",
  "amount": 599.00,
  "currency": "INR",
  "merchant_canonical": "Vodafone Idea",
  "service_category": "Telecom",
  "payment_status": "completed",
  "extraction_confidence": 0.97,
  "created_at": "ISODate"
}
```

## 🔄 Processing Pipeline

### Email Processing Flow
1. **Fetch**: Gmail API → Raw email storage
2. **Deduplicate**: SHA256 hash-based deduplication
3. **Classify**: LLM-based category classification
4. **Extract**: Structured data extraction per category
5. **Store**: MongoDB collections with indexes
6. **Cache**: In-memory caching for performance

### LLM Integration
- **Classification**: Single-shot email categorization
- **Extraction**: Structured JSON extraction with validation
- **Query Understanding**: Intent analysis and sub-query generation
- **Response Synthesis**: Natural language response generation

## 🚀 Performance Optimizations

### Cost Optimization
- **In-Memory Cache**: Redis alternative with LRU eviction
- **Batch Processing**: 16-email batches for LLM calls
- **Concurrency Control**: Semaphore-based rate limiting
- **Smart Caching**: Query result caching (30 minutes)

### Scalability Features
- **Async Processing**: Non-blocking email processing
- **Database Indexing**: Optimized MongoDB indexes
- **Connection Pooling**: Efficient database connections
- **Rate Limiting**: Request-level rate limiting

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_llm_service.py
```

### Test Structure
```
tests/
├── test_api/
│   ├── test_auth.py
│   ├── test_sync.py
│   └── test_query.py
├── test_services/
│   ├── test_llm_service.py
│   ├── test_gmail_service.py
│   └── test_database_service.py
└── test_workers/
    └── test_email_worker.py
```

## 📊 Monitoring

### Health Checks
- Database connectivity
- Cache performance
- LLM service availability
- Gmail API quota status

### Metrics
- Request/response times
- Cache hit rates
- Processing success rates
- Error rates by component

### Logging
- Structured logging with correlation IDs
- Request/response logging
- Error tracking with stack traces
- Performance monitoring

## 🔒 Security

### Authentication
- Google OAuth2 integration
- JWT token-based sessions
- Token refresh mechanism
- Secure credential storage

### Data Protection
- Email body hashing for deduplication
- Secure API key management
- Input validation and sanitization
- Rate limiting and abuse prevention

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker"]
```

### Environment Variables
```bash
# Production environment variables
export MONGODB_URL=mongodb://production-db:27017
export SECRET_KEY=your-production-secret-key
export DEBUG=false
export LOG_LEVEL=WARNING
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API examples

## 🔮 Roadmap

- [ ] Real-time email processing
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile app integration
- [ ] Advanced ML models
- [ ] Enterprise features