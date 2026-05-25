from passlib.context import CryptContext
import random
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def generate_tenant_id():
    """Generate unique tenant ID"""
    prefix = "TEN"
    random_digits = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{random_digits}"