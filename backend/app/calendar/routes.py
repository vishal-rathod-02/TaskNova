from datetime import datetime, timedelta, timezone
from flask import Blueprint, Response, current_app, jsonify, make_response, request

from ..extensions import db
from ..models import Project, Task, TimetableSlot, User
from ..models.time import utcnow

calendar_bp = Blueprint("calendar", __name__, url_prefix="/api/calendar")


def _escape_ical_text(text):
    if not text:
        return ""
    # RFC 5545 string escaping: backslash, semicolon, comma, and newline
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
        .replace("\r", "\\n")
    )


def _format_ical_datetime(dt):
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y%m%dT%H%M%SZ")


@calendar_bp.route("/feed/<string:token>.ics", methods=["GET"])
@calendar_bp.route("/feed/<string:token>", methods=["GET"])
def get_calendar_feed(token):
    """Serve a live RFC 5545 iCalendar feed for external calendar subscription (Google Calendar, Apple Calendar, Outlook)."""
    clean_token = token.strip()
    user = User.query.filter_by(calendar_token=clean_token).first()
    if not user or user.is_blocked:
        return jsonify({"message": "Invalid or expired calendar feed token."}), 404

    now_utc = utcnow()
    stamp = _format_ical_datetime(now_utc)
    app_url = current_app.config.get("APP_FRONTEND_URL", "https://tasknova.app").rstrip("/")

    tasks = (
        Task.query.options(db.joinedload(Task.project))
        .join(Project)
        .filter(Project.owner_id == user.id, Task.due_date.isnot(None))
        .order_by(Task.due_date.asc())
        .all()
    )

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//TaskNova//Academic Task Ledger//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:TaskNova Schedule ({user.full_name})",
        "X-WR-TIMEZONE:UTC",
        "X-WR-CALDESC:Live coursework, assignments, and exam deadlines from TaskNova",
    ]

    for task in tasks:
        due = task.due_date
        if not due:
            continue
        # Standard 1-hour block for assignment deadline / exam
        dtstart = _format_ical_datetime(due - timedelta(minutes=30))
        dtend = _format_ical_datetime(due)
        project_name = task.project.name if task.project else "Course"
        summary = _escape_ical_text(f"[{project_name}] {task.title}")
        description_lines = []
        if task.description:
            description_lines.append(task.description.strip())
        description_lines.append(f"Course: {project_name}")
        description_lines.append(f"Status: {task.status.upper()}")
        description_lines.append(f"Priority: {task.priority.upper()}")
        description_lines.append(f"Open in TaskNova: {app_url}/tasks")
        desc_escaped = _escape_ical_text("\n".join(description_lines))

        # RFC priority: 1=High, 5=Medium, 9=Low
        priority_val = "1" if task.priority == "high" else ("9" if task.priority == "low" else "5")
        status_val = "COMPLETED" if task.status == "done" else "CONFIRMED"

        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:tasknova-task-{task.id}-{user.id}@tasknova",
                f"DTSTAMP:{stamp}",
                f"DTSTART:{dtstart}",
                f"DTEND:{dtend}",
                f"SUMMARY:{summary}",
                f"DESCRIPTION:{desc_escaped}",
                f"STATUS:{status_val}",
                f"PRIORITY:{priority_val}",
                f"URL:{app_url}/tasks",
                "BEGIN:VALARM",
                "TRIGGER:-PT30M",
                "ACTION:DISPLAY",
                f"DESCRIPTION:Reminder: {summary}",
                "END:VALARM",
                "END:VEVENT",
            ]
        )

    # Phase 1: universal timetable slots flow into the same subscription feed.
    _WEEKDAY_ICAL = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
    today = now_utc.date()
    try:
        slots = TimetableSlot.query.filter_by(user_id=user.id).all()
    except Exception:
        slots = []
    for slot in slots:
        try:
            sh, sm = (int(p) for p in str(slot.start_time).split(":"))
            eh, em = (int(p) for p in str(slot.end_time).split(":"))
            if not (0 <= sh <= 23 and 0 <= sm <= 59 and 0 <= eh <= 23 and 0 <= em <= 59):
                continue
            if eh * 60 + em <= sh * 60 + sm:
                continue
        except (ValueError, AttributeError):
            continue
        if slot.specific_date is not None:
            if slot.specific_date < today:
                continue
            event_date = slot.specific_date
            rrule = None
        elif slot.day_of_week is not None and 0 <= slot.day_of_week <= 6:
            delta = (slot.day_of_week - today.weekday()) % 7
            event_date = today + timedelta(days=delta)
            rrule = f"RRULE:FREQ=WEEKLY;BYDAY={_WEEKDAY_ICAL[slot.day_of_week]}"
        else:
            continue
        dtstart = _format_ical_datetime(datetime(event_date.year, event_date.month, event_date.day, sh, sm))
        dtend = _format_ical_datetime(datetime(event_date.year, event_date.month, event_date.day, eh, em))
        if not dtstart or not dtend:
            continue
        type_label = str(slot.slot_type or "focus_work").replace("_", " ").title()
        summary = _escape_ical_text(f"[{type_label}] {slot.title}")
        slot_desc = [f"Timetable: {type_label}"]
        if slot.project:
            slot_desc.append(f"Project: {slot.project.name}")
        if slot.location:
            slot_desc.append(f"Location: {slot.location}")
        slot_desc.append(f"Open in TaskNova: {app_url}/timetable")
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:tasknova-slot-{slot.id}-{user.id}@tasknova",
                f"DTSTAMP:{stamp}",
                f"DTSTART:{dtstart}",
                f"DTEND:{dtend}",
                f"SUMMARY:{summary}",
                f"DESCRIPTION:{_escape_ical_text(chr(10).join(slot_desc))}",
                "STATUS:CONFIRMED",
                f"URL:{app_url}/timetable",
            ]
        )
        if rrule:
            lines.append(rrule)
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    ical_content = "\r\n".join(lines) + "\r\n"

    response = Response(ical_content, mimetype="text/calendar; charset=utf-8")
    response.headers["Content-Disposition"] = f'inline; filename="tasknova-{user.id}.ics"'
    response.headers["Cache-Control"] = "private, max-age=180, must-revalidate"
    return response
