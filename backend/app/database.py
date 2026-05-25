from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


async def init_database():
    """Initialize database - create tables and default admin"""
    try:
        # Create tables
        from app.models import Admin, Tenant, Payment, Bill, LedgerEntry, Shop, AuditLog
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Create default admin if not exists
        db = SessionLocal()
        try:
            from app.utils.auth import get_password_hash
            admin = db.query(Admin).filter(Admin.email == settings.ADMIN_EMAIL).first()
            if not admin:
                admin = Admin(
                    email=settings.ADMIN_EMAIL,
                    password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                    full_name="System Admin",
                    is_active=True,
                    role="admin"
                )
                db.add(admin)
                db.commit()
                logger.info(f"Default admin created: {settings.ADMIN_EMAIL}")
            else:
                logger.info("Admin user already exists")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise