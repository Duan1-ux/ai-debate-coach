from __future__ import annotations

import logging

from flask import Flask, jsonify

from app.config import get_config
from app.controllers.debate_controller import debate_bp
from app.extensions import db
from app.utils.errors import AppError


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config())

    if test_config:
        app.config.update(test_config)

    _configure_logging(app)
    db.init_app(app)

    app.register_blueprint(debate_bp, url_prefix="/api/debate")
    _register_error_handlers(app)
    _register_health_check(app)

    return app


def _configure_logging(app: Flask) -> None:
    logging.basicConfig(
        level=getattr(logging, app.config["LOG_LEVEL"], logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        payload = {
            "error": {
                "code": error.error_code,
                "message": error.message,
                "details": error.details,
            }
        }
        return jsonify(payload), error.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unhandled exception: %s", error)
        payload = {
            "error": {
                "code": "internal_server_error",
                "message": "服务器内部错误，请稍后重试。",
                "details": None,
            }
        }
        return jsonify(payload), 500


def _register_health_check(app: Flask) -> None:
    @app.get("/health")
    def health_check():
        return {
            "service": app.config["APP_NAME"],
            "status": "ok",
            "environment": app.config["APP_ENV"],
        }
