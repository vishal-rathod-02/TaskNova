from ..extensions import db
from .time import iso_utc, utcnow


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
        return {
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "body": self.body,
            "task_id": self.task_id,
            "is_read": self.is_read,
            "created_at": iso_utc(self.created_at),
        }


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
        return {
            "id": self.id,
            "report_date": self.report_date.isoformat(),
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "overdue_tasks": self.overdue_tasks,
            "created_at": iso_utc(self.created_at),
        }
