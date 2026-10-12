"""Phase 1 tests: universal timetable CRUD, collision detection, ownership
isolation, auto-scheduler, persona templates, and ICS feed wiring."""

from datetime import date, timedelta

from app.extensions import db
from app.models import TimetableAllocation, TimetableSlot, User


def _register(client, name, email):
    response = client.post(
        "/api/auth/register",
        json={"full_name": name, "email": email, "password": "securepass123"},
    )
    assert response.status_code == 201
    return response.json["user"]


def _headers(client, email):
    response = client.post("/api/auth/login", json={"email": email, "password": "securepass123"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json['access_token']}"}


def _project(client, headers, name="Client Sprint"):
    response = client.post("/api/projects", headers=headers, json={"name": name})
    assert response.status_code == 201
    return response.json["project"]["id"]


def _slot_payload(**overrides):
    payload = {
        "title": "Team Standup",
        "slot_type": "meeting",
        "day_of_week": 0,
        "start_time": "09:00",
        "end_time": "09:15",
        "is_recurring": True,
    }
    payload.update(overrides)
    return payload


def test_slot_crud_and_validation(client):
    _register(client, "Maya Manager", "maya@example.com")
    headers = _headers(client, "maya@example.com")

    created = client.post("/api/timetable", headers=headers, json=_slot_payload())
    assert created.status_code == 201
    slot_id = created.json["slot"]["id"]
    assert created.json["slot"]["duration_minutes"] == 15

    listed = client.get("/api/timetable?day_of_week=0", headers=headers)
    assert listed.status_code == 200
    assert [s["id"] for s in listed.json["slots"]] == [slot_id]

    bad = client.post(
        "/api/timetable", headers=headers, json=_slot_payload(start_time="10:00", end_time="09:00")
    )
    assert bad.status_code == 422

    bad_type = client.post("/api/timetable", headers=headers, json=_slot_payload(slot_type="nap"))
    assert bad_type.status_code == 422

    updated = client.put(f"/api/timetable/{slot_id}", headers=headers, json={"title": "Morning Standup"})
    assert updated.status_code == 200
    assert updated.json["slot"]["title"] == "Morning Standup"

    # Custom accent colors round-trip: burgundy persists and renders client-side.
    tinted = client.put(f"/api/timetable/{slot_id}", headers=headers, json={"color_override": "#800020"})
    assert tinted.status_code == 200
    assert tinted.json["slot"]["color_override"] == "#800020"

    bad_color = client.put(f"/api/timetable/{slot_id}", headers=headers, json={"color_override": "#zzzzzz"})
    assert bad_color.status_code == 422

    assert client.delete(f"/api/timetable/{slot_id}", headers=headers).status_code == 204
    assert client.get("/api/timetable", headers=headers).json["slots"] == []


def test_collision_detection_returns_409(client):
    _register(client, "Owen Ops", "owen@example.com")
    headers = _headers(client, "owen@example.com")

    assert client.post("/api/timetable", headers=headers, json=_slot_payload()).status_code == 201
    clash = client.post(
        "/api/timetable",
        headers=headers,
        json=_slot_payload(title="Overlap Sync", start_time="09:05", end_time="09:30"),
    )
    assert clash.status_code == 409
    assert clash.json["conflict"]["title"] == "Team Standup"

    # Adjacent (touching) blocks are allowed: end == start is not an overlap.
    adjacent = client.post(
        "/api/timetable",
        headers=headers,
        json=_slot_payload(title="After Standup", start_time="09:15", end_time="09:45"),
    )
    assert adjacent.status_code == 201

    # One-off on the same weekday collides with the recurring Monday slot.
    next_monday = date.today() + timedelta(days=(0 - date.today().weekday()) % 7)
    dated_clash = client.post(
        "/api/timetable",
        headers=headers,
        json=_slot_payload(
            title="Dated Clash",
            is_recurring=False,
            day_of_week=None,
            specific_date=next_monday.isoformat(),
            start_time="09:00",
            end_time="09:30",
        ),
    )
    assert dated_clash.status_code == 409


def test_cross_user_isolation(client):
    _register(client, "Alice Owner", "alice@example.com")
    _register(client, "Bob Intruder", "bob@example.com")
    alice = _headers(client, "alice@example.com")
    bob = _headers(client, "bob@example.com")

    created = client.post("/api/timetable", headers=alice, json=_slot_payload())
    slot_id = created.json["slot"]["id"]

    assert client.get("/api/timetable", headers=bob).json["slots"] == []
    assert client.put(f"/api/timetable/{slot_id}", headers=bob, json={"title": "Hijack"}).status_code == 403
    assert client.delete(f"/api/timetable/{slot_id}", headers=bob).status_code == 403

    # Foreign project links are rejected even when the slot itself is valid.
    foreign_project = _project(client, bob)
    linked = client.post(
        "/api/timetable", headers=alice, json=_slot_payload(title="Linked", project_id=foreign_project,
                                                           start_time="14:00", end_time="15:00")
    )
    assert linked.status_code == 403


def test_auto_schedule_preview_and_apply(client, app):
    _register(client, "Dev Deep", "dev@example.com")
    headers = _headers(client, "dev@example.com")
    project_id = _project(client, headers)

    for i, priority in enumerate(("high", "medium", "low")):
        response = client.post(
            "/api/tasks",
            headers=headers,
            json={"project_id": project_id, "title": f"Backlog {i}", "priority": priority},
        )
        assert response.status_code == 201

    # Fixed morning meeting blocks the start of today (one-off, so the test
    # is independent of which weekday it runs on).
    today_iso = date.today().isoformat()
    blocker = client.post(
        "/api/timetable",
        headers=headers,
        json=_slot_payload(is_recurring=False, day_of_week=None, specific_date=today_iso,
                           start_time="09:00", end_time="09:15"),
    )
    assert blocker.status_code == 201

    preview = client.post(
        "/api/timetable/auto-schedule",
        headers=headers,
        json={"work_start": "09:00", "work_end": "17:00", "mode": "maker", "max_tasks": 5},
    )
    assert preview.status_code == 200
    body = preview.json
    assert body["applied"] is False
    assert body["mode"] == "maker"
    # Highest priority task is scheduled first, after the 09:00-09:15 meeting.
    assert body["proposal"][0]["title"] == "Backlog 0"
    assert all(item["start_time"] >= "09:15" for item in body["proposal"])

    applied = client.post(
        "/api/timetable/auto-schedule",
        headers=headers,
        json={"work_start": "09:00", "work_end": "17:00", "mode": "pomodoro",
              "max_tasks": 5, "apply": True},
    )
    assert applied.status_code == 200
    assert applied.json["applied"] is True
    assert len(applied.json["created"]) == len(applied.json["proposal"])

    with app.app_context():
        assert TimetableAllocation.query.count() == len(applied.json["created"])
        focus_slots = TimetableSlot.query.filter_by(slot_type="focus_work").all()
        assert focus_slots and all(s.specific_date is not None and not s.is_recurring for s in focus_slots)


def test_apply_template_and_ics_feed(client):
    _register(client, "Tina Template", "tina@example.com")
    headers = _headers(client, "tina@example.com")

    applied = client.post(
        "/api/timetable/apply-template", headers=headers, json={"template": "corporate"}
    )
    assert applied.status_code == 201
    assert len(applied.json["created"]) == 4 * 5  # 4 daily entries x Mon-Fri
    assert applied.json["skipped"] == []

    # Re-applying without overwrite skips every colliding entry instead of duplicating.
    again = client.post(
        "/api/timetable/apply-template", headers=headers, json={"template": "corporate"}
    )
    assert again.status_code == 201
    assert again.json["created"] == []
    assert len(again.json["skipped"]) == 20

    bad_template = client.post(
        "/api/timetable/apply-template", headers=headers, json={"template": "nope"}
    )
    assert bad_template.status_code == 422

    # ICS feed carries the timetable slots with weekly recurrence.
    login = client.post("/api/auth/login", json={"email": "tina@example.com", "password": "securepass123"})
    token = login.json["user"]["calendar_token"]
    feed = client.get(f"/api/calendar/feed/{token}.ics")
    assert feed.status_code == 200
    assert "tasknova-slot-" in feed.get_data(as_text=True)
    assert "RRULE:FREQ=WEEKLY" in feed.get_data(as_text=True)


def _admin_headers(client, app, email="governor2@example.com"):
    from app.extensions import db as _db

    with app.app_context():
        admin = User(full_name="Governor", email=email, role="admin")
        admin.set_password("securepass123")
        _db.session.add(admin)
        _db.session.commit()
    return _headers(client, email)


def test_template_governance_toggle_and_guard(client, app):
    _register(client, "Polly Planner", "polly@example.com")
    user_headers = _headers(client, "polly@example.com")
    admin_headers = _admin_headers(client, app)

    listed = client.get("/api/admin/timetable/templates", headers=admin_headers)
    assert listed.status_code == 200
    assert {t["name"] for t in listed.json["templates"]} == {"corporate", "maker", "academic", "freelance"}
    assert all(t["is_enabled"] for t in listed.json["templates"])

    # Members cannot touch the switchboard.
    assert client.get("/api/admin/timetable/templates", headers=user_headers).status_code == 403

    disabled = client.patch(
        "/api/admin/timetable/templates/maker", headers=admin_headers, json={"is_enabled": False}
    )
    assert disabled.status_code == 200
    assert disabled.json["template"]["is_enabled"] is False

    blocked = client.post("/api/timetable/apply-template", headers=user_headers, json={"template": "maker"})
    assert blocked.status_code == 403
    assert "not available yet" in blocked.json["message"]

    # Picker source hides retired templates instead of bluntly blocking members.
    picker = client.get("/api/timetable/templates", headers=user_headers)
    assert picker.status_code == 200
    assert {t["name"] for t in picker.json["templates"]} == {"corporate", "academic", "freelance"}
    assert all("label" in t and "blocks_per_week" in t for t in picker.json["templates"])
    assert client.get("/api/timetable/templates").status_code == 401

    assert client.patch("/api/admin/timetable/templates/nope", headers=admin_headers, json={"is_enabled": False}).status_code == 404
    bad_value = client.patch(
        "/api/admin/timetable/templates/maker", headers=admin_headers, json={"is_enabled": "yes"}
    )
    assert bad_value.status_code == 422

    enabled = client.patch(
        "/api/admin/timetable/templates/maker", headers=admin_headers, json={"is_enabled": True}
    )
    assert enabled.json["template"]["is_enabled"] is True
    applied = client.post("/api/timetable/apply-template", headers=user_headers, json={"template": "maker"})
    assert applied.status_code == 201

    relisted = client.get("/api/admin/timetable/templates", headers=admin_headers)
    maker = next(t for t in relisted.json["templates"] if t["name"] == "maker")
    assert maker["active_blocks"] == len(applied.json["created"])
    assert maker["adopters"] == 1


def test_tables_created_by_schema_sync(app):
    with app.app_context():
        names = set(db.inspect(db.engine).get_table_names())
    assert {"timetable_slot", "timetable_allocation"} <= names


def test_admin_delete_cleans_timetable_rows(client, app):
    _register(client, "Doomed User", "doomed@example.com")
    headers = _headers(client, "doomed@example.com")
    project_id = _project(client, headers)
    task = client.post(
        "/api/tasks", headers=headers, json={"project_id": project_id, "title": "Leftover", "priority": "high"}
    )
    assert task.status_code == 201
    assert client.post("/api/timetable", headers=headers, json=_slot_payload()).status_code == 201
    applied = client.post(
        "/api/timetable/auto-schedule",
        headers=headers,
        json={"work_start": "09:00", "work_end": "17:00", "mode": "maker", "max_tasks": 5, "apply": True},
    )
    assert applied.json["created"]

    with app.app_context():
        doomed = User.query.filter_by(email="doomed@example.com").first()
        doomed_id = doomed.id
        admin = User(full_name="Governor", email="governor@example.com", role="admin")
        admin.set_password("securepass123")
        db.session.add(admin)
        db.session.commit()

    admin_headers = _headers(client, "governor@example.com")
    assert client.delete(f"/api/admin/users/{doomed_id}", headers=admin_headers).status_code == 204

    with app.app_context():
        assert TimetableSlot.query.filter_by(user_id=doomed_id).count() == 0
        assert TimetableAllocation.query.count() == 0
