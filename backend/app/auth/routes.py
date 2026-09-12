from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required

from ..extensions import db
from ..models import User
from ..utils.auth import require_current_user
from ..utils.rate_limit import rate_limit
from ..utils.validation import validate_registration, validation_error

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _tokens_for(user):
    claims = {"role": user.role}
    return {
        "access_token": create_access_token(identity=str(user.id), additional_claims=claims),
        "refresh_token": create_refresh_token(identity=str(user.id)),
    }


@auth_bp.post("/register")
@rate_limit(limit=5, window_seconds=60)
def register():
    data, errors = validate_registration(request.get_json(silent=True) or {})
    if errors:
        body, status = validation_error(errors)
        return jsonify(body), status
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email is already registered."}), 409

    user = User(full_name=data["full_name"], email=data["email"], role="user")
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"user": user.to_dict()}), 201


@auth_bp.post("/login")
@rate_limit(limit=10, window_seconds=60)
def login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).lower().strip()
    password = str(payload.get("password", ""))
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password."}), 401
    if user.is_blocked:
        return jsonify({"message": "Your account is blocked. Contact an administrator."}), 403
    return jsonify({**_tokens_for(user), "user": user.to_dict()})


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    return jsonify({"access_token": create_access_token(identity=str(user.id), additional_claims={"role": user.role})})


@auth_bp.get("/me")
@jwt_required()
def me():
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    return jsonify({"user": user.to_dict()})
