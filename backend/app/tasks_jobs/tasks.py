import logging
from datetime import timedelta

from flask import current_app
from sqlalchemy import func

from .. import extensions
from ..celery_app import celery
from ..extensions import db
from ..models import DailyReport, Notification, Project, Task, User
from ..models.time import iso_utc, utcnow
from ..services.email_service import send_daily_digest_email, send_deadline_email

logger = logging.getLogger(__name__)


def _same_day_notification_exists(user_id, kind, task_id, day):
    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return (
        Notification.query.filter(
            Notification.user_id == user_id,
            Notification.kind == kind,
            Notification.task_id == task_id,
            Notification.created_at >= start,
            Notification.created_at < end,
        ).first()
        is not None
    )


def run_deadline_reminders():
    """Create one persistent notification per due/overdue task per owner per day,
    and optionally dispatches an email alert if email is enabled.

    Extracted from the Celery task body so tests can exercise the same logic
    inside a Flask test-app context without a broker.
    """
    now = utcnow()
    window_end = now + timedelta(hours=current_app.config["REMINDER_WINDOW_HOURS"])
    tasks = (
        Task.query.join(Project)
        .filter(Task.due_date.isnot(None), Task.due_date <= window_end, Task.status != "done")
        .all()
    )
    notified = 0
    for task in tasks:
        kind = "overdue" if task.due_date < now else "deadline_due"
        reminder_key = f"deadline-reminder:{task.id}:{now.strftime('%Y%m%d%H')}"
        if extensions.redis_client:
            try:
                if not extensions.redis_client.set(reminder_key, "1", nx=True, ex=3600):
                    continue
            except Exception:
                logger.warning("Reminder deduplication unavailable for task %s", task.id)
        if _same_day_notification_exists(task.project.owner_id, kind, task.id, now):
            continue
        due_label = task.due_date.strftime("%b %d, %H:%M")
        title = f"Overdue: {task.title}" if kind == "overdue" else f"Due soon: {task.title}"
        db.session.add(
            Notification(
                user_id=task.project.owner_id,
                kind=kind,
                title=title[:160],
                body=f"'{task.title}' in {task.project.name} is due {due_label}.",
                task_id=task.id,
            )
        )
        logger.info("Deadline reminder queued for owner=%s task=%s due=%s", task.project.owner_id, task.id, task.due_date.isoformat())
        notified += 1

        # Dispatch email alert if owner has an email
        owner = db.session.get(User, task.project.owner_id)
        if owner and owner.email:
            try:
                send_deadline_email(
                    user_email=owner.email,
                    user_name=owner.full_name,
                    task_title=task.title,
                    project_name=task.project.name,
                    due_date_str=due_label,
                    is_overdue=(kind == "overdue"),
                )
            except Exception as mail_err:
                logger.warning("Failed sending deadline email for task %s to %s: %s", task.id, owner.email, mail_err)

    db.session.commit()
    return {"checked": len(tasks), "notified": notified, "generated_at": iso_utc(now)}


def run_daily_productivity_report():
    """Write one DailyReport per active user plus a matching notification,
    and dispatch the daily productivity digest email.
    """
    now = utcnow()
    today = now.date()
    users = User.query.filter_by(is_blocked=False).all()
    reports_written = 0
    for user in users:
        base_query = Task.query.join(Project).filter(Project.owner_id == user.id)
        total = base_query.count()
        if not total:
            continue
        completed = base_query.filter(Task.status == "done").count()
        overdue = base_query.filter(Task.due_date.isnot(None), Task.due_date < now, Task.status != "done").count()
        report = DailyReport.query.filter_by(user_id=user.id, report_date=today).first()
        if report:
            report.total_tasks = total
            report.completed_tasks = completed
            report.overdue_tasks = overdue
        else:
            report = DailyReport(
                user_id=user.id,
                report_date=today,
                total_tasks=total,
                completed_tasks=completed,
                overdue_tasks=overdue,
            )
            db.session.add(report)
        existing = Notification.query.filter_by(user_id=user.id, kind="daily_report").filter(
            func.date(Notification.created_at) == today
        ).first()
        body = f"{completed} of {total} tasks done, {overdue} overdue on {today.isoformat()}."
        is_new = existing is None
        if existing:
            existing.title = "Daily productivity report"
            existing.body = body
        else:
            db.session.add(
                Notification(
                    user_id=user.id,
                    kind="daily_report",
                    title="Daily productivity report",
                    body=body,
                )
            )
        reports_written += 1

        # Dispatch daily digest email once per day (repeat triggers only refresh the inbox row)
        if user.email and not is_new:
            logger.info("Daily digest email already sent today to %s; skipping resend.", user.email)
        if user.email and is_new:
            try:
                digest_stats = report.to_dict()
                send_daily_digest_email(
                    user_email=user.email,
                    user_name=user.full_name,
                    digest_data=digest_stats,
                )
            except Exception as mail_err:
                logger.warning("Failed sending daily digest email to %s: %s", user.email, mail_err)

    db.session.commit()
    report = {"generated_at": iso_utc(now), "reports_written": reports_written}
    logger.info("Daily productivity report generated: %s", report)
    return report



@celery.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_deadline_reminders(self):
    return run_deadline_reminders()


@celery.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def generate_daily_productivity_report(self):
    return run_daily_productivity_report()
