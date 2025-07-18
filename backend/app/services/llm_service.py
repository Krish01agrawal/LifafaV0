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
            # Decode base64 if needed
            import base64
            if email_body and email_body.startswith('data:'):
                try:
                    email_body = email_body.split(',', 1)[1]
                    email_body = base64.b64decode(email_body).decode('utf-8')
                except:
                    pass
            
            prompt = f"""
You are an expert email classifier. Categorize the following email into one of these detailed categories:

CRITICAL CLASSIFICATION RULES:
1. Classify as "finance" if there is ANY financial transaction, payment, bill, order, or receipt
2. Food delivery emails (Swiggy, Zomato, etc.) with order confirmations, receipts, or invoices are "finance"
3. Shopping emails with order confirmations, receipts, or invoices are "finance"
4. Subscription emails (Netflix, Spotify, etc.) with billing, payments, or receipts are "finance"
5. Transport services (Uber, Ola, etc.) with receipts, invoices, or payment confirmations are "finance"
6. Utility bills (electricity, water, gas, internet) are "finance"
7. Bank statements, UPI confirmations, credit card statements are "finance"
8. Any email with "receipt", "invoice", "order confirmation", "payment", "transaction" is "finance"
9. Only classify as "subscription" if it's a free service or non-payment related
10. When in doubt about financial content, classify as "finance" - let extraction determine if it's valid

EXAMPLES:
- Swiggy order confirmation/receipt/invoice = "finance"
- Swiggy order details = "finance"
- Zomato order confirmation = "finance"
- Netflix billing email = "finance"
- Uber ride receipt = "finance"
- Electricity bill = "finance"
- Bank transaction alert = "finance"
- UPI payment confirmation = "finance"
- Credit card statement = "finance"
- Insurance premium payment = "finance"
- Any email with "receipt", "invoice", "order" = "finance"

Categories:
- finance: Bills, payments, transactions, banking, credit cards, loans, investments, UPI transactions, bank alerts, subscription payments, shopping payments, food delivery payments, transport payments, utility payments, insurance payments, order confirmations with amounts, any email involving money or financial transactions
- travel: Flights, hotels, bookings, transportation, vacation packages, travel insurance, car rentals (only if no payment involved)
- job: Job applications, interviews, work communications, career opportunities, recruitment, HR updates
- promotion: Offers, discounts, marketing emails, sales, deals, coupons, cashback, referral programs (only if no payment involved)
- subscription: Free service subscriptions, non-payment memberships, free trials (NOT paid subscriptions)
- shopping: Online purchases, order confirmations, delivery updates, e-commerce, retail, marketplace (only if no payment involved)
- social: Social media notifications, friend requests, community updates, Reddit, LinkedIn, Facebook
- health: Medical appointments, health insurance, fitness, wellness, pharmacy, healthcare services (only if no payment involved)
- education: Course enrollments, academic updates, learning platforms, online courses, certifications (only if no payment involved)
- entertainment: Movie tickets, event bookings, gaming, streaming, concerts, shows, sports (only if no payment involved)
- utilities: Electricity, water, gas, internet, phone bills, municipal services, broadband (only if no payment involved)
- insurance: Policy updates, claims, coverage information, health insurance, car insurance, life insurance (only if no payment involved)
- real_estate: Property listings, rent payments, mortgage updates, real estate services, property management (only if no payment involved)
- food: Food delivery, restaurant bookings, grocery orders, meal plans, food subscriptions (only if no payment involved)
- transport: Ride-sharing, public transport, fuel, parking, vehicle services, logistics (only if no payment involved)
- technology: Software updates, tech support, IT services, cybersecurity, digital services (only if no payment involved)
- finance_investment: Investment updates, stock alerts, mutual funds, trading, financial planning (only if no payment involved)
- government: Government services, tax updates, official communications, public services
- charity: Donations, fundraising, NGO updates, social causes, volunteer opportunities
- other: Everything else not covered above

Email:
Subject: {email_subject}
Body: {email_body[:3000]}  # Increased limit for better classification

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
            # Decode base64 if needed
            import base64
            if email_body and email_body.startswith('data:'):
                try:
                    email_body = email_body.split(',', 1)[1]
                    email_body = base64.b64decode(email_body).decode('utf-8')
                except:
                    pass
            
            prompt = f"""
