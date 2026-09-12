import logging
from datetime import timedelta

from flask import current_app

from .. import extensions
from ..celery_app import celery
from ..models import Project, Task
from ..models.time import utcnow

logger = logging.getLogger(__name__)


@celery.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_deadline_reminders(self):
    now = utcnow()
    window_end = now + timedelta(hours=current_app.config["REMINDER_WINDOW_HOURS"])
    tasks = (
        Task.query.join(Project)
        .filter(Task.due_date.isnot(None), Task.due_date <= window_end, Task.status != "done")
        .all()
    )
    notified = 0
    for task in tasks:
        reminder_key = f"deadline-reminder:{task.id}:{now.strftime('%Y%m%d%H')}"
        if extensions.redis_client:
            try:
                if not extensions.redis_client.set(reminder_key, "1", nx=True, ex=3600):
                    continue
            except Exception:
                logger.warning("Reminder deduplication unavailable for task %s", task.id)
        logger.info("Deadline reminder queued for owner=%s task=%s due=%s", task.project.owner_id, task.id, task.due_date.isoformat())
        notified += 1
    return {"checked": len(tasks), "notified": notified, "generated_at": now.isoformat()}


@celery.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def generate_daily_productivity_report(self):
    now = utcnow()
    completed = Task.query.filter(Task.status == "done", Task.updated_at >= now - timedelta(days=1)).count()
    overdue = Task.query.filter(Task.due_date.isnot(None), Task.due_date < now, Task.status != "done").count()
    report = {"generated_at": now.isoformat(), "completed_last_24h": completed, "overdue_tasks": overdue}
    logger.info("Daily productivity report generated: %s", report)
    return report
