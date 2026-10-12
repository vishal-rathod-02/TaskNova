"""Business logic for the universal timetable scheduler (Phase 1 backend engine).

Security posture (must not harm existing workflows):
- Every helper is scoped to the authenticated user; cross-user rows resolve to
  404/403 exactly like the tasks service (no IDOR leakage via existence oracle
  beyond what tasks/projects already expose).
- All free-text passes through sanitize_text (XSS-safe for later rendering).
- Per-call creation caps prevent template/auto-schedule abuse.
"""

import re
from datetime import date, datetime

from flask import jsonify

from ..extensions import db
from ..models import Project, Task
from ..models.timetable import SLOT_TYPES, RoutineTemplateState, TimetableSlot
from ..tasks.service import owned_project, owned_task
from ..utils.validation import sanitize_text

TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")
COLOR_PATTERN = re.compile(r"^(#[0-9a-fA-F]{3}|#[0-9a-fA-F]{6}|[a-z]{3,12})$")
TEMPLATES = ("corporate", "maker", "academic", "freelance")
SCHEDULE_MODES = ("maker", "pomodoro")

# Governor-facing catalogue: labels/descriptions shared by the user template
# picker and the admin console. Single source so both stay in sync.
TEMPLATE_META = {
    "corporate": {
        "label": "Corporate Standard",
        "description": "Standup, lunch, syncs, and a daily wrap-up for team cadence.",
    },
    "maker": {
        "label": "Deep Work / Maker",
        "description": "Protected morning focus block plus an afternoon collaboration window.",
    },
    "academic": {
        "label": "Campus Routine",
        "description": "Lectures, lab sessions, and evening focus sprints.",
    },
    "freelance": {
        "label": "Freelance Sprint",
        "description": "Client project mornings with admin and outreach afternoons.",
    },
}


def seed_template_states():
    """Insert missing template state rows (all enabled). Idempotent."""
    for name in TEMPLATES:
        if db.session.get(RoutineTemplateState, name) is None:
            db.session.add(RoutineTemplateState(template_name=name, is_enabled=True))
    db.session.commit()


def template_states():
    """Return {name: RoutineTemplateState}, healing missing rows on the fly."""
    rows = {row.template_name: row for row in RoutineTemplateState.query.all()}
    missing = [name for name in TEMPLATES if name not in rows]
    if missing:
        seed_template_states()
        rows = {row.template_name: row for row in RoutineTemplateState.query.all()}
    return rows


def is_template_enabled(name):
    row = db.session.get(RoutineTemplateState, name)
    return row.is_enabled if row else True

# DoS guard: a single template/auto-schedule call can never create more rows.
MAX_SLOTS_PER_CALL = 40
MAX_TASKS_PER_SCHEDULE = 20


def _minutes(hhmm):
    hours, mins = (int(p) for p in str(hhmm).split(":"))
    return hours * 60 + mins


def _hhmm(total_minutes):
    total_minutes = max(0, min(24 * 60, int(total_minutes)))
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def parse_day(value):
    try:
        day = int(value)
    except (TypeError, ValueError):
        return None
    return day if 0 <= day <= 6 else None


def parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except ValueError:
        return None


def owned_slot(user, slot_id):
    slot = db.session.get(TimetableSlot, slot_id)
    if not slot:
        return None, (jsonify({"message": "Timetable slot not found."}), 404)
    if slot.user_id != user.id:
        return None, (jsonify({"message": "You do not have access to this timetable slot."}), 403)
    return slot, None


