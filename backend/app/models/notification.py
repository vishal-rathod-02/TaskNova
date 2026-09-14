import re

from ..extensions import db
from .time import iso_utc, utcnow


def _compute_digest_stats(total, completed, overdue, report_date_str=None):
    total = max(0, total or 0)
    completed = max(0, completed or 0)
    overdue = max(0, overdue or 0)
    in_progress = max(0, total - completed - overdue)
    rate = round((completed / total * 100), 1) if total > 0 else 0

    if rate >= 80:
        momentum = "Peak Velocity"
        grade = "A+"
        quote = "Outstanding execution! You've crushed the vast majority of your active coursework."
    elif rate >= 60:
        momentum = "Strong Progress"
        grade = "A"
        quote = "Great momentum! You're making swift progress through your active subjects."
    elif rate >= 40:
        momentum = "Steady Momentum"
        grade = "B"
        quote = "Solid daily rhythm. Keep pushing to close out your upcoming assignments."
    elif rate > 0:
        momentum = "Active Progress"
        grade = "C"
        quote = "Good start! Focus on high-priority tasks to boost your completion velocity."
    else:
        momentum = "Sprint Setup"
        grade = "In Progress"
        quote = "Your study backlog is ready. Plan a Pomodoro sprint to kickstart your progress."

    return {
        "report_date": report_date_str,
        "total_tasks": total,
        "completed_tasks": completed,
        "overdue_tasks": overdue,
        "in_progress_tasks": in_progress,
        "completion_rate": rate,
        "momentum": momentum,
        "grade": grade,
        "quote": quote,
    }


class Notification(db.Model):
    __tablename__ = "notification"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    kind = db.Column(db.String(30), nullable=False, default="deadline_due")
    title = db.Column(db.String(160), nullable=False)
    body = db.Column(db.Text, nullable=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=True, index=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    user = db.relationship("User", back_populates="notifications")

    def to_dict(self):
        data = {
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "body": self.body,
            "task_id": self.task_id,
            "is_read": self.is_read,
            "created_at": iso_utc(self.created_at),
        }
        if self.kind == "daily_report":
            report_date = self.created_at.date()
            report = DailyReport.query.filter_by(user_id=self.user_id, report_date=report_date).first()
            if report:
                data["digest"] = report.to_dict()
            else:
                body_text = self.body or ""
                match = re.search(r"(\d+)\s+of\s+(\d+)\s+tasks done(?:,\s+(\d+)\s+overdue)?", body_text)
                if match:
                    comp = int(match.group(1))
                    tot = int(match.group(2))
                    ovd = int(match.group(3) or 0)
                    data["digest"] = _compute_digest_stats(tot, comp, ovd, report_date.isoformat())
                else:
                    data["digest"] = _compute_digest_stats(0, 0, 0, report_date.isoformat())
        return data


class DailyReport(db.Model):
    __tablename__ = "daily_report"
    __table_args__ = (db.UniqueConstraint("user_id", "report_date", name="uq_daily_report_user_date"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    report_date = db.Column(db.Date, nullable=False, index=True)
    total_tasks = db.Column(db.Integer, nullable=False, default=0)
    completed_tasks = db.Column(db.Integer, nullable=False, default=0)
    overdue_tasks = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    user = db.relationship("User", back_populates="daily_reports")

    def to_dict(self):
        stats = _compute_digest_stats(
            self.total_tasks,
            self.completed_tasks,
            self.overdue_tasks,
            self.report_date.isoformat(),
        )
        return {
            "id": self.id,
            "created_at": iso_utc(self.created_at),
            **stats,
        }

