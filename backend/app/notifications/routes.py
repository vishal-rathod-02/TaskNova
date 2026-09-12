from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import Notification
from ..utils.auth import require_current_user

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@notifications_bp.get("")
@jwt_required()
def list_notifications():
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    query = Notification.query.filter_by(user_id=user.id)
    if request.args.get("unread_only", "false").lower() == "true":
        query = query.filter_by(is_read=False)
    kind = request.args.get("kind")
    if kind:
        query = query.filter_by(kind=kind)
    query = query.order_by(Notification.created_at.desc())

    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 20, type=int), 1), 100)
    result = query.paginate(page=page, per_page=per_page, error_out=False)
    unread_count = Notification.query.filter_by(user_id=user.id, is_read=False).count()
    return jsonify(
        {
            "notifications": [item.to_dict() for item in result.items],
            "unread_count": unread_count,
            "pagination": {"page": result.page, "per_page": result.per_page, "total": result.total, "pages": result.pages},
        }
    )


@notifications_bp.post("/<int:notification_id>/read")
@jwt_required()
def mark_notification_read(notification_id):
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
    if not notification:
        return jsonify({"message": "Notification not found."}), 404
    notification.is_read = True
    db.session.commit()
    return jsonify({"notification": notification.to_dict()})


@notifications_bp.post("/read-all")
@jwt_required()
def mark_all_notifications_read():
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    Notification.query.filter_by(user_id=user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"message": "All notifications marked as read."})
