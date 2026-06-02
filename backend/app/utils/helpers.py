from sqlalchemy.orm import Session
from app.models import Tenant, LedgerEntry
from datetime import datetime
import random
import string


def generate_receipt_number():
    """Generate unique receipt number"""
    prefix = "RCP"
    date_str = datetime.now().strftime("%Y%m%d")
    random_digits vi = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{date_str}{random_digits}"


def update_tenant_balance(tenant_id: int, db: Session):
    """Recalculate tenant balance from ledger entries"""
    ledger_entries = db.query(LedgerEntry).filter(
        LedgerEntry.tenant_id == tenant_id
    ).order_by(LedgerEntry.date).all()

    balance = 0
    for entry in ledger_entries:
        balance += entry.credit - entry.debit
        entry.balance = balance

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if tenant:
        tenant.current_balance = balance

    db.commit()
    return balance