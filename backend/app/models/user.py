from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from .time import utcnow


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    is_blocked = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    projects = db.relationship("Project", back_populates="owner", lazy="select", cascade="all, delete-orphan")
    created_tasks = db.relationship("Task", back_populates="creator", lazy="select", foreign_keys="Task.created_by")
    activity_logs = db.relationship("ActivityLog", back_populates="actor", lazy="select")
    notifications = db.relationship("Notification", back_populates="user", lazy="select", cascade="all, delete-orphan")
    daily_reports = db.relationship("DailyReport", back_populates="user", lazy="select", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "is_blocked": self.is_blocked,
            "created_at": self.created_at.isoformat(),
        }
