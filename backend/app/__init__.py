from app.models import DailyReport
from app.models import Notification
import json
import logging
from time import perf_counter

from flask import Flask, g, jsonify, request

from .admin import admin_bp
from .analytics import analytics_bp
from .auth import auth_bp
from .calendar import calendar_bp
from .celery_app import init_celery
from .commands import register_commands
from .config import Config
from .extensions import cors, db, init_redis, jwt, migrate
from .models import ActivityLog, Project, Task, User
from .notifications import notifications_bp
from .projects import projects_bp
from .tasks import tasks_bp


import os
import secrets
from sqlalchemy import inspect, text


def _ensure_database_schema(app):
    """Safely apply schema additions for existing SQLite/PostgreSQL tables without breaking existing data."""
    try:
        with app.app_context():
            db.create_all()
            dialect = db.engine.dialect.name.lower()

            if dialect == "postgresql":
                # PostgreSQL natively supports ADD COLUMN IF NOT EXISTS and requires double quotes for "user"
                with db.engine.begin() as conn:
                    conn.execute(
                        text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS email_digest_enabled BOOLEAN NOT NULL DEFAULT TRUE;')
                    )
                    conn.execute(
                        text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS email_alerts_enabled BOOLEAN NOT NULL DEFAULT TRUE;')
                    )
                    conn.execute(
                        text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS calendar_token VARCHAR(64);')
                    )
                app.logger.info("PostgreSQL schema sync executed successfully.")
            else:
                with db.engine.begin() as conn:
                    inspector = inspect(conn)
                    table_names = set(inspector.get_table_names())
                    if "user" in table_names:
                        cols = {c["name"] for c in inspector.get_columns("user")}
                        if "email_digest_enabled" not in cols:
                            conn.execute(text('ALTER TABLE "user" ADD COLUMN email_digest_enabled BOOLEAN NOT NULL DEFAULT 1'))
                        if "email_alerts_enabled" not in cols:
                            conn.execute(text('ALTER TABLE "user" ADD COLUMN email_alerts_enabled BOOLEAN NOT NULL DEFAULT 1'))
                        if "calendar_token" not in cols:
                            conn.execute(text('ALTER TABLE "user" ADD COLUMN calendar_token VARCHAR(64)'))

            # Backfill any legacy users without calendar tokens
            try:
                legacy_users = User.query.filter((User.calendar_token == None) | (User.calendar_token == "")).all()
                if legacy_users:
                    for u in legacy_users:
                        u.calendar_token = secrets.token_urlsafe(32)
                    db.session.commit()
            except Exception as backfill_err:
                db.session.rollback()
                app.logger.warning("Calendar token backfill notice: %s", backfill_err)

    except Exception as exc:
        app.logger.error("Database schema auto-sync failed: %s", exc, exc_info=True)


def _bootstrap_admin(app):
    admin_email = os.getenv("ADMIN_EMAIL", "admin@tasknova.com").lower().strip()
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_name = os.getenv("ADMIN_NAME", "System Admin")

    if not admin_email or not admin_password:
        return

    try:
        with app.app_context():
            # If user has configured their own private admin email, purge the public default 'admin@tasknova.com'
            if admin_email != "admin@tasknova.com":
                legacy_admin = User.query.filter_by(email="admin@tasknova.com").first()
                if legacy_admin:
                    Project.query.filter_by(owner_id=legacy_admin.id).delete(synchronize_session=False)
                    Notification.query.filter_by(user_id=legacy_admin.id).delete(synchronize_session=False)
                    DailyReport.query.filter_by(user_id=legacy_admin.id).delete(synchronize_session=False)
                    ActivityLog.query.filter_by(user_id=legacy_admin.id).delete(synchronize_session=False)
                    db.session.delete(legacy_admin)
                    db.session.commit()
                    app.logger.info("Purged default public admin: admin@tasknova.com")

            admin = User.query.filter_by(email=admin_email).first()
            if not admin:
                admin = User(full_name=admin_name, email=admin_email, role="admin")
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                app.logger.info("Auto-bootstrapped admin account: %s", admin_email)
            else:
                updated = False
                if admin.role != "admin":
                    admin.role = "admin"
                    updated = True
                if admin.full_name != admin_name:
                    admin.full_name = admin_name
                    updated = True
                if os.getenv("ADMIN_PASSWORD"):
                    admin.set_password(admin_password)
                    updated = True
                if updated:
                    db.session.commit()
                    app.logger.info("Synced admin credentials from environment: %s", admin_email)
    except Exception as exc:
        app.logger.warning("Admin bootstrap notice: %s", exc)


def create_app(config_override=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_override:
        app.config.update(config_override)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}},
        allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        supports_credentials=True,
    )
    init_redis(app)
    init_celery(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(notifications_bp)
    register_commands(app)

    if app.config.get("AUTO_CREATE_DB", True):
        _ensure_database_schema(app)
        _bootstrap_admin(app)

    @app.before_request
    def begin_request_timer():
        g.request_started_at = perf_counter()

    @app.after_request
    def log_and_secure_request(response):
        # Attach OWASP security response headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"

        if request.path.startswith("/api/"):
            app.logger.info(
                json.dumps(
                    {
                        "event": "api_request",
                        "method": request.method,
                        "path": request.path,
                        "status": response.status_code,
                        "duration_ms": round((perf_counter() - g.get("request_started_at", perf_counter())) * 1000, 2),
                    }
                )
            )
        return response

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"message": "Resource not found."}), 404
        return error

    @app.errorhandler(500)
    def server_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"message": "Internal server error."}), 500
        return error

    @app.errorhandler(Exception)
    def handle_unhandled_exception(error):
        app.logger.error("Unhandled exception on %s %s: %s", request.method, request.path, error, exc_info=True)
        if request.path.startswith("/api/"):
            return jsonify({"message": "An unexpected server error occurred."}), 500
        return error

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "tasknova-api"})

    return app
