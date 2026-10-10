import logging
from collections import defaultdict, deque
from functools import wraps
from threading import Lock
from time import monotonic

from flask import current_app, jsonify, make_response, request

from .. import extensions

logger = logging.getLogger(__name__)

_local_attempts = defaultdict(deque)
_local_lock = Lock()


def _get_client_ip():
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def reset_rate_limits():
    """Helper for test suites to reset local rate limit counters."""
    with _local_lock:
        _local_attempts.clear()


def rate_limit(limit=10, window_seconds=60, key_prefix=None):
    """Distributed Redis-backed rate limiter with seamless in-memory fallback.

    - Uses Redis atomic counter with TTL for multi-worker production environments.
    - Gracefully degrades to thread-safe local sliding window when Redis is offline.
    - Injects standard RFC rate limiting headers: X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            # Bypass during automated test runs unless explicitly testing rate limits
            if current_app.config.get("TESTING") and not current_app.config.get("TESTING_RATE_LIMIT"):
                return fn(*args, **kwargs)

            ip = _get_client_ip()
            prefix = key_prefix or fn.__name__
            redis_client = extensions.redis_client

            # 1. Try Distributed Redis
            if redis_client:
                try:
                    redis_key = f"ratelimit:{prefix}:{ip}"
                    pipe = redis_client.pipeline()
                    pipe.incr(redis_key)
                    pipe.ttl(redis_key)
                    current_count, ttl = pipe.execute()

                    if current_count == 1 or ttl < 0:
                        redis_client.expire(redis_key, window_seconds)
                        ttl = window_seconds

                    remaining = max(0, limit - current_count)

                    if current_count > limit:
                        retry_after = max(1, ttl)
                        response = make_response(
                            jsonify(
                                {
                                    "message": "Too many requests. Please slow down and try again shortly.",
                                    "retry_after": retry_after,
                                }
                            ),
                            429,
                        )
                        response.headers["Retry-After"] = str(retry_after)
                        response.headers["X-RateLimit-Limit"] = str(limit)
                        response.headers["X-RateLimit-Remaining"] = "0"
                        return response

                    result = fn(*args, **kwargs)
                    resp = make_response(result)
                    resp.headers["X-RateLimit-Limit"] = str(limit)
                    resp.headers["X-RateLimit-Remaining"] = str(remaining)
                    return resp
                except Exception as exc:
                    logger.debug("Redis rate limiting failover: %s", exc)

            # 2. In-memory Fallback (thread-safe sliding window)
            key = f"{prefix}:{ip}"
            now = monotonic()
            with _local_lock:
                attempts = _local_attempts[key]
                while attempts and attempts[0] <= now - window_seconds:
                    attempts.popleft()

                if len(attempts) >= limit:
                    oldest = attempts[0] if attempts else now
                    retry_after = max(1, int(window_seconds - (now - oldest)))
                    response = make_response(
                        jsonify(
                            {
                                "message": "Too many requests. Please slow down and try again shortly.",
                                "retry_after": retry_after,
                            }
                        ),
                        429,
                    )
                    response.headers["Retry-After"] = str(retry_after)
                    response.headers["X-RateLimit-Limit"] = str(limit)
                    response.headers["X-RateLimit-Remaining"] = "0"
                    return response

                attempts.append(now)
                remaining = max(0, limit - len(attempts))

            result = fn(*args, **kwargs)
            resp = make_response(result)
            resp.headers["X-RateLimit-Limit"] = str(limit)
            resp.headers["X-RateLimit-Remaining"] = str(remaining)
            return resp

        return wrapped

    return decorator
