from flask import Blueprint, jsonify, request

from sqlalchemy import func, or_

from ..extensions import db
from ..models import ActivityLog, DailyReport, Notification, Project, Task, TimetableAllocation, TimetableSlot, User
from ..timetable.service import TEMPLATE_META, TEMPLATE_SLOTS, TEMPLATES, template_states
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
    # Timetable data is user-owned: drop allocations touching the user's slots or
    # tasks first (bulk deletes bypass ORM cascades), then the slots themselves.
    slot_ids = [slot.id for slot in TimetableSlot.query.filter_by(user_id=user.id).all()]
    remaining_task_ids = [task.id for task in Task.query.filter_by(created_by=user.id).all()]
    allocation_filter = []
    if slot_ids:
        allocation_filter.append(TimetableAllocation.slot_id.in_(slot_ids))
    if remaining_task_ids:
        allocation_filter.append(TimetableAllocation.task_id.in_(remaining_task_ids))
    if allocation_filter:
        TimetableAllocation.query.filter(or_(*allocation_filter)).delete(synchronize_session=False)
    if slot_ids:
        TimetableSlot.query.filter(TimetableSlot.id.in_(slot_ids)).delete(synchronize_session=False)
    # A user may have activity on tasks that were later reassigned in a future extension.
    ActivityLog.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    Notification.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    DailyReport.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    db.session.delete(user)
    db.session.commit()
    invalidate_dashboard_cache()
    return "", 204


@admin_bp.get("/timetable/templates")
@role_required("admin")
def list_routine_templates():
    """Governor switchboard: persona templates with live adoption (aggregate counts only)."""
    states = template_states()
    templates = []
    for name in TEMPLATES:
        meta = TEMPLATE_META[name]
        active_blocks = TimetableSlot.query.filter_by(source_template=name).count()
        adopters = (
            db.session.query(func.count(func.distinct(TimetableSlot.user_id)))
            .filter(TimetableSlot.source_template == name)
            .scalar()
            or 0
        )
        templates.append(
            states[name].to_dict(
                {
                    "label": meta["label"],
                    "description": meta["description"],
                    "blocks_per_week": len(TEMPLATE_SLOTS[name]) * 5,
                    "active_blocks": active_blocks,
                    "adopters": adopters,
                }
            )
        )
    return jsonify({"templates": templates})


@admin_bp.patch("/timetable/templates/<string:name>")
@role_required("admin")
def update_routine_template(name):
    name = str(name).strip().lower()
    if name not in TEMPLATES:
        return jsonify({"message": "Routine template not found."}), 404
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload.get("is_enabled"), bool):
        return jsonify({"message": "Validation failed", "errors": {"is_enabled": "Provide a boolean value."}}), 422
    states = template_states()
    states[name].is_enabled = payload["is_enabled"]
    db.session.commit()
    return jsonify({"template": states[name].to_dict({"label": TEMPLATE_META[name]["label"]})})
