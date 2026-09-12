from collections import defaultdict, deque
from functools import wraps
from threading import Lock
from time import monotonic

from flask import jsonify, request

_attempts = defaultdict(deque)
_lock = Lock()


def rate_limit(limit, window_seconds):
    """A lightweight process-local guard for credential endpoints in development deployments."""

    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            key = f"{fn.__name__}:{request.remote_addr or 'unknown'}"
            now = monotonic()
            with _lock:
                attempts = _attempts[key]
                while attempts and attempts[0] <= now - window_seconds:
                    attempts.popleft()
                if len(attempts) >= limit:
                    return jsonify({"message": "Too many attempts. Please try again shortly."}), 429
                attempts.append(now)
            return fn(*args, **kwargs)

        return decorated

    return wrapper