def validate_slot(payload, partial=False):
    """Validate slot fields; returns (data, errors) mirroring validate_task."""
    errors = {}
    data = {}

    if not partial or "title" in payload:
        title = sanitize_text(payload.get("title", ""))
        if not 1 <= len(title) <= 160:
            errors["title"] = "Enter a slot title between 1 and 160 characters."
        data["title"] = title

    if not partial or "slot_type" in payload:
        slot_type = str(payload.get("slot_type", "focus_work")).strip().lower()
        if slot_type not in SLOT_TYPES:
            errors["slot_type"] = f"Slot type must be one of: {', '.join(sorted(SLOT_TYPES))}."
        data["slot_type"] = slot_type

    if "day_of_week" in payload or not partial:
        raw_day = payload.get("day_of_week")
        if raw_day is None or raw_day == "":
            data["day_of_week"] = None
        else:
            day = parse_day(raw_day)
            if day is None:
                errors["day_of_week"] = "Day of week must be an integer 0 (Mon) to 6 (Sun)."
            data["day_of_week"] = day

    for field in ("start_time", "end_time"):
        if not partial or field in payload:
            value = str(payload.get(field, "")).strip()
            if not TIME_PATTERN.match(value):
                errors[field] = "Enter a valid 24-hour time as HH:MM."
            data[field] = value
    if "start_time" in data and "end_time" in data and not errors.get("start_time") and not errors.get("end_time"):
        if _minutes(data["end_time"]) <= _minutes(data["start_time"]):
            errors["end_time"] = "End time must be after start time."

    if not partial or "location" in payload:
        location = sanitize_text(payload.get("location", "")) or None
        if location and len(location) > 200:
            errors["location"] = "Location must be 200 characters or fewer."
        data["location"] = location

    if not partial or "color_override" in payload:
        color = str(payload.get("color_override", "")).strip() or None
        if color and (len(color) > 20 or not COLOR_PATTERN.match(color)):
            errors["color_override"] = "Use a hex color (#RGB/#RRGGBB) or short palette token."
        data["color_override"] = color

    if not partial or "is_recurring" in payload:
        raw = payload.get("is_recurring", True)
        data["is_recurring"] = bool(raw) if not isinstance(raw, str) else raw.strip().lower() not in {"false", "0", "no"}

    if "specific_date" in payload or not partial:
        raw_date = payload.get("specific_date")
        if raw_date in (None, ""):
            data["specific_date"] = None
        else:
            parsed = parse_date(raw_date)
            if not parsed:
                errors["specific_date"] = "Enter a valid calendar date as YYYY-MM-DD."
            data["specific_date"] = parsed

    # Structural rule: recurring blocks need a weekday; one-off blocks need a date.
    # In partial (PATCH-style) mode the merged result is validated by the caller,
    # so only enforce here for full creates.
    if not errors and not partial:
        if data.get("is_recurring") and data.get("day_of_week") is None:
            errors["day_of_week"] = "Recurring slots require a day of week (0=Mon to 6=Sun)."
        if not data.get("is_recurring") and data.get("specific_date") is None:
            errors["specific_date"] = "One-off slots require a specific date."

    if not partial or "project_id" in payload:
        raw_project = payload.get("project_id")
        if raw_project in (None, ""):
            data["project_id"] = None
        else:
            try:
                project_id = int(raw_project)
                if project_id < 1:
                    raise ValueError
            except (TypeError, ValueError):
                errors["project_id"] = "Select a valid project."
                data["project_id"] = None
            else:
                data["project_id"] = project_id

    return data, errors


def find_collision(user, day_of_week, specific_date, start_time, end_time, exclude_id=None):
    """Return the first owned slot overlapping the candidate window, else None.

    Recurring candidates collide with same-weekday recurring slots and with
    one-off slots whose date falls on that weekday. Dated candidates collide
    with same-date one-offs and with recurring slots on that date's weekday.
    """
    start_m = _minutes(start_time)
    end_m = _minutes(end_time)
    query = TimetableSlot.query.filter_by(user_id=user.id)
    if exclude_id:
        query = query.filter(TimetableSlot.id != exclude_id)
    for slot in query.all():
        same_scope = False
        if specific_date is not None:
            if slot.specific_date == specific_date:
                same_scope = True
            elif slot.specific_date is None and slot.day_of_week == specific_date.weekday():
                same_scope = True
        elif day_of_week is not None:
            if slot.specific_date is not None:
                same_scope = slot.specific_date.weekday() == day_of_week
            else:
                same_scope = slot.day_of_week == day_of_week
        if not same_scope:
            continue
        try:
            s, e = _minutes(slot.start_time), _minutes(slot.end_time)
        except ValueError:
            continue
        if start_m < e and s < end_m:
            return slot
    return None


def slots_for_date(user, target):
    """All owned slots effective on a calendar date (recurring + one-off)."""
    weekday = target.weekday()
    return (
        TimetableSlot.query.filter_by(user_id=user.id)
        .filter(
            (TimetableSlot.specific_date == target)
            | ((TimetableSlot.specific_date.is_(None)) & (TimetableSlot.day_of_week == weekday))
        )
        .order_by(TimetableSlot.start_time.asc())
        .all()
    )


