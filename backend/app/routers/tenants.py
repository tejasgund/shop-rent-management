from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from app.database import SessionLocal
from app.models import Tenant, Shop, LedgerEntry
from app.schemas import TenantCreate, TenantUpdate, TenantResponse
from app.routers.auth import get_current_user
from app.utils.auth import get_password_hash, generate_tenant_id
from datetime import datetime

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
        tenant_data: TenantCreate,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Check if user is admin
    if current_user["type"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if username exists
    existing = db.query(Tenant).filter(Tenant.username == tenant_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if shop exists and is vacant
    shop = db.query(Shop).filter(Shop.id == tenant_data.shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    if shop.status != "vacant":
        raise HTTPException(status_code=400, detail="Shop is already occupied")

    # Create tenant
    tenant = Tenant(
        tenant_id=generate_tenant_id(),
        full_name=tenant_data.full_name,
        shop_id=tenant_data.shop_id,
        mobile_number=tenant_data.mobile_number,
        email=tenant_data.email,
        address=tenant_data.address,
        deposit_amount=tenant_data.deposit_amount,
        monthly_rent=tenant_data.monthly_rent,
        rent_due_date=tenant_data.rent_due_date,
        agreement_start_date=tenant_data.agreement_start_date,
        agreement_end_date=tenant_data.agreement_end_date,
        notes=tenant_data.notes,
        username=tenant_data.username,
        password_hash=get_password_hash(tenant_data.password),
        current_balance=0
    )

    db.add(tenant)

    # Update shop status
    shop.status = "occupied"

    # Add initial ledger entry for deposit
    if tenant_data.deposit_amount > 0:
        ledger = LedgerEntry(
            tenant_id=tenant.id,
            date=datetime.now(),
            description="Security Deposit Received",
            credit=tenant_data.deposit_amount,
            debit=0,
            balance=tenant_data.deposit_amount,
            reference_type="deposit"
        )
        db.add(ledger)

    db.commit()
    db.refresh(tenant)

    return tenant


@router.get("/", response_model=List[TenantResponse])
async def get_tenants(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        search: Optional[str] = None,
        status: Optional[str] = None,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    query = db.query(Tenant).filter(Tenant.deleted_at.is_(None))

    if search:
        query = query.filter(
            or_(
                Tenant.full_name.contains(search),
                Tenant.username.contains(search),
                Tenant.mobile_number.contains(search),
                Tenant.tenant_id.contains(search)
            )
        )

    if status:
        is_active = status == "active"
        query = query.filter(Tenant.is_active == is_active)

    tenants = query.offset(skip).limit(limit).all()

    # Load shop info
    for tenant in tenants:
        if tenant.shop:
            tenant.shop_number = tenant.shop.shop_number
            tenant.shop_name = tenant.shop.shop_name

    return tenants


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
        tenant_id: int,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if current_user["type"] == "tenant" and current_user["user"].id != tenant_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id, Tenant.deleted_at.is_(None)).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if tenant.shop:
        tenant.shop_number = tenant.shop.shop_number
        tenant.shop_name = tenant.shop.shop_name

    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
        tenant_id: int,
        tenant_data: TenantUpdate,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if current_user["type"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id, Tenant.deleted_at.is_(None)).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    for field, value in tenant_data.dict(exclude_unset=True).items():
        setattr(tenant, field, value)

    db.commit()
    db.refresh(tenant)

    if tenant.shop:
        tenant.shop_number = tenant.shop.shop_number
        tenant.shop_name = tenant.shop.shop_name

    return tenant


@router.delete("/{tenant_id}")
async def delete_tenant(
        tenant_id: int,
        current_user=Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if current_user["type"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id, Tenant.deleted_at.is_(None)).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Soft delete
    tenant.deleted_at = datetime.now()
    tenant.is_active = False

    # Update shop status
    if tenant.shop:
        tenant.shop.status = "vacant"

    db.commit()

    return {"message": "Tenant deleted successfully"}