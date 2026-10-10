from threading import Lock

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from redis.exceptions import RedisError

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

redis_client = None

_in_memory_blocklist = set()
_blocklist_lock = Lock()


def add_token_to_blocklist(jti, expires_in_seconds=604800):
    """Revoke a JWT token by adding its unique jti to Redis or local blocklist."""
    global redis_client
    if redis_client:
        try:
            redis_client.setex(f"jwt:blocklist:{jti}", expires_in_seconds, "1")
            return
        except Exception:
            pass
    with _blocklist_lock:
        _in_memory_blocklist.add(jti)


def clear_in_memory_blocklist():
    """Helper for unit tests."""
    with _blocklist_lock:
        _in_memory_blocklist.clear()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload.get("jti")
    if not jti:
        return False
    global redis_client
    if redis_client:
        try:
            val = redis_client.get(f"jwt:blocklist:{jti}")
            if val is not None:
                return True
        except Exception:
            pass
    with _blocklist_lock:
        return jti in _in_memory_blocklist


def init_redis(app):
    global redis_client
    client = Redis.from_url(app.config["REDIS_URL"], decode_responses=True)
    try:
        client.ping()
        redis_client = client
        app.logger.info("Redis cache connected")
    except RedisError:
        redis_client = None
        app.logger.warning("Redis unavailable; cache and Celery-backed features will degrade gracefully")

