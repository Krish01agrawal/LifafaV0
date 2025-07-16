"""
Comprehensive Financial Transaction Models
=========================================

Enhanced models for storing detailed financial transaction data
with maximum categorization and metadata for efficient retrieval.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    """Enhanced transaction types"""
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

class PaymentStatus(str, Enum):
    """Payment status"""
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"
    PARTIAL = "partial"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"

class UPIApp(str, Enum):
    """UPI Apps"""
    GOOGLE_PAY = "google_pay"
    PHONE_PE = "phone_pe"
    PAYTM = "paytm"
    AMAZON_PAY = "amazon_pay"
    BHIM = "bhim"
    HDFC_BANK = "hdfc_bank"
    AXIS_BANK = "axis_bank"
    UNKNOWN = "unknown"

class BankDetails(BaseModel):
    """Bank account details"""
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_type: Optional[str] = None
    ifsc_code: Optional[str] = None
    branch: Optional[str] = None

class UPIReceiver(BaseModel):
    """UPI receiver details"""
    upi_id: Optional[str] = None
    name: Optional[str] = None
    upi_app: Optional[str] = None
    merchant_code: Optional[str] = None

class UPIFlow(BaseModel):
    """UPI transaction flow"""
    direction: str = "outgoing"  # outgoing/incoming
    description: str = "Money sent from your account"
    transaction_type: Optional[str] = None

class UPIDetails(BaseModel):
    """Complete UPI transaction details"""
    transaction_flow: Optional[UPIFlow] = None
    receiver: Optional[UPIReceiver] = None
    sender_upi_id: Optional[str] = None
    transaction_reference: Optional[str] = None
    merchant_category_code: Optional[str] = None

class CardDetails(BaseModel):
    """Card transaction details"""
    card_type: Optional[str] = None  # visa, mastercard, rupay
    card_number_last4: Optional[str] = None
    card_network: Optional[str] = None
    card_issuer: Optional[str] = None
    card_category: Optional[str] = None  # credit, debit, prepaid

class SubscriptionDetails(BaseModel):
    """Subscription information"""
    is_subscription: bool = False
    product_name: Optional[str] = None
    category: Optional[str] = None
    type: Optional[str] = None
    confidence_score: float = 0.0
    detection_reasons: List[str] = []
    subscription_frequency: Optional[str] = None  # monthly, yearly, quarterly
    next_renewal_date: Optional[str] = None
    is_automatic_payment: bool = False
    subscription_id: Optional[str] = None

class MerchantDetails(BaseModel):
    """Detailed merchant information"""
    canonical_name: str
    original_name: str
    patterns: List[str] = []
    category: Optional[str] = None
    subcategory: Optional[str] = None
    confidence_score: float = 0.0
    detection_method: Optional[str] = None  # pattern_match, ai_extraction, manual

class FinancialBreakdown(BaseModel):
    """Financial amount breakdown"""
    total_amount: float = 0.0
    base_amount: float = 0.0
    tax_amount: float = 0.0
    discount_amount: float = 0.0
    late_fee_amount: float = 0.0
    processing_fee: float = 0.0
    cashback_amount: float = 0.0
    convenience_fee: float = 0.0

class EmailMetadata(BaseModel):
    """Email metadata for context"""
    subject: str
    sender: str
    received_date: Optional[str] = None
    snippet: Optional[str] = None
    body_hash: Optional[str] = None
    importance_score: float = 0.0
    is_financial_email: bool = False
    is_promotional: bool = False

class ExtractionMetadata(BaseModel):
    """Extraction process metadata"""
    extracted_at: datetime
    extraction_method: str = "ai_extraction"  # ai_extraction, pattern_match, manual
    confidence_score: float = 0.0
    data_completeness: float = 0.0
    extraction_version: str = "2.0"
    model_used: Optional[str] = None
    processing_time_ms: Optional[int] = None

class FinancialTransaction(BaseModel):
    """Comprehensive financial transaction model"""
    
    # Core identifiers
    id: str = Field(..., description="Unique transaction ID")
    email_id: str = Field(..., description="Original email ID")
    user_id: str = Field(..., description="User ID")
    
    # Core transaction data
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(default="INR", description="Currency code")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    transaction_date: Optional[str] = Field(None, description="Transaction date YYYY-MM-DD")
    
    # Merchant information
    merchant: str = Field(..., description="Merchant name")
    merchant_details: Optional[MerchantDetails] = None
    service_category: Optional[ServiceCategory] = None
    service_name: Optional[str] = None
    
    # Payment details
    payment_method: PaymentMethod = Field(default=PaymentMethod.UNKNOWN)
    payment_status: PaymentStatus = Field(default=PaymentStatus.COMPLETED)
    transaction_id: Optional[str] = None
    invoice_number: Optional[str] = None
    order_id: Optional[str] = None
    receipt_number: Optional[str] = None
    
    # Banking details
    bank_details: Optional[BankDetails] = None
    account_info: Optional[Dict[str, Any]] = None
    
    # UPI specific details
    upi_details: Optional[UPIDetails] = None
    
    # Card specific details
    card_details: Optional[CardDetails] = None
    
    # Subscription details
    subscription_details: Optional[SubscriptionDetails] = None
    is_subscription: bool = False
    subscription_product: Optional[str] = None
    
    # Financial breakdown
    financial_breakdown: Optional[FinancialBreakdown] = None
    
    # Billing and service periods
    due_date: Optional[str] = None
    service_period_start: Optional[str] = None
    service_period_end: Optional[str] = None
    billing_period_start: Optional[str] = None
    billing_period_end: Optional[str] = None
    
    # Email context
    email_metadata: Optional[EmailMetadata] = None
    description: Optional[str] = None
    snippet: Optional[str] = None
    sender: Optional[str] = None
    subject: Optional[str] = None
    
    # Extraction metadata
    extraction_metadata: Optional[ExtractionMetadata] = None
    extracted_at: Optional[datetime] = None
    confidence_score: float = Field(default=0.0, description="Overall confidence score")
    
    # Additional fields for comprehensive storage
    amount_original: Optional[str] = None  # Original amount string from email
    date_original: Optional[str] = None    # Original date string from email
    full_text_context: Optional[str] = None
    email_summary: Optional[str] = None
    
    # Action flags
    requires_action: bool = False
    is_automatic_payment: bool = False
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TransactionQuery(BaseModel):
    """Query model for efficient MongoDB queries"""
    user_id: str
    date_range: Optional[Dict[str, str]] = None
    amount_range: Optional[Dict[str, float]] = None
    transaction_types: Optional[List[TransactionType]] = None
    payment_methods: Optional[List[PaymentMethod]] = None
    merchants: Optional[List[str]] = None
    categories: Optional[List[ServiceCategory]] = None
    is_subscription: Optional[bool] = None
    confidence_min: Optional[float] = None
    limit: Optional[int] = 100
    offset: Optional[int] = 0

class TransactionStats(BaseModel):
    """Transaction statistics"""
    total_transactions: int = 0
    total_amount: float = 0.0
    avg_amount: float = 0.0
    transaction_count_by_type: Dict[str, int] = {}
    amount_by_type: Dict[str, float] = {}
    merchant_breakdown: Dict[str, int] = {}
    category_breakdown: Dict[str, int] = {}
    payment_method_breakdown: Dict[str, int] = {}
    subscription_count: int = 0
    subscription_amount: float = 0.0
    date_range: Optional[Dict[str, str]] = None

class CategorizedEmail(BaseModel):
    """Enhanced categorized email model"""
    user_id: str
    email_id: str
    category: str
    subcategory: Optional[str] = None
    confidence: float = 0.0
    key_indicators: List[str] = []
    merchant_detected: Optional[str] = None
    transaction_likely: bool = False
    priority: str = "medium"  # high, medium, low
    importance_score: float = 0.0
    
    # Original email data
    original_email: Dict[str, Any] = {}
    
    # Processing flags
    categorized: bool = True
    categorized_at: Optional[datetime] = None
    financial_data_extracted: bool = False
    extracted_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }  