from ..extensions import db
from .time import iso_utc, utcnow

# Universal slot classifications shared by every persona (corporate, maker,
# freelance, academic). Kept as a frozenset so validation stays DB-agnostic.
SLOT_TYPES = frozenset({"meeting", "focus_work", "operations", "habit", "personal"})

ALLOCATION_STATUSES = frozenset({"scheduled", "in_progress", "completed", "deferred"})


class TimetableSlot(db.Model):
    """A fixed weekly routine block or a single-date override owned by one user."""

    __tablename__ = "timetable_slot"
    __table_args__ = (
        db.Index("ix_timetable_slot_user_day", "user_id", "day_of_week"),
        db.Index("ix_timetable_slot_user_date", "user_id", "specific_date"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=True, index=True)
    title = db.Column(db.String(160), nullable=False)
    slot_type = db.Column(db.String(20), nullable=False, default="focus_work")
    # 0=Mon ... 6=Sun. Set for recurring weekly routine blocks.
    day_of_week = db.Column(db.Integer, nullable=True)
    # "HH:MM" 24-hour strings; stored as text to stay portable across SQLite/Postgres.
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    color_override = db.Column(db.String(20), nullable=True)
    is_recurring = db.Column(db.Boolean, nullable=False, default=True)
    # Concrete calendar date for one-off overrides; null for pure weekly routine.
    specific_date = db.Column(db.Date, nullable=True)
    # Persona template this block was created from (corporate/maker/academic/freelance);
    # null for hand-made blocks. Powers admin template adoption analytics.
    source_template = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    owner = db.relationship("User", back_populates="timetable_slots")
    project = db.relationship("Project", back_populates="timetable_slots")
    allocations = db.relationship(
        "TimetableAllocation", back_populates="slot", lazy="select", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def duration_minutes(self):
        try:
            sh, sm = (int(p) for p in str(self.start_time).split(":"))
            eh, em = (int(p) for p in str(self.end_time).split(":"))
            return (eh * 60 + em) - (sh * 60 + sm)
        except (ValueError, AttributeError):
            return 0

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "project_name": self.project.name if self.project else None,
            "title": self.title,
            "slot_type": self.slot_type,
            "day_of_week": self.day_of_week,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_minutes": self.duration_minutes,
            "location": self.location,
            "color_override": self.color_override,
            "is_recurring": self.is_recurring,
            "specific_date": self.specific_date.isoformat() if self.specific_date else None,
            "source_template": self.source_template,
            "allocations": [a.to_dict() for a in self.allocations] if self.allocations else [],
            "created_at": iso_utc(self.created_at),
        }


class RoutineTemplateState(db.Model):
    """Platform-governor switchboard for persona quick-start templates.

    One row per template name; admins toggle availability without redeploying.
    Seeded with all-enabled defaults on app boot (see sync_database_schema).
    """

    __tablename__ = "routine_template_state"

    template_name = db.Column(db.String(20), primary_key=True)
    is_enabled = db.Column(db.Boolean, nullable=False, default=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=utcnow, onupdate=utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self, extra=None):
        payload = {
            "name": self.template_name,
            "is_enabled": self.is_enabled,
            "updated_at": iso_utc(self.updated_at),
        }
        if extra:
            payload.update(extra)
        return payload


class TimetableAllocation(db.Model):
    """Links a backlog task into a timetable slot (the "Plan My Day" output)."""

    __tablename__ = "timetable_allocation"
    __table_args__ = (db.UniqueConstraint("slot_id", "task_id", name="uq_allocation_slot_task"),)

    id = db.Column(db.Integer, primary_key=True)
    slot_id = db.Column(db.Integer, db.ForeignKey("timetable_slot.id"), nullable=False, index=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="scheduled")
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    slot = db.relationship("TimetableSlot", back_populates="allocations")
    task = db.relationship("Task", back_populates="timetable_allocations")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "slot_id": self.slot_id,
            "task_id": self.task_id,
            "task_title": self.task.title if self.task else None,
            "status": self.status,
            "created_at": iso_utc(self.created_at),
        }
