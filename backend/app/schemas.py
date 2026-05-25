from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from enum import Enum


# Enums
class PaymentTypeEnum(str, Enum):
    MONTHLY_RENT = "monthly_rent"
    DEPOSIT = "deposit"
    ELECTRICITY = "electricity"
    MAINTENANCE = "maintenance"
    PENALTY = "penalty"
    OTHER = "other"


class PaymentMethodEnum(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    UPI = "upi"
    CHEQUE = "cheque"


class BillTypeEnum(str, Enum):
    ELECTRICITY = "electricity"
    WATER = "water"
    MAINTENANCE = "maintenance"
    OTHER = "other"


# Auth Schemas
class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class TenantLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_id: int


# Tenant Schemas
class TenantCreate(BaseModel):
    full_name: str
    shop_id: int
    mobile_number: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    deposit_amount: Decimal = 0
    monthly_rent: Decimal
    rent_due_date: int = 5
    agreement_start_date: date
    agreement_end_date: date
    notes: Optional[str] = None
    username: str
    password: str


class TenantUpdate(BaseModel):
    full_name: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    monthly_rent: Optional[Decimal] = None
    rent_due_date: Optional[int] = None
    agreement_end_date: Optional[date] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class TenantResponse(BaseModel):
    id: int
    tenant_id: str
    full_name: str
    shop_id: int
    shop_number: Optional[str] = None
    shop_name: Optional[str] = None
    mobile_number: str
    email: Optional[str] = None
    address: Optional[str] = None
    deposit_amount: Decimal
    monthly_rent: Decimal
    rent_due_date: int
    agreement_start_date: date
    agreement_end_date: date
    notes: Optional[str] = None
    username: str
    is_active: bool
    current_balance: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


# Payment Schemas
class PaymentCreate(BaseModel):
    tenant_id: int
    payment_date: datetime
    amount: Decimal
    payment_type: PaymentTypeEnum
    payment_method: PaymentMethodEnum
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    receipt_number: str
    tenant_id: int
    payment_date: datetime
    amount: Decimal
    payment_type: PaymentTypeEnum
    payment_method: PaymentMethodEnum
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Bill Schemas
class BillCreate(BaseModel):
    tenant_id: int
    bill_type: BillTypeEnum
    bill_month: date
    amount: Decimal
    due_date: date
    notes: Optional[str] = None


class BillResponse(BaseModel):
    id: int
    tenant_id: int
    bill_type: BillTypeEnum
    bill_month: date
    amount: Decimal
    due_date: date
    notes: Optional[str] = None
    is_paid: bool
    paid_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# Ledger Schemas
class LedgerEntryResponse(BaseModel):
    id: int
    date: datetime
    description: str
    debit: Decimal
    credit: Decimal
    balance: Decimal

    class Config:
        from_attributes = True


# Shop Schemas
class ShopCreate(BaseModel):
    shop_number: str
    shop_name: str
    area: Optional[float] = None
    monthly_rent: Decimal


class ShopResponse(BaseModel):
    id: int
    shop_number: str
    shop_name: str
    area: Optional[float] = None
    monthly_rent: Decimal
    status: str

    class Config:
        from_attributes = True