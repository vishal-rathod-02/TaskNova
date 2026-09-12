import json

from ..extensions import db
from .time import utcnow


class ActivityLog(db.Model):
    __tablename__ = "activity_log"

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    task = db.relationship("Task", back_populates="activity_logs")
    actor = db.relationship("User", back_populates="activity_logs")

    def to_dict(self):
        try:
            detail = json.loads(self.details) if self.details else None
        except json.JSONDecodeError:
            detail = self.details
        return {
            "id": self.id,
            "action": self.action,
            "detail": detail,
            "created_at": self.created_at.isoformat(),
            "task_id": self.task_id,
            "actor_id": self.user_id,
            "actor_name": self.actor.full_name if self.actor else "Unknown user",
        }
