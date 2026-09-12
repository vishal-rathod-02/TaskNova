from app.extensions import db
from app.models import User


def auth_header(client, email, password):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json['access_token']}"}


def test_task_lifecycle_records_activity_and_updates_analytics(client):
    account = {"full_name": "Priya Dev", "email": "priya@example.com", "password": "securepass"}
    assert client.post("/api/auth/register", json=account).status_code == 201
    headers = auth_header(client, account["email"], account["password"])

    project = client.post("/api/projects", headers=headers, json={"name": "Release plan", "description": "Ship v1"})
    assert project.status_code == 201
    project_id = project.json["project"]["id"]

    task = client.post(
        "/api/tasks",
        headers=headers,
        json={"project_id": project_id, "title": "Write release notes", "priority": "high", "due_date": "2026-10-01T09:00"},
    )
    assert task.status_code == 201
    task_id = task.json["task"]["id"]

    assert client.put(f"/api/tasks/{task_id}", headers=headers, json={"status": "in_progress"}).json["task"]["status"] == "in_progress"
    assert client.post(f"/api/tasks/{task_id}/complete", headers=headers).json["task"]["status"] == "done"

    activity = client.get(f"/api/tasks/{task_id}/activity", headers=headers)
    assert activity.status_code == 200
    assert [entry["action"] for entry in activity.json["activity"]] == ["status_changed", "status_changed", "created"]

    dashboard = client.get("/api/analytics/me", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json["stats"]["completed_tasks"] == 1


def test_admin_can_block_but_not_delete_an_admin(client, app):
    user_account = {"full_name": "Standard User", "email": "user@example.com", "password": "securepass"}
    assert client.post("/api/auth/register", json=user_account).status_code == 201
    with app.app_context():
        admin = User(full_name="Ops Admin", email="admin@example.com", role="admin")
        admin.set_password("securepass")
        db.session.add(admin)
        db.session.commit()

    admin_headers = auth_header(client, "admin@example.com", "securepass")
    users = client.get("/api/admin/users", headers=admin_headers)
    standard_user = next(user for user in users.json["users"] if user["email"] == user_account["email"])
    admin_user = next(user for user in users.json["users"] if user["email"] == "admin@example.com")

    blocked = client.patch(f"/api/admin/users/{standard_user['id']}/block", headers=admin_headers, json={"is_blocked": True})
    assert blocked.status_code == 200
    assert blocked.json["user"]["is_blocked"] is True
    assert client.post("/api/auth/login", json={"email": user_account["email"], "password": user_account["password"]}).status_code == 403
    assert client.delete(f"/api/admin/users/{admin_user['id']}", headers=admin_headers).status_code == 400
