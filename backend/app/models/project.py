from ..extensions import db
from .time import iso_utc, utcnow


class Project(db.Model):
    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    owner = db.relationship("User", back_populates="projects")
    tasks = db.relationship("Task", back_populates="project", lazy="select", cascade="all, delete-orphan")

    def to_dict(self, include_task_count=False):
        payload = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "created_at": iso_utc(self.created_at),
        }
        if include_task_count:
            payload["task_count"] = len(self.tasks)
        return payload
