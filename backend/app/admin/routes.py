from flask import Blueprint, jsonify, request

from ..extensions import db
from ..models import ActivityLog, DailyReport, Notification, Project, Task, User
from ..utils.auth import require_current_user, role_required
from ..utils.cache import invalidate_dashboard_cache

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/users")
@role_required("admin")
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({"users": [user.to_dict() for user in users]})


@admin_bp.patch("/users/<int:user_id>/block")
@role_required("admin")
def update_user_block(user_id):
    current_admin = require_current_user()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found."}), 404
    if current_admin and user.id == current_admin.id:
        return jsonify({"message": "You cannot block your own active administrator account."}), 400
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload.get("is_blocked"), bool):
        return jsonify({"message": "Validation failed", "errors": {"is_blocked": "Provide a boolean value."}}), 422
    user.is_blocked = payload["is_blocked"]
    db.session.commit()
    invalidate_dashboard_cache(user.id)
    return jsonify({"user": user.to_dict()})


@admin_bp.delete("/users/<int:user_id>")
@role_required("admin")
def delete_user(user_id):
    current_admin = require_current_user()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"message": "User not found."}), 404
    if current_admin and user.id == current_admin.id:
        return jsonify({"message": "You cannot delete your own active administrator account."}), 400
    project_ids = [project.id for project in Project.query.filter_by(owner_id=user.id).all()]
    if project_ids:
        task_ids = [task.id for task in Task.query.filter(Task.project_id.in_(project_ids)).all()]
        if task_ids:
            ActivityLog.query.filter(ActivityLog.task_id.in_(task_ids)).delete(synchronize_session=False)
            Task.query.filter(Task.id.in_(task_ids)).delete(synchronize_session=False)
        Project.query.filter(Project.id.in_(project_ids)).delete(synchronize_session=False)
    # A user may have activity on tasks that were later reassigned in a future extension.
    ActivityLog.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    Notification.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    DailyReport.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    db.session.delete(user)
    db.session.commit()
    invalidate_dashboard_cache()
    return "", 204
