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
