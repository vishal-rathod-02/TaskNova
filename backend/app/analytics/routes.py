from datetime import timedelta

from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from ..extensions import db
from ..models import ActivityLog, Project, Task, User
from ..models.time import utcnow
from ..utils.auth import require_current_user, role_required
from ..utils.cache import get_cached_json, set_cached_json

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


def _breakdown(query, field):
    return [{"label": label, "count": count} for label, count in query.with_entities(field, func.count(Task.id)).group_by(field).all()]


def _personal_stats(user):
    base_query = Task.query.join(Project).filter(Project.owner_id == user.id)
    total_tasks = base_query.count()
    completed_tasks = base_query.filter(Task.status == "done").count()
    overdue_tasks = base_query.filter(Task.due_date.isnot(None), Task.due_date < utcnow(), Task.status != "done").count()
    status_breakdown = _breakdown(base_query, Task.status)
    priority_breakdown = _breakdown(base_query, Task.priority)

    start = utcnow().date() - timedelta(days=6)
    completion_rows = (
        db.session.query(func.date(ActivityLog.created_at), func.count(ActivityLog.id))
        .join(Task, ActivityLog.task_id == Task.id)
        .join(Project, Task.project_id == Project.id)
        .filter(Project.owner_id == user.id, ActivityLog.action == "status_changed", ActivityLog.created_at >= start)
        .group_by(func.date(ActivityLog.created_at))
        .all()
    )
    completion_by_day = {str(day): count for day, count in completion_rows}
    trend = []
    for offset in range(7):
        day = start + timedelta(days=offset)
        trend.append({"date": day.isoformat(), "count": completion_by_day.get(day.isoformat(), 0)})

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": round((completed_tasks / total_tasks) * 100, 1) if total_tasks else 0,
        "status_breakdown": status_breakdown,
        "priority_breakdown": priority_breakdown,
        "completion_trend": trend,
    }


def _admin_stats():
    now = utcnow()
    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(status="done").count()
    return {
        "total_users": User.query.count(),
        "active_users": User.query.filter_by(is_blocked=False).count(),
        "blocked_users": User.query.filter_by(is_blocked=True).count(),
        "total_projects": Project.query.count(),
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": Task.query.filter(Task.due_date.isnot(None), Task.due_date < now, Task.status != "done").count(),
        "activity_last_24h": ActivityLog.query.filter(ActivityLog.created_at >= now - timedelta(hours=24)).count(),
    }


@analytics_bp.get("/me")
@jwt_required()
def personal_dashboard():
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    key = f"dashboard:user:{user.id}"
    cached = get_cached_json(key)
    if cached is not None:
        return jsonify({"stats": cached, "source": "cache"})
    stats = _personal_stats(user)
    set_cached_json(key, stats, current_app.config["DASHBOARD_CACHE_TTL"])
    return jsonify({"stats": stats, "source": "database"})


@analytics_bp.get("/admin")
@role_required("admin")
def admin_dashboard():
    key = "dashboard:admin:global"
    cached = get_cached_json(key)
    if cached is not None:
        return jsonify({"stats": cached, "source": "cache"})
    stats = _admin_stats()
    set_cached_json(key, stats, current_app.config["ADMIN_DASHBOARD_CACHE_TTL"])
    return jsonify({"stats": stats, "source": "database"})
