from celery import Celery, Task
from celery.schedules import crontab

celery = Celery("tasknova", include=["app.tasks_jobs.tasks"])


def init_celery(app):
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        timezone="UTC",
        task_track_started=True,
        task_time_limit=180,
        task_soft_time_limit=120,
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        beat_schedule={
            "send-deadline-reminders": {
                "task": "app.tasks_jobs.tasks.send_deadline_reminders",
                "schedule": crontab(minute="*/15"),
            },
            "generate-daily-productivity-report": {
                "task": "app.tasks_jobs.tasks.generate_daily_productivity_report",
                "schedule": crontab(hour=0, minute=5),
            },
        },
    )

    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = FlaskTask
    return celery
