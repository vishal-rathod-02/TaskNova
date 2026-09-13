import json
import logging
from time import perf_counter

from flask import Flask, g, jsonify, request

from .admin import admin_bp
from .analytics import analytics_bp
from .auth import auth_bp
from .celery_app import init_celery
from .commands import register_commands
from .config import Config
from .extensions import cors, db, init_redis, jwt, migrate
from .models import ActivityLog, Project, Task, User
from .notifications import notifications_bp
from .projects import projects_bp
from .tasks import tasks_bp


import os

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
    app.register_blueprint(admin_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(notifications_bp)
    register_commands(app)

    if app.config.get("AUTO_CREATE_DB", True):
        with app.app_context():
            db.create_all()
        _bootstrap_admin(app)

    @app.before_request
    def begin_request_timer():
        g.request_started_at = perf_counter()

    @app.after_request
    def log_request(response):
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

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "tasknova-api"})

    return app