You are a financial data extractor. Extract detailed transaction data from this email.

CRITICAL REQUIREMENTS:
- ONLY extract data if there is a REAL financial transaction (payment, bill, order, etc.)
- If this is just a promotional email, subscription notification, or general communication, return null for all fields
- Look for SPECIFIC financial information:
  * Actual payment amounts (₹, $, etc.)
  * Order confirmations with prices
  * Bill payments with amounts
  * Transaction receipts
  * Payment confirmations
  * Bank statements
  * UPI transaction details

EXAMPLES OF WHAT TO EXTRACT:
✅ Swiggy order confirmation/receipt with amount: ₹299
✅ Swiggy order details with items and total
✅ Zomato order confirmation with amount
✅ SBI Mutual Fund transaction: ₹5000
✅ Electricity bill payment: ₹1200
✅ Netflix subscription: ₹499
❌ Slack account creation (no payment)
❌ GitHub welcome email (no payment)
❌ General promotional emails (no payment)

IMPORTANT: Food delivery emails (Swiggy, Zomato) are ALWAYS financial transactions - extract order details, amounts, items, delivery charges, taxes, etc.

Email:
Subject: {email_subject}
Body: {email_body[:4000]}  # Increased limit for better extraction

Return JSON in this exact format with detailed UPI and bank information:
{{
  "transaction_type": "payment|bill|subscription|income|refund|fee|transfer|debit|credit",
  "amount": 599.00,
  "currency": "INR",
  "transaction_date": "2024-03-15",
  "due_date": "2024-03-20",
  "service_period_start": "2024-02-01",
  "service_period_end": "2024-02-28",
  "merchant_canonical": "Vodafone Idea Limited",
  "merchant_name": "Vi",
  "merchant_category": "Telecom|Utilities|OTT|Banking|E-commerce|Education|Entertainment|Food|Transport|Healthcare",
  "merchant_patterns": ["Vi*", "*Vodafone*", "*Idea*"],
  "service_name": "Postpaid Plan",
  "service_category": "Telecom",
  "payment_status": "completed|pending|failed|partial|disputed|cancelled",
  "payment_method": "upi|credit_card|debit_card|net_banking|wallet|cash",
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
  "subscription_frequency": "monthly|weekly|yearly|one_time",
  "next_renewal_date": "2024-04-15",
  "is_subscription": true,
  "subscription_product": "Vodafone Postpaid",
  "confidence_score": 0.97,
  "bank_details": {{
    "bank_name": "HDFC Bank",
    "account_number": "XXXX8121"
  }},
  "upi_details": {{
    "transaction_flow": {{
      "direction": "outgoing|incoming",
      "description": "Money sent from your account"
    }},
    "receiver": {{
      "upi_id": "vodafone.rzp@hdfcbank",
      "name": "Vodafone Idea",
      "upi_app": "HDFC Bank UPI"
    }}
  }},
  "card_details": {{}},
  "subscription_details": {{
    "is_subscription": true,
    "product_name": "Vodafone Postpaid",
    "category": "Telecom",
    "type": "Mobile Service",
    "confidence_score": 0.8,
    "detection_reasons": ["Subscription keyword: postpaid", "Product keyword: vodafone"]
  }},
  "extraction_confidence": 0.97
}}

Extract ALL possible details from the email. If information is missing, use null or empty values.
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
You are a promotional data extractor. Extract detailed promotional data from this email:

Email:
Subject: {email_subject}
Body: {email_body[:3000]}  # Increased limit for better extraction

