from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import Project, Task
from ..utils.auth import require_current_user
from ..utils.cache import invalidate_dashboard_cache
from ..utils.validation import validation_error, validate_project
from ..tasks.service import apply_task_filters, create_task, owned_project

projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")


def _current_user_or_error():
    user = require_current_user()
    if not user:
        return None, (jsonify({"message": "Unauthorized or blocked user."}), 403)
    return user, None


@projects_bp.get("")
@jwt_required()
def list_projects():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    projects = Project.query.filter_by(owner_id=user.id).order_by(Project.created_at.desc()).all()
    return jsonify({"projects": [project.to_dict(include_task_count=True) for project in projects]})


@projects_bp.post("")
@jwt_required()
def create_project():
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    data, errors = validate_project(request.get_json(silent=True) or {})
    if errors:
        body, status = validation_error(errors)
        return jsonify(body), status
    project = Project(name=data["name"], description=data["description"], owner_id=user.id)
    db.session.add(project)
    db.session.commit()
    invalidate_dashboard_cache(user.id)
    return jsonify({"project": project.to_dict(include_task_count=True)}), 201


@projects_bp.get("/<int:project_id>")
@jwt_required()
def get_project(project_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    project, error_response = owned_project(user, project_id)
    if error_response:
        return error_response
    return jsonify({"project": project.to_dict(include_task_count=True)})


@projects_bp.put("/<int:project_id>")
@jwt_required()
def update_project(project_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    project, error_response = owned_project(user, project_id)
    if error_response:
        return error_response
    data, errors = validate_project(request.get_json(silent=True) or {})
    if errors:
        body, status = validation_error(errors)
        return jsonify(body), status
    project.name = data["name"]
    project.description = data["description"]
    db.session.commit()
    invalidate_dashboard_cache(user.id)
    return jsonify({"project": project.to_dict(include_task_count=True)})


@projects_bp.delete("/<int:project_id>")
@jwt_required()
def delete_project(project_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    project, error_response = owned_project(user, project_id)
    if error_response:
        return error_response
    db.session.delete(project)
    db.session.commit()
    invalidate_dashboard_cache(user.id)
    return "", 204


@projects_bp.get("/<int:project_id>/tasks")
@jwt_required()
def list_project_tasks(project_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    project, error_response = owned_project(user, project_id)
    if error_response:
        return error_response
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 50, type=int), 1), 100)
    query = apply_task_filters(Task.query.filter_by(project_id=project.id), request.args).order_by(Task.due_date.is_(None), Task.due_date.asc())
    result = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(
        {
            "tasks": [task.to_dict() for task in result.items],
            "pagination": {"page": result.page, "per_page": result.per_page, "total": result.total, "pages": result.pages},
        }
    )


@projects_bp.post("/<int:project_id>/tasks")
@jwt_required()
def create_project_task(project_id):
    user, error_response = _current_user_or_error()
    if error_response:
        return error_response
    project, error_response = owned_project(user, project_id)
    if error_response:
        return error_response
    task, errors = create_task(user, project, request.get_json(silent=True) or {})
    if errors:
        body, status = validation_error(errors)
        return jsonify(body), status
    invalidate_dashboard_cache(user.id)
    return jsonify({"task": task.to_dict()}), 201
