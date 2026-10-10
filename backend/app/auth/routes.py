from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token, get_jwt, jwt_required

from ..extensions import add_token_to_blocklist, db
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
    user.ensure_calendar_token()
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
    user.ensure_calendar_token()
    db.session.commit()
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


@auth_bp.post("/logout")
@jwt_required(verify_type=False)
def logout():
    jwt_data = get_jwt()
    jti = jwt_data.get("jti")
    if jti:
        add_token_to_blocklist(jti)

    payload = request.get_json(silent=True) or {}
    extra_token = payload.get("refresh_token")
    if extra_token:
        try:
            decoded = decode_token(extra_token)
            extra_jti = decoded.get("jti")
            if extra_jti:
                add_token_to_blocklist(extra_jti)
        except Exception:
            pass

    return jsonify({"message": "Successfully logged out and session revoked."})


@auth_bp.patch("/preferences")
@jwt_required()
def update_preferences():
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    payload = request.get_json(silent=True) or {}
    if "email_digest_enabled" in payload:
        user.email_digest_enabled = bool(payload["email_digest_enabled"])
    if "email_alerts_enabled" in payload:
        user.email_alerts_enabled = bool(payload["email_alerts_enabled"])
    db.session.commit()
    return jsonify({"user": user.to_dict(), "message": "Notification preferences updated."})


@auth_bp.post("/calendar-token/regenerate")
@jwt_required()
def regenerate_calendar_token():
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    token = user.regenerate_calendar_token()
    db.session.commit()
    return jsonify({"calendar_token": token, "user": user.to_dict()})

