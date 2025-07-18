"""
Enhanced Financial and Email Models
==================================

Comprehensive models for all database collections in the enhanced email categorization system.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
import hashlib

# ============================================================================
# ENUMS
# ============================================================================

class TransactionType(str, Enum):
    """Transaction types"""
    PAYMENT = "payment"
    BILL = "bill"
    SUBSCRIPTION = "subscription"
    INCOME = "income"
    REFUND = "refund"
    FEE = "fee"
    TRANSFER = "transfer"
    INVESTMENT = "investment"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"
    DEBIT = "debit"
    CREDIT = "credit"

class PaymentMethod(str, Enum):
    """Payment methods"""
    UPI = "upi"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    NET_BANKING = "net_banking"
    WALLET = "wallet"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    EMI = "emi"
    AUTO_DEBIT = "auto_debit"
    UNKNOWN = "unknown"

class PaymentStatus(str, Enum):
    """Payment status"""
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"
    PARTIAL = "partial"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"

class ServiceCategory(str, Enum):
    """Service categories"""
    TELECOM = "telecom"
    UTILITIES = "utilities"
    OTT = "ott"
    BANKING = "banking"
    ECOMMERCE = "ecommerce"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    TRANSPORT = "transport"
    FOOD = "food"
    ENTERTAINMENT = "entertainment"
    INVESTMENT = "investment"
    INSURANCE = "insurance"
    GOVERNMENT = "government"
    RETAIL = "retail"
    CLOUD_STORAGE = "cloud_storage"
    FINANCIAL_SERVICES = "financial_services"

class EmailCategory(str, Enum):
    """Email categories"""
    FINANCE = "finance"
    TRAVEL = "travel"
    JOB = "job"
    PROMOTION = "promotion"
    SUBSCRIPTION = "subscription"
    SHOPPING = "shopping"
    SOCIAL = "social"
    HEALTH = "health"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    INSURANCE = "insurance"
    REAL_ESTATE = "real_estate"
    FOOD = "food"
    TRANSPORT = "transport"
    TECHNOLOGY = "technology"
    FINANCE_INVESTMENT = "finance_investment"
    GOVERNMENT = "government"
    CHARITY = "charity"
    OTHER = "other"

class SyncStatus(str, Enum):
    """Sync status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class CategorizationStatus(str, Enum):
    """Categorization status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class QueueStatus(str, Enum):
    """Queue status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"

