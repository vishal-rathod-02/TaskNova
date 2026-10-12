from datetime import date

from flask import jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models.timetable import TimetableAllocation, TimetableSlot
from ..utils.auth import require_current_user
from ..utils.rate_limit import rate_limit
from ..utils.validation import validation_error
from . import timetable_bp
from .service import (
    MAX_SLOTS_PER_CALL,
    MAX_TASKS_PER_SCHEDULE,
    SCHEDULE_MODES,
    TEMPLATE_SLOTS,
    TEMPLATES,
    build_proposal,
    find_collision,
    is_template_enabled,
    owned_slot,
    parse_date,
    parse_day,
    resolve_project,
    resolve_task,
    slots_for_date,
    validate_slot,
)


def _slot_payload(slot):
    return {"slot": slot.to_dict()}


@timetable_bp.get("/templates")
@jwt_required()
def list_available_templates():
    """Persona picker source: only admin-enabled templates are ever listed."""
    from .service import TEMPLATE_META, TEMPLATE_SLOTS, template_states

    states = template_states()
    templates = [
        {
            "name": name,
            "label": TEMPLATE_META[name]["label"],
            "description": TEMPLATE_META[name]["description"],
            "blocks_per_week": len(TEMPLATE_SLOTS[name]) * 5,
        }
        for name in states
        if states[name].is_enabled
    ]
    return jsonify({"templates": templates})


@timetable_bp.get("")
@jwt_required()
def list_slots():
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    query = TimetableSlot.query.filter_by(user_id=user.id)

    day = request.args.get("day_of_week")
    if day is not None and day != "":
        parsed = parse_day(day)
        if parsed is None:
            return jsonify({"message": "Validation failed", "errors": {"day_of_week": "Use 0 (Mon) to 6 (Sun)."}}), 422
        query = query.filter(TimetableSlot.day_of_week == parsed)

    target = request.args.get("date")
    if target:
        parsed_date = parse_date(target)
        if not parsed_date:
            return jsonify({"message": "Validation failed", "errors": {"date": "Use YYYY-MM-DD."}}), 422
        query = query.filter(
            (TimetableSlot.specific_date == parsed_date)
            | ((TimetableSlot.specific_date.is_(None)) & (TimetableSlot.day_of_week == parsed_date.weekday()))
        )

    slot_type = (request.args.get("slot_type") or "").strip().lower()
    if slot_type:
        from ..models.timetable import SLOT_TYPES

        if slot_type not in SLOT_TYPES:
            return jsonify({"message": "Validation failed", "errors": {"slot_type": "Unknown slot type."}}), 422
        query = query.filter(TimetableSlot.slot_type == slot_type)

    slots = (
        query.options(db.joinedload(TimetableSlot.project), db.joinedload(TimetableSlot.allocations))
        .order_by(
            TimetableSlot.specific_date.is_(None),
            TimetableSlot.specific_date.asc(),
            TimetableSlot.day_of_week.asc(),
            TimetableSlot.start_time.asc(),
        )
        .all()
    )
    return jsonify({"slots": [s.to_dict() for s in slots]})


