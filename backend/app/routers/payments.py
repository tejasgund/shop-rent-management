from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import SessionLocal
from app.models import Payment, Tenant, LedgerEntry, Admin
from app.schemas import PaymentCreate, PaymentResponse
from app.routers.auth import get_current_user
from app.utils.helpers import generate_receipt_number, update_tenant_balance

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
        payment_data: PaymentCreate,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if current_user["type"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    tenant = db.query(Tenant).filter(Tenant.id == payment_data.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Create payment
    payment = Payment(
        receipt_number=generate_receipt_number(),
        tenant_id=payment_data.tenant_id,
        payment_date=payment_data.payment_date,
        amount=payment_data.amount,
        payment_type=payment_data.payment_type,
        payment_method=payment_data.payment_method,
        reference_number=payment_data.reference_number,
        notes=payment_data.notes,
        created_by=current_user["user"].id
    )

    db.add(payment)

    # Update ledger
    ledger = LedgerEntry(
        tenant_id=tenant.id,
        date=datetime.now(),
        description=f"Payment received - {payment_data.payment_type.value} - Receipt: {payment.receipt_number}",
        debit=payment_data.amount,
        credit=0,
        balance=tenant.current_balance - payment_data.amount,
        reference_type="payment",
        reference_id=payment.id
    )
    db.add(ledger)

    # Update tenant balance
    tenant.current_balance -= payment_data.amount

    db.commit()
    db.refresh(payment)

    return payment


@router.get("/", response_model=List[PaymentResponse])
async def get_payments(
        tenant_id: Optional[int] = None,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    query = db.query(Payment)

    if tenant_id:
        if current_user["type"] == "tenant" and current_user["user"].id != tenant_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        query = query.filter(Payment.tenant_id == tenant_id)

    payments = query.order_by(Payment.payment_date.desc()).offset(skip).limit(limit).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
        payment_id: int,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if current_user["type"] == "tenant" and current_user["user"].id != payment.tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return payment
