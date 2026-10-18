"""FastAPI entry point.  Run from backend/:  uvicorn app.main:app --reload --port 8000

Environment (contract section 4): DEMO_MODE=1 enables /demo/*, DB_PATH, SIGNING_KEY_B64 (optional),
CORS_ORIGINS (comma separated, extra to the two Vite dev origins), RATE_LIMIT_PER_MIN (default 30).
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import api, demo_router
from app.core import db
from app.core.errors import AppError
from app.ledger import signer

log = logging.getLogger("landcheck")
DEV_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


def ensure_seeded() -> None:
    """First run: create the schema and load the deterministic seed. Existing data is left alone."""
    from seed import load

    conn = db.connect()
    try:
        if conn.execute("SELECT COUNT(*) FROM plots").fetchone()[0] == 0:
            load.load(conn)
            log.info("seeded %s", db.db_path())
    finally:
        conn.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    signer.load_or_create_key()  # fail at startup, not on the first request
    ensure_seeded()
    yield


def _error(code: str, message: str, status: int, field: str | None = None, headers: dict | None = None):
    return JSONResponse({"error": {"code": code, "message": message, "field": field}}, status_code=status,
                        headers=headers)


def create_app() -> FastAPI:
    app = FastAPI(title="Bhumi_Kroy API", version="1", lifespan=lifespan)
    extra = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
    app.add_middleware(CORSMiddleware, allow_origins=DEV_ORIGINS + extra, allow_methods=["GET", "POST"],
                       allow_headers=["Content-Type"])

    @app.exception_handler(AppError)
    async def on_app_error(_: Request, e: AppError):
        headers = {"Retry-After": "60"} if e.code == "RATE_LIMITED" else None
        return _error(e.code, e.message, e.http_status, e.field, headers)

    @app.exception_handler(RequestValidationError)
    async def on_validation(_: Request, e: RequestValidationError):
        first = e.errors()[0] if e.errors() else {}
        field = ".".join(str(p) for p in first.get("loc", ()) if p not in ("body", "path", "query")) or None
        return _error("VALIDATION_ERROR", str(first.get("msg", "Invalid request")), 422, field)

    @app.exception_handler(StarletteHTTPException)
    async def on_http(_: Request, e: StarletteHTTPException):
        if e.status_code in (404, 405):
            return _error("NOT_FOUND", "No such endpoint", 404)
        return _error("INTERNAL", "Request failed", e.status_code)

    @app.exception_handler(Exception)
    async def on_crash(_: Request, e: Exception):
        log.exception("unhandled error", exc_info=e)
        return _error("INTERNAL", "Something went wrong on our side", 500)  # never leak internals

    app.include_router(api)
    app.include_router(demo_router)
    return app


app = create_app()
