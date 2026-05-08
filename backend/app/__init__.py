import os

from flask import Flask, jsonify, request

from .config import Config
from .extensions import cors, db, init_redis, jwt, migrate
from .routes import api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )
    init_redis(app)

    app.register_blueprint(api)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    if app.config.get("AUTO_CREATE_DB", True):
        with app.app_context():
            db.create_all()

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        return response

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "tasknova-api"})

    return app
