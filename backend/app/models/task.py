from ..extensions import db
from .time import iso_utc, utcnow


class Task(db.Model):
    __tablename__ = "task"
    __table_args__ = (db.Index("ix_task_status_due_date", "status", "deadline"),)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), nullable=False, default="medium")
    status = db.Column(db.String(20), nullable=False, default="todo")
    # The existing SQLite schema used `deadline`; retain the physical column while exposing `due_date` in v1 APIs.
    due_date = db.Column("deadline", db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    project = db.relationship("Project", back_populates="tasks")
    creator = db.relationship("User", back_populates="created_tasks", foreign_keys=[created_by])
    activity_logs = db.relationship("ActivityLog", back_populates="task", lazy="select", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            # New writes arrive UTC-normalized from the frontend. Legacy rows
            # keep their previous comparison basis; re-save a due date to
            # normalize it if its displayed time drifts by your UTC offset.
            "due_date": iso_utc(self.due_date),
            "project_id": self.project_id,
            "project_name": self.project.name if self.project else None,
            "created_by": self.created_by,
            "created_at": iso_utc(self.created_at),
            "updated_at": iso_utc(self.updated_at),
        }
