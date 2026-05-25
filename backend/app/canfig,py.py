from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "shop_rent_db"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # App
    APP_NAME: str = "Shop Rent Management System"
    DEBUG: bool = False

    # Admin
    ADMIN_EMAIL: str = "admin@shoprent.com"
    ADMIN_PASSWORD: str = "Admin@123"

    class Config:
        env_file = ".env"


settings = Settings()