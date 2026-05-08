import json
import os
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from sqlalchemy import func
from werkzeug.utils import secure_filename

from .extensions import db, redis_client
from .models import ActivityLog, Project, Task, User
from .utils import role_required

api = Blueprint("api", __name__, url_prefix="/api")


def _get_current_user():
    identity = get_jwt_identity()
    return User.query.get(int(identity))


def _log_activity(task_id, user_id, action, metadata=None):
    log = ActivityLog(task_id=task_id, user_id=user_id, action=action, details=metadata)
    db.session.add(log)


@api.post("/auth/register")
def register():
    payload = request.get_json() or {}
    required_fields = ["full_name", "email", "password"]
    if not all(payload.get(field) for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(email=payload["email"].lower().strip()).first():
        return jsonify({"message": "Email already registered"}), 409

    user = User(
        full_name=payload["full_name"].strip(),
        email=payload["email"].lower().strip(),
        role=payload.get("role", "user"),
    )
    user.set_password(payload["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"user": user.to_dict()}), 201


@api.post("/auth/login")
def login():
    payload = request.get_json() or {}
    email = payload.get("email", "").lower().strip()
    password = payload.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password"}), 401
    if user.is_blocked:
        return jsonify({"message": "Your account is blocked"}), 403

    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    refresh_token = create_refresh_token(identity=str(user.id))
    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(),
        }
    )


@api.post("/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    if not user or user.is_blocked:
        return jsonify({"message": "Unauthorized"}), 403
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"access_token": access_token})


@api.get("/me")
@jwt_required()
def me():
    user = _get_current_user()
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({"user": user.to_dict()})


@api.get("/projects")
@jwt_required()
def get_projects():
    user = _get_current_user()
    if user.role == "admin":
        projects = Project.query.order_by(Project.created_at.desc()).all()
    else:
        projects = Project.query.filter_by(owner_id=user.id).order_by(Project.created_at.desc()).all()
    return jsonify({"projects": [project.to_dict() for project in projects]})


@api.post("/projects")
@jwt_required()
def create_project():
    user = _get_current_user()
    payload = request.get_json() or {}
    if not payload.get("name"):
        return jsonify({"message": "Project name is required"}), 400

    project = Project(
        name=payload["name"].strip(),
        description=payload.get("description"),
        owner_id=user.id,
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({"project": project.to_dict()}), 201


@api.put("/projects/<int:project_id>")
@jwt_required()
def update_project(project_id):
    user = _get_current_user()
    project = Project.query.get_or_404(project_id)
    if user.role != "admin" and project.owner_id != user.id:
        return jsonify({"message": "Forbidden"}), 403

    payload = request.get_json() or {}
    if "name" in payload:
        project.name = payload["name"].strip()
    if "description" in payload:
        project.description = payload["description"]
    db.session.commit()
    return jsonify({"project": project.to_dict()})


@api.delete("/projects/<int:project_id>")
@jwt_required()
def delete_project(project_id):
    user = _get_current_user()
    project = Project.query.get_or_404(project_id)
    if user.role != "admin" and project.owner_id != user.id:
        return jsonify({"message": "Forbidden"}), 403
    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted"})


@api.get("/tasks")
@jwt_required()
def get_tasks():
    user = _get_current_user()
    project_id = request.args.get("project_id", type=int)

    query = Task.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    if user.role != "admin":
        owned_projects = [p.id for p in Project.query.filter_by(owner_id=user.id).all()]
        query = query.filter(Task.project_id.in_(owned_projects))

    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify({"tasks": [task.to_dict() for task in tasks]})


@api.post("/tasks")
@jwt_required()
def create_task():
    user = _get_current_user()
    payload = request.get_json() or {}
    required_fields = ["title", "project_id", "priority"]
    if not all(payload.get(field) for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    project = Project.query.get_or_404(payload["project_id"])
    if user.role != "admin" and project.owner_id != user.id:
        return jsonify({"message": "Forbidden"}), 403

    deadline = None
    if payload.get("deadline"):
        deadline = datetime.fromisoformat(payload["deadline"])

    task = Task(
        title=payload["title"].strip(),
        description=payload.get("description"),
        priority=payload.get("priority", "medium"),
        status=payload.get("status", "todo"),
        deadline=deadline,
        project_id=payload["project_id"],
        assignee_id=payload.get("assignee_id"),
        created_by=user.id,
        attachment_url=payload.get("attachment_url"),
    )
    db.session.add(task)
    db.session.flush()
    _log_activity(task.id, user.id, "created_task", f"Task '{task.title}' created")
    db.session.commit()
    return jsonify({"task": task.to_dict()}), 201


@api.post("/uploads")
@jwt_required()
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "No file provided"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "Empty filename"}), 400

    safe_name = secure_filename(file.filename)
    timestamped_name = f"{int(datetime.utcnow().timestamp())}_{safe_name}"
    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], timestamped_name)
    file.save(upload_path)
    return jsonify({"attachment_url": upload_path})


