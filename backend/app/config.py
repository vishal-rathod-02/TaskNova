import os
from datetime import timedelta

from dotenv import load_dotenv

# Load local environment overrides if present, then standard .env
load_dotenv(".env.local")
load_dotenv(".env")



def _origins():
    value = os.getenv("CORS_ORIGINS", "").strip()
    if not value or value == "*":
        return [r".*"]
    items = [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip().rstrip("/")]
    if "*" in items:
        return [r".*"]
    return items



def _database_url():
    url = os.getenv("DATABASE_URL", "sqlite:///tasknova.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_ACCESS_TTL", "15")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TTL_DAYS", "7")))

    CORS_ORIGINS = _origins()
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    DASHBOARD_CACHE_TTL = int(os.getenv("DASHBOARD_CACHE_TTL", "60"))
    ADMIN_DASHBOARD_CACHE_TTL = int(os.getenv("ADMIN_DASHBOARD_CACHE_TTL", "120"))
    REMINDER_WINDOW_HOURS = int(os.getenv("REMINDER_WINDOW_HOURS", "24"))
    AUTO_CREATE_DB = os.getenv("AUTO_CREATE_DB", "true").lower() == "true"

    # Mail / SMTP Notification Settings
    MAIL_ENABLED = os.getenv("MAIL_ENABLED", "false").lower() == "true"
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "TaskNova <[EMAIL_ADDRESS]")
    APP_FRONTEND_URL = os.getenv("APP_FRONTEND_URL", "https://localhost:5173")

