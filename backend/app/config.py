import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _origins():
    value = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    # Browsers send `Origin` without a trailing slash, so normalize entries:
    # `http://localhost:5173/` would otherwise never match and produce
    # responses with no Access-Control-Allow-Origin header at all.
    return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip().rstrip("/")]


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
