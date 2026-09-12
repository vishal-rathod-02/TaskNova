from datetime import datetime, timedelta

from flask import jsonify

from ..extensions import db
from ..models import Project, Task
from ..utils.activity import log_task_activity
from ..utils.validation import parse_iso_datetime, validate_task


def owned_project(user, project_id):
    project = db.session.get(Project, project_id)
    if not project:
        return None, (jsonify({"message": "Project not found."}), 404)
    if project.owner_id != user.id:
        return None, (jsonify({"message": "You do not have access to this project."}), 403)
    return project, None


def owned_task(user, task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return None, (jsonify({"message": "Task not found."}), 404)
    if task.project.owner_id != user.id:
        return None, (jsonify({"message": "You do not have access to this task."}), 403)
    return task, None


def apply_task_filters(query, args):
    status = args.get("status")
    priority = args.get("priority")
    due_from = parse_iso_datetime(args.get("due_from"))
    due_to = parse_iso_datetime(args.get("due_to"))
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if due_from:
        query = query.filter(Task.due_date >= due_from)
    if due_to:
        # Date-only filters include the whole selected end day.
        if len(args.get("due_to", "")) == 10:
            due_to += timedelta(days=1)
            query = query.filter(Task.due_date < due_to)
        else:
            query = query.filter(Task.due_date <= due_to)
    return query


def create_task(user, project, payload):
    enriched_payload = {**payload, "project_id": project.id}
    data, errors = validate_task(enriched_payload)
    if errors:
        return None, errors
    task = Task(
        title=data["title"],
        description=data["description"],
        priority=data["priority"],
        status=data["status"],
        due_date=data["due_date"],
        project_id=project.id,
        created_by=user.id,
    )
    db.session.add(task)
    db.session.flush()
    log_task_activity(task.id, user.id, "created", {"after": {"title": task.title, "status": task.status, "priority": task.priority}})
    db.session.commit()
    return task, None


def update_task(user, task, payload):
    allowed_fields = {"title", "description", "priority", "status", "due_date"}
    if not set(payload).intersection(allowed_fields):
        return None, {"task": "Provide at least one task field to update."}
    data, errors = validate_task(payload, partial=True)
    if errors:
        return None, errors
    mutable_fields = {"title", "description", "priority", "status", "due_date"}
    changes = {}
    for field in mutable_fields.intersection(data):
        old_value = getattr(task, field)
        new_value = data[field]
        if old_value != new_value:
            changes[field] = {
                "from": old_value.isoformat() if isinstance(old_value, datetime) else old_value,
                "to": new_value.isoformat() if isinstance(new_value, datetime) else new_value,
            }
            setattr(task, field, new_value)
    if not changes:
        return task, None
    action = "status_changed" if set(changes) == {"status"} else "updated"
    log_task_activity(task.id, user.id, action, {"changes": changes})
    db.session.commit()
    return task, None
