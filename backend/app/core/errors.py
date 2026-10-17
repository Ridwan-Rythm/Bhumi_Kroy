"""Uniform application errors. The API layer maps them to {"error": {code, message, field}}."""
from __future__ import annotations

STATUS = {
    "VALIDATION_ERROR": 422,
    "NOT_FOUND": 404,
    "RATE_LIMITED": 429,
    "DEMO_DISABLED": 404,
    "NOT_IMPLEMENTED": 501,
    "INTERNAL": 500,
}


class AppError(Exception):
    def __init__(self, code: str, message: str, field: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field

    @property
    def http_status(self) -> int:
        return STATUS[self.code]

    def to_dict(self) -> dict:
        return {"error": {"code": self.code, "message": self.message, "field": self.field}}