@api.put("/tasks/<int:task_id>")
@jwt_required()
def update_task(task_id):
    user = _get_current_user()
    payload = request.get_json() or {}
    task = Task.query.get_or_404(task_id)
    project = Project.query.get(task.project_id)

    if user.role != "admin" and project.owner_id != user.id:
        return jsonify({"message": "Forbidden"}), 403

    mutable_fields = ["title", "description", "status", "priority", "assignee_id", "attachment_url"]
    for field in mutable_fields:
        if field in payload:
            setattr(task, field, payload[field])

    if "deadline" in payload and payload["deadline"]:
        task.deadline = datetime.fromisoformat(payload["deadline"])

    _log_activity(task.id, user.id, "updated_task", f"Task '{task.title}' updated")
    db.session.commit()
    return jsonify({"task": task.to_dict()})


@api.post("/tasks/<int:task_id>/complete")
@jwt_required()
def complete_task(task_id):
    user = _get_current_user()
    task = Task.query.get_or_404(task_id)
    project = Project.query.get(task.project_id)
    if user.role != "admin" and project.owner_id != user.id:
        return jsonify({"message": "Forbidden"}), 403

    task.status = "done"
    _log_activity(task.id, user.id, "completed_task", f"Task '{task.title}' marked as done")
    db.session.commit()
    return jsonify({"task": task.to_dict()})


@api.delete("/tasks/<int:task_id>")
@jwt_required()
def delete_task(task_id):
    user = _get_current_user()
    task = Task.query.get_or_404(task_id)
    project = Project.query.get(task.project_id)
    if user.role != "admin" and project.owner_id != user.id:
        return jsonify({"message": "Forbidden"}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})


@api.get("/tasks/<int:task_id>/logs")
@jwt_required()
def get_logs(task_id):
    user = _get_current_user()
    task = Task.query.get_or_404(task_id)
    project = Project.query.get(task.project_id)
    if user.role != "admin" and project.owner_id != user.id:
        return jsonify({"message": "Forbidden"}), 403

    logs = ActivityLog.query.filter_by(task_id=task_id).order_by(ActivityLog.created_at.desc()).all()
    return jsonify({"logs": [log.to_dict() for log in logs]})


@api.get("/admin/users")
@role_required("admin")
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({"users": [user.to_dict() for user in users]})


@api.post("/admin/users/<int:user_id>/toggle-block")
@role_required("admin")
def toggle_block(user_id):
    user = User.query.get_or_404(user_id)
    user.is_blocked = not user.is_blocked
    db.session.commit()
    return jsonify({"user": user.to_dict()})


@api.delete("/admin/users/<int:user_id>")
@role_required("admin")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        return jsonify({"message": "Cannot delete admin user"}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})


@api.get("/analytics/dashboard")
@jwt_required()
def analytics_dashboard():
    user = _get_current_user()
    cache_key = f"dashboard_stats:{user.id}:{user.role}"
    cached = redis_client.get(cache_key) if redis_client else None
    if cached:
        return jsonify({"stats": json.loads(cached), "source": "cache"})

    query = Task.query
    if user.role != "admin":
        owned_projects = [p.id for p in Project.query.filter_by(owner_id=user.id).all()]
        query = query.filter(Task.project_id.in_(owned_projects))

    total_tasks = query.count()
    done_tasks = query.filter_by(status="done").count()
    overdue_tasks = query.filter(Task.deadline.isnot(None), Task.deadline < datetime.utcnow(), Task.status != "done").count()

    stats = {
        "total_tasks": total_tasks,
        "completed_tasks": done_tasks,
        "overdue_tasks": overdue_tasks,
        "completion_rate": round((done_tasks / total_tasks) * 100, 2) if total_tasks else 0.0,
    }

    if redis_client:
        redis_client.setex(cache_key, 120, json.dumps(stats))

    return jsonify({"stats": stats, "source": "db"})


@api.get("/analytics/status-breakdown")
@jwt_required()
def analytics_status():
    user = _get_current_user()
    query = db.session.query(Task.status, func.count(Task.id)).group_by(Task.status)
    if user.role != "admin":
        owned_projects = [p.id for p in Project.query.filter_by(owner_id=user.id).all()]
        query = query.filter(Task.project_id.in_(owned_projects))
    data = [{"status": status, "count": count} for status, count in query.all()]
    return jsonify({"items": data})
