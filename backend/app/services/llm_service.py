import openai
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config.settings import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for handling LLM operations with OpenAI."""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature
    
    async def classify_email(self, email_subject: str, email_body: str) -> str:
        """Classify email into categories."""
        try:
            prompt = f"""
You are an email classifier. Categorize the following email into one of these categories:

Categories:
- finance: Bills, payments, transactions, banking
- travel: Flights, hotels, bookings, transportation
- job: Job applications, interviews, work communications
- promotion: Offers, discounts, marketing emails
- subscription: Service subscriptions, renewals
- other: Everything else

Email:
Subject: {email_subject}
Body: {email_body[:1000]}  # Limit body length

Return only the category name.
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            category = response.choices[0].message.content.strip().lower()
            logger.info(f"Email classified as: {category}")
            return category
            
        except Exception as e:
            logger.error(f"Error classifying email: {e}")
            return "other"
    
    async def extract_financial_data(self, email_subject: str, email_body: str) -> Dict[str, Any]:
        """Extract financial transaction data from email."""
        try:
            prompt = f"""
You are a financial data extractor. Extract structured data from this email:

Email:
Subject: {email_subject}
Body: {email_body}

Return JSON in this exact format:
{{
  "transaction_type": "payment|bill|subscription|income|refund|fee|transfer",
  "amount": 599.00,
  "currency": "INR",
  "transaction_date": "2024-03-15",
  "due_date": "2024-03-20",
  "service_period_start": "2024-02-01",
  "service_period_end": "2024-02-28",
  "merchant_canonical": "Vodafone Idea",
  "merchant_name": "Vi",
  "merchant_category": "Telecom",
  "merchant_patterns": ["Vi*", "*Vodafone*"],
  "service_name": "Postpaid Plan",
  "service_category": "Telecom",
  "payment_status": "completed",
  "payment_method": "upi",
  "invoice_number": "INV-2024-12345",
  "transaction_reference": "TXN123456",
  "is_automatic_payment": true,
  "requires_action": false,
  "amount_original": "₹599.00",
  "date_original": "15th March 2024",
  "full_text_context": "Your payment of ₹599 to Vi is successful.",
  "email_summary": "Paid Vodafone bill of ₹599 via UPI",
  "tax_amount": 45.00,
  "late_fee_amount": 0.00,
  "billing_period_start": "2024-02-01",
  "billing_period_end": "2024-02-28",
  "account_number": "XXXXXXXXXX",
  "service_provider": "Vodafone Idea",
  "subscription_frequency": "monthly",
  "next_renewal_date": "2024-04-15",
  "extraction_confidence": 0.97
}}

Only return valid JSON. If information is missing, use null or empty values.
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            try:
                # Find JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                json_str = content[start_idx:end_idx]
                
                data = json.loads(json_str)
                logger.info(f"Financial data extracted successfully")
                return data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response content: {content}")
                raise
                
        except Exception as e:
            logger.error(f"Error extracting financial data: {e}")
            raise
    
    async def extract_travel_data(self, email_subject: str, email_body: str) -> Dict[str, Any]:
        """Extract travel booking data from email."""
        try:
            prompt = f"""
You are a travel data extractor. Extract structured data from this email:

Email:
Subject: {email_subject}
Body: {email_body}

Return JSON in this exact format:
{{
  "booking_type": "flight|hotel|train|bus|car_rental|package",
  "service_provider": "MakeMyTrip",
  "provider_canonical": "MakeMyTrip India Pvt Ltd",
  "booking_reference": "MMT123456",
  "pnr_number": "ABC123",
  "travel_date": "2024-04-15",
  "return_date": "2024-04-20",
  "from_location": "Mumbai",
  "to_location": "Delhi",
  "passenger_count": 2,
  "total_amount": 15000.00,
  "currency": "INR",
  "payment_method": "credit_card",
  "payment_status": "completed",
  "booking_status": "confirmed",
  "cancellation_policy": "Free cancellation until 24 hours before",
  "check_in_time": "14:00",
  "check_out_time": "12:00",
  "flight_number": "AI101",
  "hotel_name": "Taj Palace",
  "room_type": "Deluxe",
  "extraction_confidence": 0.97
}}

