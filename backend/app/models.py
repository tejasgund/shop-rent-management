from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum, Date, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class PaymentType(str, enum.Enum):
    MONTHLY_RENT = "monthly_rent"
    DEPOSIT = "deposit"
    ELECTRICITY = "electricity"
    MAINTENANCE = "maintenance"
    PENALTY = "penalty"
    OTHER = "other"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    UPI = "upi"
    CHEQUE = "cheque"


class BillType(str, enum.Enum):
    ELECTRICITY = "electricity"
    WATER = "water"
    MAINTENANCE = "maintenance"
    OTHER = "other"


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default="admin")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    shop_number = Column(String(50), unique=True, nullable=False, index=True)
    shop_name = Column(String(255), nullable=False)
    area = Column(Float)
    monthly_rent = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(50), default="vacant")  # occupied, vacant, maintenance
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenants = relationship("Tenant", back_populates="shop")


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=False)
    mobile_number = Column(String(20), nullable=False, index=True)
    email = Column(String(255), index=True)
    address = Column(Text)
    deposit_amount = Column(DECIMAL(10, 2), default=0)
    monthly_rent = Column(DECIMAL(10, 2), nullable=False)
    rent_due_date = Column(Integer, default=5)  # Day of month
    agreement_start_date = Column(Date, nullable=False)
    agreement_end_date = Column(Date, nullable=False)
    notes = Column(Text)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    current_balance = Column(DECIMAL(10, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))  # Soft delete

    # Relationships
    shop = relationship("Shop", back_populates="tenants")
    payments = relationship("Payment", back_populates="tenant", cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="tenant", cascade="all, delete-orphan")
    ledger_entries = relationship("LedgerEntry", back_populates="tenant", cascade="all, delete-orphan")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    payment_date = Column(DateTime(timezone=True), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    reference_number = Column(String(100))
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey("admins.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="payments")
    admin = relationship("Admin")


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    bill_type = Column(Enum(BillType), nullable=False)
    bill_month = Column(Date, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    notes = Column(Text)
    is_paid = Column(Boolean, default=False)
    paid_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="bills")


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    description = Column(String(500), nullable=False)
    debit = Column(DECIMAL(10, 2), default=0)
    credit = Column(DECIMAL(10, 2), default=0)
    balance = Column(DECIMAL(10, 2), nullable=False)
    reference_type = Column(String(50))  # payment, bill, adjustment
    reference_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="ledger_entries")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_type = Column(String(50))  # admin, tenant
    action = Column(String(100), nullable=False)
    description = Column(Text)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())