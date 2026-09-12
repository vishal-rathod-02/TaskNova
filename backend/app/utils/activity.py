import json

from ..extensions import db
from ..models import ActivityLog


def log_task_activity(task_id, user_id, action, detail=None):
    db.session.add(
        ActivityLog(
            task_id=task_id,
            user_id=user_id,
            action=action,
            details=json.dumps(detail) if detail is not None else None,
        )
    )
