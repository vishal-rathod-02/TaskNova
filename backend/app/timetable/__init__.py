from flask import Blueprint

timetable_bp = Blueprint("timetable", __name__, url_prefix="/api/timetable")

from . import routes  # noqa: E402,F401
