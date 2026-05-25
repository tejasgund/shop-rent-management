from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from app.database import engine, SessionLocal, init_database
from app.routers import auth, tenants, payments, bills, reports, dashboard
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    await init_database()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Shop Rent Management System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["Tenants"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(bills.router, prefix="/api/bills", tags=["Bills"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    return {"message": "Shop Rent Management System API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}