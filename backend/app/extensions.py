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