class Priority(str, Enum):
    """Priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# ============================================================================
# CORE USER & AUTHENTICATION MODELS
# ============================================================================

class UserPreferences(BaseModel):
    """User preferences"""
    currency: str = "INR"
    timezone: str = "Asia/Kolkata"
    language: str = "en"
    notifications: Dict[str, bool] = Field(default_factory=lambda: {
        "email_alerts": True,
        "spending_alerts": True,
        "subscription_reminders": True
    })

class User(BaseModel):
    """Enhanced user model"""
    user_id: str
    email: str
    name: Optional[str] = None
    google_auth_token: Optional[str] = None
    gmail_access_token: Optional[str] = None
    gmail_refresh_token: Optional[str] = None
    gmail_scope: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    last_sync_date: Optional[datetime] = None
    sync_status: SyncStatus = SyncStatus.PENDING
    emails_synced: int = 0
    emails_categorized: int = 0
    emails_extracted: int = 0
    categorization_status: CategorizationStatus = CategorizationStatus.PENDING
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    subscription_tier: str = "free"
    is_active: bool = True
    verification_status: str = "pending"

class UserSession(BaseModel):
    """User session model"""
    user_id: str
    session_id: str
    access_token: str
    refresh_token: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_type: Optional[str] = None
    login_time: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_active: bool = True
    logout_time: Optional[datetime] = None

# ============================================================================
# RAW EMAIL MODELS
# ============================================================================

class EmailAttachment(BaseModel):
    """Email attachment model"""
    attachment_id: str
    filename: str
    content_type: str
    size: int
    is_inline: bool = False

class EmailLog(BaseModel):
    """Enhanced email log model"""
    id: str
    email_id: str
    user_id: str
    gmail_id: str
    thread_id: Optional[str] = None
    subject: str
    from_: str = Field(alias="from")
    to: str
    cc: List[str] = Field(default_factory=list)
    bcc: List[str] = Field(default_factory=list)
    snippet: str
    body: Optional[str] = None
    body_plain: Optional[str] = None
    body_html: Optional[str] = None
    received_date: datetime
    sent_date: Optional[datetime] = None
    labels: List[str] = Field(default_factory=list)
    is_read: bool = False
    is_starred: bool = False
    is_important: bool = False
    is_spam: bool = False
    is_trash: bool = False
    size_estimate: Optional[int] = None
    history_id: Optional[str] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    attachments: List[EmailAttachment] = Field(default_factory=list)
    classification_status: str = "pending"
    email_category: Optional[str] = None
    importance_score: float = 5.0
    financial: bool = False
    body_hash: Optional[str] = None
    subject_hash: Optional[str] = None
    sender_domain: Optional[str] = None
    extraction_attempts: int = 0
    last_extraction_attempt: Optional[datetime] = None
    extraction_error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def generate_hashes(self):
        """Generate hashes for body and subject"""
        if self.body:
            self.body_hash = hashlib.sha256(self.body.encode()).hexdigest()
        if self.subject:
            self.subject_hash = hashlib.sha256(self.subject.encode()).hexdigest()

class Email(BaseModel):
    """Enhanced email model"""
    id: str
    email_id: str
    user_id: str
    subject: str
    from_: str = Field(alias="from")
    snippet: str
    body: Optional[str] = None
    date: datetime
    financial: bool = False
    importance_score: float = 5.0
    filter_reason: Optional[str] = None
    data_complete: bool = False
    sender_domain: Optional[str] = None
    sender_category: Optional[str] = None
    is_transactional: bool = False
    requires_action: bool = False
    urgency_level: Optional[str] = None
    attachments: List[EmailAttachment] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# CATEGORIZED EMAIL MODELS
# ============================================================================

class CategorizedEmail(BaseModel):
    """Enhanced categorized email model"""
    user_id: str
    email_id: str
    primary_category: str
    secondary_category: Optional[str] = None
    tertiary_category: Optional[str] = None
    subcategory: Optional[str] = None
    confidence: float
    key_indicators: List[str] = Field(default_factory=list)
    merchant_detected: Optional[str] = None
    merchant_confidence: Optional[float] = None
    transaction_likely: bool = False
    priority: Priority = Priority.MEDIUM
    importance_score: float = 5.0
    urgency_level: Optional[str] = None
    requires_action: bool = False
    action_required: Optional[str] = None
    deadline: Optional[datetime] = None
    original_email: Dict[str, Any] = Field(default_factory=dict)
    categorized: bool = True
    categorized_at: datetime = Field(default_factory=datetime.utcnow)
    financial_data_extracted: bool = False
    extracted_at: Optional[datetime] = None
    ai_model_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# FINANCIAL TRANSACTION MODELS
# ============================================================================

class BankDetails(BaseModel):
    """Bank details model"""
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_type: Optional[str] = None
    ifsc_code: Optional[str] = None
    branch: Optional[str] = None
    card_type: Optional[str] = None
    card_number: Optional[str] = None

class UPITransactionFlow(BaseModel):
    """UPI transaction flow model"""
    direction: str  # "outgoing" or "incoming"
    description: str

class UPIReceiver(BaseModel):
    """UPI receiver model"""
    upi_id: str
    name: str
    upi_app: str
    merchant_code: Optional[str] = None

class UPISender(BaseModel):
    """UPI sender model"""
    upi_id: Optional[str] = None
    upi_app: Optional[str] = None

class UPIDetails(BaseModel):
    """UPI details model"""
    transaction_flow: UPITransactionFlow
    receiver: UPIReceiver
    sender: UPISender = Field(default_factory=UPISender)

class CardDetails(BaseModel):
    """Card details model"""
    card_type: Optional[str] = None
    card_number: Optional[str] = None
    expiry_date: Optional[str] = None
    card_network: Optional[str] = None

class SubscriptionDetails(BaseModel):
    """Subscription details model"""
    is_subscription: bool = False
    product_name: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    confidence_score: float = 0.7
    detection_reasons: List[str] = Field(default_factory=list)
    subscription_frequency: Optional[str] = None
    next_renewal_date: Optional[datetime] = None
    is_automatic_payment: bool = False

class LocationDetails(BaseModel):
    """Location details model"""
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    coordinates: Optional[Dict[str, float]] = None

class FinancialTransaction(BaseModel):
    """Enhanced financial transaction model"""
    id: str
    email_id: str
    user_id: str
    date: datetime
    amount: float
    currency: str = "INR"
    transaction_type: TransactionType
    transaction_subtype: Optional[str] = None
    merchant: str
    merchant_canonical: str
    merchant_original: Optional[str] = None
    merchant_patterns: List[str] = Field(default_factory=list)
    description: str
    detailed_description: Optional[str] = None
    payment_method: PaymentMethod
    payment_submethod: Optional[str] = None
    account_info: Optional[str] = None
    transaction_id: Optional[str] = None
    transaction_reference: Optional[str] = None
    invoice_number: Optional[str] = None
    order_id: Optional[str] = None
    receipt_number: Optional[str] = None
    
    # Email Details
    sender: str
    subject: str
    snippet: str
    email_body_hash: Optional[str] = None
    email_received_date: datetime
    
    # Service Details
    service_category: ServiceCategory
    service_subcategory: Optional[str] = None
    service_name: Optional[str] = None
    service_provider: Optional[str] = None
    
    # Payment Details
    payment_status: PaymentStatus = PaymentStatus.COMPLETED
    payment_flow: str = "outgoing"
    is_automatic_payment: bool = False
    is_recurring: bool = False
    requires_action: bool = False
    
    # Amount Breakdown
    total_amount: float
    base_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    late_fee_amount: Optional[float] = None
    processing_fee: Optional[float] = None
    cashback_amount: Optional[float] = None
    convenience_fee: Optional[float] = None
    delivery_fee: Optional[float] = None
    tip_amount: Optional[float] = None
    
    # Dates
    transaction_date: Optional[str] = None
    due_date: Optional[datetime] = None
    service_period_start: Optional[datetime] = None
    service_period_end: Optional[datetime] = None
    billing_period_start: Optional[datetime] = None
    billing_period_end: Optional[datetime] = None
    clearance_date: Optional[str] = None
    important_invoice_date: Optional[datetime] = None
    
    # Bank Details
    bank_details: BankDetails = Field(default_factory=BankDetails)
    
    # UPI Details
    upi_details: UPIDetails = Field(default_factory=UPIDetails)
    
    # Card Details
    card_details: CardDetails = Field(default_factory=CardDetails)
    
    # Subscription Details
    is_subscription: bool = False
    subscription_product: Optional[str] = None
    subscription_details: SubscriptionDetails = Field(default_factory=SubscriptionDetails)
    
    # Location Details
    location: LocationDetails = Field(default_factory=LocationDetails)
    
    # Categorization
    primary_category: str = "finance"
    secondary_category: Optional[str] = None
    tertiary_category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Quality Metrics
    confidence_score: float = 0.8
    extraction_confidence: float = 0.95
    data_completeness: float = 0.90
    ai_model_used: Optional[str] = None
    extraction_method: str = "ai_extraction"
    
    # Metadata
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# SPECIALIZED CATEGORY MODELS
# ============================================================================

class Subscription(BaseModel):
    """Enhanced subscription model"""
    user_id: str
    email_id: str
    service_name: str
    service_canonical: str
    service_category: str
    service_subcategory: str
    subscription_type: str
    subscription_tier: str
    amount: float
    currency: str = "INR"
    billing_frequency: str
    billing_cycle: str
    next_billing_date: datetime
    last_billing_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    cancellation_date: Optional[datetime] = None
    is_automatic_payment: bool = True
    payment_method: PaymentMethod
    status: str = "active"
    auto_renewal: bool = True
    trial_period: bool = False
    trial_end_date: Optional[datetime] = None
    merchant_canonical: str
    merchant_original: Optional[str] = None
    upi_id: Optional[str] = None
    confidence_score: float = 0.98
    detection_reasons: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TravelLocation(BaseModel):
    """Travel location model"""
    city: str
    airport_code: Optional[str] = None
    country: str = "India"

class PassengerDetails(BaseModel):
    """Passenger details model"""
    name: str
    age: Optional[int] = None
    passport_number: Optional[str] = None

class FlightDetails(BaseModel):
    """Flight details model"""
    airline: Optional[str] = None
    flight_number: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    duration: Optional[str] = None

class HotelDetails(BaseModel):
    """Hotel details model"""
    hotel_name: Optional[str] = None
    room_type: Optional[str] = None
    amenities: List[str] = Field(default_factory=list)

class TravelBooking(BaseModel):
    """Enhanced travel booking model"""
    user_id: str
    email_id: str
    booking_type: str
    service_provider: str
    provider_canonical: str
    booking_reference: str
    pnr_number: Optional[str] = None
    confirmation_number: Optional[str] = None
    travel_date: datetime
    return_date: Optional[datetime] = None
    booking_date: Optional[datetime] = None
    from_location: TravelLocation
    to_location: TravelLocation
    passenger_count: int
    passenger_details: List[PassengerDetails] = Field(default_factory=list)
    total_amount: float
    currency: str = "INR"
    payment_method: PaymentMethod
    payment_status: PaymentStatus = PaymentStatus.COMPLETED
    booking_status: str = "confirmed"
    cancellation_policy: Optional[str] = None
    refund_policy: Optional[str] = None
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    flight_details: FlightDetails = Field(default_factory=FlightDetails)
    hotel_details: HotelDetails = Field(default_factory=HotelDetails)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class JobCommunication(BaseModel):
    """Enhanced job communication model"""
    user_id: str
    email_id: str
    communication_type: str
    company_name: str
    company_canonical: str
    position_title: str
    position_level: Optional[str] = None
    department: Optional[str] = None
    application_status: str
    interview_stage: Optional[str] = None
    interview_date: Optional[datetime] = None
    interview_type: Optional[str] = None
    interview_duration: Optional[str] = None
    salary_offered: Optional[float] = None
    salary_currency: str = "INR"
    salary_type: Optional[str] = None
    location: Optional[str] = None
    work_type: Optional[str] = None
    urgency_level: Optional[str] = None
    requires_response: bool = False
    response_deadline: Optional[datetime] = None
    application_id: Optional[str] = None
    job_id: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    benefits: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CashbackDetails(BaseModel):
    """Cashback details model"""
    amount: float
    type: str  # "instant" or "delayed"
    validity_days: int

class ReferralDetails(BaseModel):
    """Referral details model"""
    referral_code: str
    reward_amount: float
    validity_days: int

class PromotionalEmail(BaseModel):
    """Enhanced promotional email model"""
    user_id: str
    email_id: str
    promotion_type: str
    discount_amount: Optional[float] = None
    discount_percentage: Optional[float] = None
    original_price: Optional[float] = None
    discounted_price: Optional[float] = None
    currency: str = "INR"
    merchant_canonical: str
    merchant_name: str
    merchant_category: str
    offer_category: str
    promotion_code: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    minimum_purchase: Optional[float] = None
    maximum_discount: Optional[float] = None
    terms_conditions: Optional[str] = None
    is_expired: bool = False
    is_used: bool = False
    usage_limit: Optional[int] = None
    usage_count: int = 0
    offer_highlights: List[str] = Field(default_factory=list)
    target_audience: Optional[str] = None
    exclusions: List[str] = Field(default_factory=list)
    delivery_info: Optional[str] = None
    payment_options: List[str] = Field(default_factory=list)
    cashback_details: Optional[CashbackDetails] = None
    referral_details: Optional[ReferralDetails] = None
    extraction_confidence: float = 0.94
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# SYSTEM & ANALYTICS MODELS
# ============================================================================

class EmailQueue(BaseModel):
    """Enhanced email queue model"""
    user_id: str
    email_id: str
    queue_type: str
    status: QueueStatus = QueueStatus.PENDING
    priority: int = 5
    attempts: int = 0
    max_attempts: int = 3
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    retry_after: Optional[datetime] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    worker_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ExtractionFailure(BaseModel):
    """Enhanced extraction failure model"""
    email_id: str
    user_id: str
    failure_type: str
    failure_stage: str
    error_message: str
    error_code: Optional[str] = None
    error_stack: Optional[str] = None
    email_data: Dict[str, Any] = Field(default_factory=dict)
    attempts: int = 0
    max_attempts: int = 3
    is_resolved: bool = False
    resolution_method: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    ai_model_used: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class QueryLog(BaseModel):
    """Enhanced query log model"""
    user_id: str
    session_id: Optional[str] = None
    query_text: str
    query_intent: Optional[str] = None
    query_type: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    subcategories: List[str] = Field(default_factory=list)
    merchants: List[str] = Field(default_factory=list)
    date_range: Optional[Dict[str, datetime]] = None
    results_count: int = 0
    processing_time_ms: int = 0
    success: bool = True
    error_message: Optional[str] = None
    ai_model_used: Optional[str] = None
    response_quality: Optional[str] = None
    user_satisfaction: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TopCategory(BaseModel):
    """Top category model"""
    category: str
    amount: float

class TopMerchant(BaseModel):
    """Top merchant model"""
    merchant: str
    amount: float

class PaymentMethodCount(BaseModel):
    """Payment method count model"""
    method: str
    count: int

class UserAnalytics(BaseModel):
    """Enhanced user analytics model"""
    user_id: str
    date: str
    emails_synced: int = 0
    emails_categorized: int = 0
    emails_extracted: int = 0
    financial_transactions: int = 0
    subscriptions: int = 0
    travel_bookings: int = 0
    job_communications: int = 0
    promotional_emails: int = 0
    queries_made: int = 0
    total_spending: float = 0.0
    top_categories: List[TopCategory] = Field(default_factory=list)
    top_merchants: List[TopMerchant] = Field(default_factory=list)
    payment_methods: List[PaymentMethodCount] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Chat(BaseModel):
    """Enhanced chat model"""
    user_id: str
    session_id: str
    message: str
    message_type: str  # "user" or "bot"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    query_intent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)  