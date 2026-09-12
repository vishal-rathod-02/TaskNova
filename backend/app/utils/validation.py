import re
from datetime import datetime

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PRIORITIES = {"low", "medium", "high"}
STATUSES = {"todo", "in_progress", "done"}


def validation_error(errors):
    return {"message": "Validation failed", "errors": errors}, 422


def parse_iso_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def validate_registration(payload):
    errors = {}
    full_name = str(payload.get("full_name", "")).strip()
    email = str(payload.get("email", "")).lower().strip()
    password = str(payload.get("password", ""))
    if not 2 <= len(full_name) <= 120:
        errors["full_name"] = "Enter a name between 2 and 120 characters."
    if not EMAIL_PATTERN.match(email):
        errors["email"] = "Enter a valid email address."
    if len(password) < 8:
        errors["password"] = "Use a password with at least 8 characters."
    return {"full_name": full_name, "email": email, "password": password}, errors


def validate_project(payload):
    errors = {}
    name = str(payload.get("name", "")).strip()
    description = str(payload.get("description", "")).strip() or None
    if not 1 <= len(name) <= 120:
        errors["name"] = "Enter a project name between 1 and 120 characters."
    if description and len(description) > 5000:
        errors["description"] = "Description must be 5000 characters or fewer."
    return {"name": name, "description": description}, errors


def validate_task(payload, partial=False):
    errors = {}
    data = {}
    if not partial or "title" in payload:
        title = str(payload.get("title", "")).strip()
        if not 1 <= len(title) <= 160:
            errors["title"] = "Enter a task title between 1 and 160 characters."
        data["title"] = title
    if not partial or "description" in payload:
        description = str(payload.get("description", "")).strip() or None
        if description and len(description) > 10000:
            errors["description"] = "Description must be 10000 characters or fewer."
        data["description"] = description
    if not partial or "priority" in payload:
        priority = payload.get("priority", "medium")
        if priority not in PRIORITIES:
            errors["priority"] = "Priority must be low, medium, or high."
        data["priority"] = priority
    if not partial or "status" in payload:
        status = payload.get("status", "todo")
        if status not in STATUSES:
            errors["status"] = "Status must be todo, in_progress, or done."
        data["status"] = status
    if not partial or "due_date" in payload:
        raw_due_date = payload.get("due_date")
        due_date = parse_iso_datetime(raw_due_date)
        if raw_due_date and not due_date:
            errors["due_date"] = "Enter a valid due date and time."
        data["due_date"] = due_date
    if not partial or "project_id" in payload:
        try:
            project_id = int(payload.get("project_id"))
            if project_id < 1:
                raise ValueError
        except (TypeError, ValueError):
            project_id = None
            errors["project_id"] = "Select a valid project."
        data["project_id"] = project_id
    return data, errors