Return JSON in this exact format with detailed merchant and offer information:
{{
  "promotion_type": "discount|offer|sale|coupon|cashback|referral|free_trial|upgrade|membership",
  "discount_amount": 200.00,
  "discount_percentage": 20.0,
  "original_price": 1000.00,
  "discounted_price": 800.00,
  "currency": "INR|USD|EUR",
  "merchant_canonical": "Amazon India Private Limited",
  "merchant_name": "Amazon",
  "merchant_category": "E-commerce|Electronics|Fashion|Food|Travel|Entertainment|Education|Healthcare|Finance",
  "offer_category": "Electronics|Fashion|Home|Beauty|Sports|Books|Automotive|Baby|Pet|Garden",
  "promotion_code": "SAVE20",
  "valid_from": "2024-03-15",
  "valid_until": "2024-03-20",
  "minimum_purchase": 500.00,
  "maximum_discount": 500.00,
  "terms_conditions": "Valid on selected items only. Cannot be combined with other offers.",
  "is_expired": false,
  "is_used": false,
  "offer_highlights": ["Free delivery", "No cost EMI", "Instant discount"],
  "target_audience": "new_customers|existing_customers|all_customers|premium_members",
  "exclusions": ["Gift cards", "Digital content"],
  "delivery_info": "Free delivery on orders above ₹499",
  "payment_options": ["Credit Card", "UPI", "Net Banking"],
  "extraction_confidence": 0.94
}}

Extract ALL possible promotional details from the email. If information is missing, use null or empty values.
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
    
    async def extract_subscription_data(self, email_subject: str, email_body: str) -> Dict[str, Any]:
        """Extract subscription data from email."""
        try:
            # Decode base64 if needed
            import base64
            if email_body and email_body.startswith('data:'):
                try:
                    email_body = email_body.split(',', 1)[1]
                    email_body = base64.b64decode(email_body).decode('utf-8')
                except:
                    pass
            
            prompt = f"""
You are a subscription data extractor. Extract detailed subscription data from this email:

Email:
Subject: {email_subject}
Body: {email_body[:3000]}  # Increased limit for better extraction

Return JSON in this exact format with detailed subscription information:
{{
  "subscription_type": "streaming|software|service|membership|newsletter|platform|cloud|gaming|fitness|education|music|news|food|transport|healthcare|finance",
  "service_name": "Netflix",
  "service_canonical": "Netflix Inc",
  "service_category": "Entertainment|Productivity|Communication|Education|Health|Finance|Food|Transport|Shopping|Gaming|Music|News|Fitness|Cloud",
  "plan_name": "Premium Plan",
  "plan_features": ["4K streaming", "4 screens", "Downloads", "Ad-free"],
  "billing_frequency": "monthly|weekly|yearly|quarterly|one_time",
  "amount": 799.00,
  "currency": "INR|USD|EUR",
  "billing_date": "2024-03-15",
  "next_billing_date": "2024-04-15",
  "subscription_status": "active|inactive|cancelled|suspended|trial",
  "auto_renewal": true,
  "trial_end_date": null,
  "cancellation_date": null,
  "account_email": "user@example.com",
  "subscription_id": "sub_123456789",
  "payment_method": "credit_card|debit_card|upi|net_banking|wallet",
  "requires_action": false,
  "plan_details": {{
    "duration": "1 month",
    "price_per_month": 799.00,
    "annual_savings": 0.00,
    "features_count": 4
  }},
  "usage_limits": {{
    "screens": 4,
    "quality": "4K",
    "downloads": "Unlimited"
  }},
  "cancellation_policy": "Cancel anytime",
  "refund_policy": "No refunds for partial months",
  "support_contact": "support@netflix.com",
  "extraction_confidence": 0.95
}}

Extract ALL possible subscription details from the email. If information is missing, use null or empty values.
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
            logger.info(f"Subscription data extracted successfully")
            return data
            
        except Exception as e:
            logger.error(f"Error extracting subscription data: {e}")
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