Only return valid JSON. If information is missing, use null or empty values.
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            json_str = content[start_idx:end_idx]
            
            data = json.loads(json_str)
            logger.info(f"Travel data extracted successfully")
            return data
            
        except Exception as e:
            logger.error(f"Error extracting travel data: {e}")
            raise
    
    async def extract_job_data(self, email_subject: str, email_body: str) -> Dict[str, Any]:
        """Extract job communication data from email."""
        try:
            prompt = f"""
You are a job data extractor. Extract structured data from this email:

Email:
Subject: {email_subject}
Body: {email_body}

Return JSON in this exact format:
{{
  "communication_type": "application|interview|offer|rejection|follow_up|networking",
  "company_name": "Google",
  "company_canonical": "Google LLC",
  "position_title": "Software Engineer",
  "position_level": "Senior",
  "department": "Engineering",
  "location": "Mountain View, CA",
  "remote_option": true,
  "salary_range_min": 120000,
  "salary_range_max": 180000,
  "currency": "USD",
  "interview_date": "2024-03-20",
  "interview_time": "10:00 AM",
  "interview_type": "phone",
  "interview_round": 1,
  "total_rounds": 4,
  "application_status": "interview",
  "application_date": "2024-03-01",
  "response_date": "2024-03-15",
  "requires_action": true,
  "action_deadline": "2024-03-18",
  "extraction_confidence": 0.96
}}

Only return valid JSON. If information is missing, use null or empty values.
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            json_str = content[start_idx:end_idx]
            
            data = json.loads(json_str)
            logger.info(f"Job data extracted successfully")
            return data
            
        except Exception as e:
            logger.error(f"Error extracting job data: {e}")
            raise
    
    async def extract_promotional_data(self, email_subject: str, email_body: str) -> Dict[str, Any]:
        """Extract promotional data from email."""
        try:
            prompt = f"""
You are a promotional data extractor. Extract structured data from this email:

Email:
Subject: {email_subject}
Body: {email_body}

Return JSON in this exact format:
{{
  "promotion_type": "discount|offer|sale|coupon|cashback|referral",
  "discount_amount": 200.00,
  "discount_percentage": 20.0,
  "original_price": 1000.00,
  "discounted_price": 800.00,
  "currency": "INR",
  "merchant_canonical": "Amazon India",
  "merchant_name": "Amazon",
  "merchant_category": "E-commerce",
  "offer_category": "Electronics",
  "promotion_code": "SAVE20",
  "valid_from": "2024-03-15",
  "valid_until": "2024-03-20",
  "minimum_purchase": 500.00,
  "maximum_discount": 500.00,
  "terms_conditions": "Valid on selected items only",
  "is_expired": false,
  "is_used": false,
  "extraction_confidence": 0.94
}}

Only return valid JSON. If information is missing, use null or empty values.
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            json_str = content[start_idx:end_idx]
            
            data = json.loads(json_str)
            logger.info(f"Promotional data extracted successfully")
            return data
            
        except Exception as e:
            logger.error(f"Error extracting promotional data: {e}")
            raise
    
    async def understand_query_intent(self, query: str) -> Dict[str, Any]:
        """Understand user query intent and break into sub-queries."""
        try:
            prompt = f"""
You are a query intent analyzer. Understand the user's question and break it into sub-queries.

User Query: {query}

Return JSON in this format:
{{
  "primary_intent": "expense_analysis|income_analysis|subscription_analysis|travel_analysis",
  "time_period": "2024-06|last_month|last_3_months|all_time",
  "categories": ["finance", "travel", "subscription"],
  "sub_queries": [
    "transactions in finance category for June 2024",
    "travel bookings in June 2024",
    "subscription payments in June 2024"
  ],
  "metrics": ["total_amount", "count", "breakdown_by_merchant"]
}}
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            json_str = content[start_idx:end_idx]
            
            data = json.loads(json_str)
            logger.info(f"Query intent understood successfully")
            return data
            
        except Exception as e:
            logger.error(f"Error understanding query intent: {e}")
            raise
    
    async def synthesize_response(self, query: str, data_points: List[Dict[str, Any]]) -> str:
        """Synthesize natural language response from data points."""
        try:
            data_summary = json.dumps(data_points, indent=2)
            
            prompt = f"""
You are a financial assistant. Create a natural language response based on the user's query and the provided data.

User Query: {query}

Data Points:
{data_summary}

Create a comprehensive, helpful response that:
1. Directly answers the user's question
2. Provides relevant insights and breakdowns
3. Uses natural, conversational language
4. Includes specific amounts, dates, and merchant names where relevant
5. Is concise but informative

Response:
"""
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"Response synthesized successfully")
            return content
            
        except Exception as e:
            logger.error(f"Error synthesizing response: {e}")
            raise

# Global LLM service instance
llm_service = LLMService() 