from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from .models import User


def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            user = User.query.get(identity)
            if not user or user.is_blocked:
                return jsonify({"message": "Unauthorized or blocked user"}), 403
            if user.role not in roles:
                return jsonify({"message": "Insufficient permissions"}), 403
            return fn(*args, **kwargs)

        return decorator

    return wrapper
