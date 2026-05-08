from datetime import datetime, timedelta

from . import create_app
from .celery_app import celery
from .extensions import db
from .models import Task, User

app = create_app()


@celery.task
def send_deadline_reminders():
    with app.app_context():
        tomorrow = datetime.utcnow() + timedelta(days=1)
        tasks = Task.query.filter(
            Task.deadline.isnot(None),
            Task.deadline <= tomorrow,
            Task.status != "done",
            Task.assignee_id.isnot(None),
        ).all()
        reminders = []
        for task in tasks:
            user = User.query.get(task.assignee_id)
            if user:
                reminders.append(
                    {
                        "email": user.email,
                        "task_title": task.title,
                        "deadline": task.deadline.isoformat(),
                    }
                )
        return {"sent_reminders": len(reminders), "items": reminders}


@celery.task
def generate_daily_productivity_report():
    with app.app_context():
        total = Task.query.count()
        completed = Task.query.filter_by(status="done").count()
        overdue = Task.query.filter(Task.deadline < datetime.utcnow(), Task.status != "done").count()
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "total_tasks": total,
            "completed_tasks": completed,
            "overdue_tasks": overdue,
        }
