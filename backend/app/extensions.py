from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from redis import Redis

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

redis_client = None


def init_redis(app):
    global redis_client
    redis_client = Redis.from_url(app.config["REDIS_URL"], decode_responses=True)