@timetable_bp.post("")
@jwt_required()
@rate_limit(limit=30, window_seconds=60)
def create_slot():
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    payload = request.get_json(silent=True) or {}
    data, errors = validate_slot(payload)
    if errors:
        body, status = validation_error(errors)
        return jsonify(body), status

    _, project_error = resolve_project(user, data.get("project_id"))
    if project_error:
        return project_error

    clash = find_collision(user, data["day_of_week"], data["specific_date"], data["start_time"], data["end_time"])
    if clash:
        return (
            jsonify({"message": "Time slot overlaps an existing routine entry.", "conflict": clash.to_dict()}),
            409,
        )

    slot = TimetableSlot(
        user_id=user.id,
        project_id=data.get("project_id"),
        title=data["title"],
        slot_type=data["slot_type"],
        day_of_week=data["day_of_week"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        location=data.get("location"),
        color_override=data.get("color_override"),
        is_recurring=data["is_recurring"],
        specific_date=data.get("specific_date"),
    )
    db.session.add(slot)
    db.session.commit()
    return jsonify(_slot_payload(slot)), 201


@timetable_bp.put("/<int:slot_id>")
@jwt_required()
@rate_limit(limit=30, window_seconds=60)
def update_slot(slot_id):
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    slot, error = owned_slot(user, slot_id)
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    data, errors = validate_slot(payload, partial=True)
    if errors:
        body, status = validation_error(errors)
        return jsonify(body), status

    if "project_id" in payload:
        _, project_error = resolve_project(user, data.get("project_id"))
        if project_error:
            return project_error
    if not any(k in payload for k in ("title", "slot_type", "day_of_week", "start_time", "end_time",
                                      "location", "color_override", "is_recurring", "specific_date", "project_id")):
        return jsonify({"message": "Validation failed", "errors": {"slot": "Provide at least one slot field to update."}}), 422

    # Resolve effective window for collision detection (merge with stored values).
    eff_day = data.get("day_of_week", slot.day_of_week) if "day_of_week" in payload else slot.day_of_week
    if "specific_date" in payload:
        eff_date = data.get("specific_date")
    else:
        eff_date = slot.specific_date
    eff_start = data.get("start_time", slot.start_time) if "start_time" in payload else slot.start_time
    eff_end = data.get("end_time", slot.end_time) if "end_time" in payload else slot.end_time
    eff_recurring = data.get("is_recurring", slot.is_recurring) if "is_recurring" in payload else slot.is_recurring

    # Structural rule on the merged result.
    if eff_recurring and eff_day is None:
        return jsonify({"message": "Validation failed", "errors": {"day_of_week": "Recurring slots require a day of week."}}), 422
    if not eff_recurring and eff_date is None:
        return jsonify({"message": "Validation failed", "errors": {"specific_date": "One-off slots require a specific date."}}), 422

    window_changed = (
        "day_of_week" in payload or "specific_date" in payload or "start_time" in payload or "end_time" in payload
    )
    if window_changed:
        clash = find_collision(user, eff_day, eff_date, eff_start, eff_end, exclude_id=slot.id)
        if clash:
            return (
                jsonify({"message": "Updated time overlaps an existing routine entry.", "conflict": clash.to_dict()}),
                409,
            )

    mutable = ("title", "slot_type", "day_of_week", "start_time", "end_time", "location",
               "color_override", "is_recurring", "specific_date", "project_id")
    for field in mutable:
        if field in payload:
            setattr(slot, field, data.get(field))
    db.session.commit()
    return jsonify(_slot_payload(slot))


@timetable_bp.delete("/<int:slot_id>")
@jwt_required()
@rate_limit(limit=30, window_seconds=60)
def delete_slot(slot_id):
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    slot, error = owned_slot(user, slot_id)
    if error:
        return error
    # Allocations cascade via relationship; explicit delete keeps SQLite FK behavior safe.
    TimetableAllocation.query.filter_by(slot_id=slot.id).delete(synchronize_session=False)
    db.session.delete(slot)
    db.session.commit()
    return "", 204


@timetable_bp.post("/auto-schedule")
@jwt_required()
@rate_limit(limit=10, window_seconds=60)
def auto_schedule():
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    payload = request.get_json(silent=True) or {}

    target = parse_date(payload.get("date")) if payload.get("date") else date.today()
    if payload.get("date") and not target:
        return jsonify({"message": "Validation failed", "errors": {"date": "Use YYYY-MM-DD."}}), 422
    mode = str(payload.get("mode", "maker")).strip().lower()
    if mode not in SCHEDULE_MODES:
        return jsonify({"message": "Validation failed", "errors": {"mode": "Mode must be maker or pomodoro."}}), 422

    from .service import TIME_PATTERN

    work_start = str(payload.get("work_start", "09:00")).strip()
    work_end = str(payload.get("work_end", "17:00")).strip()
    if not TIME_PATTERN.match(work_start) or not TIME_PATTERN.match(work_end):
        return jsonify({"message": "Validation failed", "errors": {"work_start": "Use HH:MM workday bounds."}}), 422
    try:
        max_tasks = min(max(int(payload.get("max_tasks", 6)), 1), MAX_TASKS_PER_SCHEDULE)
    except (TypeError, ValueError):
        return jsonify({"message": "Validation failed", "errors": {"max_tasks": "Use 1 to 20."}}), 422

    result = build_proposal(user, target, work_start, work_end, mode, max_tasks)

    if not payload.get("apply"):
        return jsonify({**result, "applied": False})

    # Apply: materialize each proposal item as a dated focus block + allocation.
    created, skipped = [], []
    for item in result["proposal"]:
        if len(created) >= MAX_SLOTS_PER_CALL:
            skipped.append({**item, "reason": "Per-call creation cap reached."})
            continue
        clash = find_collision(user, None, target, item["start_time"], item["end_time"])
        if clash:
            skipped.append({**item, "reason": "Overlaps an existing entry.", "conflict_id": clash.id})
            continue
        task, task_error = resolve_task(user, item["task_id"])
        if task_error:
            skipped.append({**item, "reason": "Task no longer accessible."})
            continue
        slot = TimetableSlot(
            user_id=user.id,
            project_id=task.project_id,
            title=item["title"][:160],
            slot_type="focus_work",
            day_of_week=None,
            start_time=item["start_time"],
            end_time=item["end_time"],
            is_recurring=False,
            specific_date=target,
        )
        db.session.add(slot)
        db.session.flush()
        db.session.add(TimetableAllocation(slot_id=slot.id, task_id=task.id, status="scheduled"))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            skipped.append({**item, "reason": "Already scheduled."})
            continue
        created.append({**item, "slot_id": slot.id})
    return jsonify({**result, "applied": True, "created": created, "skipped": skipped})


@timetable_bp.post("/apply-template")
@jwt_required()
@rate_limit(limit=10, window_seconds=60)
def apply_template():
    user = require_current_user()
    if not user:
        return jsonify({"message": "Unauthorized or blocked user."}), 403
    payload = request.get_json(silent=True) or {}
    template = str(payload.get("template", "")).strip().lower()
    if template not in TEMPLATES:
        return (
            jsonify({"message": "Validation failed", "errors": {"template": f"Choose one of: {', '.join(TEMPLATES)}."}}),
            422,
        )
    if not is_template_enabled(template):
        return jsonify({"message": "This routine template is not available yet."}), 403

    raw_days = payload.get("days", [0, 1, 2, 3, 4])
    if not isinstance(raw_days, list) or not raw_days:
        return jsonify({"message": "Validation failed", "errors": {"days": "Provide weekdays 0 (Mon) to 6 (Sun)."}}), 422
    days = []
    for d in raw_days:
        parsed = parse_day(d)
        if parsed is None:
            return jsonify({"message": "Validation failed", "errors": {"days": "Provide weekdays 0 (Mon) to 6 (Sun)."}}), 422
        if parsed not in days:
            days.append(parsed)

    overwrite = bool(payload.get("overwrite", False))
    planned = len(days) * len(TEMPLATE_SLOTS[template])
    if planned > MAX_SLOTS_PER_CALL:
        return (
            jsonify({"message": "Validation failed", "errors": {"days": f"Template batch capped at {MAX_SLOTS_PER_CALL} slots."}}),
            422,
        )

    created, skipped = [], []
    for day in sorted(days):
        for title, slot_type, start, end, location in TEMPLATE_SLOTS[template]:
            clash = find_collision(user, day, None, start, end)
            if clash:
                if overwrite:
                    TimetableAllocation.query.filter_by(slot_id=clash.id).delete(synchronize_session=False)
                    db.session.delete(clash)
                    db.session.flush()
                else:
                    skipped.append({"day_of_week": day, "title": title, "reason": "Overlaps an existing entry."})
                    continue
            slot = TimetableSlot(
                user_id=user.id,
                project_id=None,
                title=title,
                slot_type=slot_type,
                day_of_week=day,
                start_time=start,
                end_time=end,
                location=location or None,
                is_recurring=True,
                specific_date=None,
                source_template=template,
            )
            db.session.add(slot)
            created.append({"day_of_week": day, "title": title, "start_time": start, "end_time": end})
    db.session.commit()
    return jsonify({"template": template, "created": created, "skipped": skipped}), 201
