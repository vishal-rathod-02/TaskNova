from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import ActivityLog, Project, Task
from ..utils.activity import log_task_activity
from ..utils.auth import require_current_user
from ..utils.cache import invalidate_dashboard_cache
from ..utils.validation import validation_error
from .service import apply_task_filters, create_task, owned_project, owned_task, update_task

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


def _pagination(query):
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 50, type=int), 1), 100)
    result = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "tasks": [task.to_dict() for task in result.items],
        "pagination": {"page": result.page, "per_page": result.per_page, "total": result.total, "pages": result.pages},
    }


@tasks_bp.get("")
@jwt_required()
def list_tasks():
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    query = Task.query.join(Project).filter(Project.owner_id == user.id)
    project_id = request.args.get("project_id", type=int)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    query = apply_task_filters(query, request.args).order_by(Task.due_date.is_(None), Task.due_date.asc(), Task.created_at.desc())
    return jsonify(_pagination(query))


@tasks_bp.post("")
@jwt_required()
def create_task_route():
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    payload = request.get_json(silent=True) or {}
    project_id = payload.get("project_id")
    try:
        project_id = int(project_id)
    except (TypeError, ValueError):
        return jsonify({"message": "Validation failed", "errors": {"project_id": "Select a valid project."}}), 422
    project, error_response = owned_project(user, project_id)
    if error_response:
        return error_response
    task, errors = create_task(user, project, payload)
    if errors:
        body, status = validation_error(errors)
        return jsonify(body), status
    invalidate_dashboard_cache(user.id)
    return jsonify({"task": task.to_dict()}), 201


@tasks_bp.get("/<int:task_id>")
@jwt_required()
def get_task(task_id):
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    task, error_response = owned_task(user, task_id)
    if error_response:
        return error_response
    return jsonify({"task": task.to_dict()})


@tasks_bp.put("/<int:task_id>")
@jwt_required()
def update_task_route(task_id):
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    task, error_response = owned_task(user, task_id)
    if error_response:
        return error_response
    task, errors = update_task(user, task, request.get_json(silent=True) or {})
    if errors:
        body, status = validation_error(errors)
        return jsonify(body), status
    invalidate_dashboard_cache(user.id)
    return jsonify({"task": task.to_dict()})


@tasks_bp.post("/<int:task_id>/complete")
@jwt_required()
def complete_task(task_id):
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    task, error_response = owned_task(user, task_id)
    if error_response:
        return error_response
    if task.status != "done":
        previous_status = task.status
        task.status = "done"
        log_task_activity(task.id, user.id, "status_changed", {"changes": {"status": {"from": previous_status, "to": "done"}}})
        db.session.commit()
        invalidate_dashboard_cache(user.id)
    return jsonify({"task": task.to_dict()})


@tasks_bp.delete("/<int:task_id>")
@jwt_required()
def delete_task(task_id):
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    task, error_response = owned_task(user, task_id)
    if error_response:
        return error_response
    log_task_activity(task.id, user.id, "deleted", {"before": {"title": task.title, "status": task.status}})
    db.session.delete(task)
    db.session.commit()
    invalidate_dashboard_cache(user.id)
    return "", 204


@tasks_bp.get("/<int:task_id>/activity")
@jwt_required()
def task_activity(task_id):
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    task, error_response = owned_task(user, task_id)
    if error_response:
        return error_response
    logs = ActivityLog.query.filter_by(task_id=task.id).order_by(ActivityLog.created_at.desc()).all()
    return jsonify({"activity": [log.to_dict() for log in logs]})
