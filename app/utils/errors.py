from __future__ import annotations


class AppError(Exception):
    status_code = 400
    error_code = "app_error"

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details


class ValidationError(AppError):
    status_code = 400
    error_code = "validation_error"


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"


class ConflictError(AppError):
    status_code = 409
    error_code = "conflict"


class LLMClientError(AppError):
    status_code = 502
    error_code = "llm_upstream_error"
