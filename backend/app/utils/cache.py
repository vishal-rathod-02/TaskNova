import json

from redis.exceptions import RedisError

from .. import extensions


def get_cached_json(key):
    if not extensions.redis_client:
        return None
    try:
        value = extensions.redis_client.get(key)
        return json.loads(value) if value else None
    except (RedisError, json.JSONDecodeError):
        return None


def set_cached_json(key, value, ttl):
    if not extensions.redis_client:
        return
    try:
        extensions.redis_client.setex(key, ttl, json.dumps(value))
    except RedisError:
        pass


def delete_cached(*keys):
    if not extensions.redis_client or not keys:
        return
    try:
        extensions.redis_client.delete(*keys)
    except RedisError:
        pass


def invalidate_dashboard_cache(user_id=None):
    keys = ["dashboard:admin:global"]
    if user_id:
        keys.append(f"dashboard:user:{user_id}")
    delete_cached(*keys)
