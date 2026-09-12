from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from ..extensions import db
from ..models import User


def get_current_user():
    identity = get_jwt_identity()
    if not identity:
        return None
    return db.session.get(User, int(identity))


def require_current_user():
    user = get_current_user()
    if not user or user.is_blocked:
        return None
    return user


def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user = require_current_user()
            if not user:
                return jsonify({"message": "Unauthorized or blocked user"}), 403
            if user.role not in roles:
                return jsonify({"message": "Insufficient permissions"}), 403
            return fn(*args, **kwargs)

        return decorator

    return wrapper