def free_windows(slots, work_start="09:00", work_end="17:00"):
    """Carve free gaps between blocker slots inside the workday window."""
    day_start, day_end = _minutes(work_start), _minutes(work_end)
    busy = []
    for slot in slots:
        try:
            busy.append((_minutes(slot.start_time), _minutes(slot.end_time)))
        except ValueError:
            continue
    busy.sort()
    merged = []
    for s, e in busy:
        s, e = max(s, day_start), min(e, day_end)
        if e <= s:
            continue
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    gaps, cursor = [], day_start
    for s, e in merged:
        if s > cursor:
            gaps.append((cursor, s))
        cursor = max(cursor, e)
    if cursor < day_end:
        gaps.append((cursor, day_end))
    return [(_hhmm(s), _hhmm(e)) for s, e in gaps]


def rank_backlog(user, limit):
    """Pending tasks ordered by priority then due-date proximity (nulls last)."""
    priority_rank = {"high": 0, "medium": 1, "low": 2}
    tasks = (
        Task.query.join(Project)
        .filter(Project.owner_id == user.id, Task.status != "done")
        .order_by(Task.created_at.desc())
        .limit(200)
        .all()
    )
    tasks.sort(
        key=lambda t: (
            priority_rank.get(t.priority, 1),
            t.due_date is None,
            t.due_date or datetime.max,
        )
    )
    return tasks[:limit]


def build_proposal(user, target, work_start, work_end, mode, max_tasks):
    """Greedy fit of backlog tasks into free windows. Pure function: no writes."""
    slots = slots_for_date(user, target)
    gaps = free_windows(slots, work_start, work_end)
    tasks = rank_backlog(user, max_tasks)

    block = 90 if mode == "maker" else 25
    break_mins = 0 if mode == "maker" else 5
    buffer_mins = 5 if mode == "maker" else 0
    min_block = 30 if mode == "maker" else 25

    proposal, unscheduled = [], list(tasks)
    gap_minutes = [(_minutes(s), _minutes(e)) for s, e in gaps]

    for task in list(tasks):
        placed = False
        for i, (gs, ge) in enumerate(gap_minutes):
            need = min(block, ge - gs)
            if need < min_block:
                continue
            proposal.append(
                {
                    "task_id": task.id,
                    "title": task.title,
                    "project_id": task.project_id,
                    "project_name": task.project.name if task.project else None,
                    "priority": task.priority,
                    "start_time": _hhmm(gs),
                    "end_time": _hhmm(gs + need),
                }
            )
            cursor = gs + need + (break_mins or buffer_mins)
            gap_minutes[i] = (cursor, ge)
            unscheduled.remove(task)
            placed = True
            break
        if not placed:
            continue
    return {
        "date": target.isoformat(),
        "mode": mode,
        "work_start": work_start,
        "work_end": work_end,
        "free_windows": [{"start_time": s, "end_time": e} for s, e in gaps],
        "proposal": proposal,
        "unscheduled": [{"task_id": t.id, "title": t.title, "priority": t.priority} for t in unscheduled],
    }


# Persona quick-start templates: (title, slot_type, start, end, location).
TEMPLATE_SLOTS = {
    "corporate": [
        ("Team Standup", "meeting", "09:00", "09:15", "Google Meet"),
        ("Lunch Break", "habit", "12:30", "13:30", ""),
        ("Stakeholder Sync", "meeting", "16:00", "16:30", ""),
        ("Daily Wrap-up", "operations", "17:30", "17:45", ""),
    ],
    "maker": [
        ("Deep Work Block", "focus_work", "08:30", "12:00", ""),
        ("Collaboration Window", "meeting", "13:30", "15:30", ""),
    ],
    "academic": [
        ("Morning Lectures", "meeting", "09:00", "10:30", "Room 401"),
        ("Lab Session", "meeting", "11:00", "12:30", "Lab B"),
        ("Evening Study Sprint", "focus_work", "19:00", "21:00", "Library"),
    ],
    "freelance": [
        ("Client Project Work", "focus_work", "09:00", "12:00", ""),
        ("Admin & Outreach", "operations", "14:00", "15:00", ""),
    ],
}


def resolve_project(user, project_id):
    if project_id is None:
        return None, None
    project, error = owned_project(user, project_id)
    if error:
        return None, error
    return project, None


def resolve_task(user, task_id):
    try:
        task_id = int(task_id)
    except (TypeError, ValueError):
        return None, (jsonify({"message": "Validation failed", "errors": {"task_id": "Select a valid task."}}), 422)
    task, error = owned_task(user, task_id)
    if error:
        return None, error
    return task, None
