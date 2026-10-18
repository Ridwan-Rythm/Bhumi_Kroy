"""HTTP routes (contract section 5). Thin wrappers over app.engine.pipeline and app.services.*."""
from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import APIRouter, Depends, Request

from app.api.ratelimit import rate_limit
from app.core import db
from app.core.errors import AppError
from app.engine.pipeline import run_check
from app.ledger import signer
from app.services import demo_service as demo
from app.services import verify_service

SAMPLES_PATH = Path(__file__).resolve().parents[2] / "seed" / "golden" / "samples.json"

api = APIRouter(prefix="/api/v1")


async def demo_enabled() -> None:
    demo.require_demo()  # DEMO_DISABLED (404) before anything else, even before the body is parsed


demo_router = APIRouter(prefix="/demo", dependencies=[Depends(demo_enabled)])  # NOT under /api/v1 (section 5)


async def get_conn():
    """One SQLite connection per request, opened and closed in the event-loop thread."""
    conn = db.connect()
    try:
        yield conn
    finally:
        conn.close()


async def json_body(request: Request) -> dict:
    try:
        body = await request.json()
    except (ValueError, UnicodeDecodeError):
        raise AppError("VALIDATION_ERROR", "Request body must be valid JSON") from None
    if not isinstance(body, dict):
        raise AppError("VALIDATION_ERROR", "Request body must be a JSON object")
    return body


def _text(body: dict, key: str, required: bool = True) -> str | None:
    v = body.get(key)
    if v is None and not required:
        return None
    if not isinstance(v, str) or not v.strip():
        raise AppError("VALIDATION_ERROR", f"{key} is required and must be text", key)
    return v


# ---- meta -----------------------------------------------------------------------------------------
@api.get("/health")
async def health() -> dict:
    return {"ok": True, "demo_mode": os.environ.get("DEMO_MODE") == "1"}


@api.get("/meta/locations")
async def locations(conn=Depends(get_conn)) -> dict:
    rows = conn.execute("SELECT * FROM admin_units ORDER BY rowid").fetchall()
    districts: dict[str, dict] = {}
    upazilas: dict[str, dict] = {}
    for r in rows:
        if r["kind"] == "district":
            districts[r["id"]] = {"id": r["id"], "name_bn": r["name_bn"], "name_en": r["name_en"], "upazilas": []}
        elif r["kind"] == "upazila":
            u = {"id": r["id"], "name_bn": r["name_bn"], "name_en": r["name_en"], "mouzas": []}
            upazilas[r["id"]] = u
            districts[r["parent_id"]]["upazilas"].append(u)
        elif r["kind"] == "mouza":
            upazilas[r["parent_id"]]["mouzas"].append(
                {"id": r["id"], "name_bn": r["name_bn"], "name_en": r["name_en"], "jl_no": r["jl_no"]})
    return {"districts": list(districts.values())}


@api.get("/meta/samples")
async def samples() -> list:
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


@api.get("/meta/pubkey")
async def pubkey() -> dict:
    return {"key_id": signer.KEY_ID, "alg": "Ed25519", "public_key_b64": signer.public_key_b64()}


# ---- check / reports / verify ---------------------------------------------------------------------
@api.post("/check", dependencies=[Depends(rate_limit)])
async def check(body: dict = Depends(json_body), conn=Depends(get_conn)) -> dict:
    # HTTP 200 for every verdict, including RED, GREY and INTEGRITY_ALERT.
    return await run_check(conn, body)


@api.get("/reports/{report_id}")
async def get_report(report_id: str, conn=Depends(get_conn)) -> dict:
    row = conn.execute("SELECT json FROM reports WHERE report_id=?", (report_id,)).fetchone()
    if row is None:
        raise AppError("NOT_FOUND", "No such report", "report_id")
    return json.loads(row["json"])


@api.post("/verify", dependencies=[Depends(rate_limit)])
async def verify(body: dict = Depends(json_body), conn=Depends(get_conn)) -> dict:
    if "short_code" in body:
        return verify_service.verify(conn, short_code=_text(body, "short_code"))
    if "payload_b64" in body or "signature_b64" in body:
        return verify_service.verify(conn, payload_b64=_text(body, "payload_b64"),
                                     signature_b64=_text(body, "signature_b64"))
    raise AppError("VALIDATION_ERROR", "Send short_code, or payload_b64 and signature_b64", "short_code")


# ---- demo (DEMO_MODE=1) ---------------------------------------------------------------------------
@demo_router.post("/tamper")
async def demo_tamper(body: dict = Depends(json_body), conn=Depends(get_conn)) -> dict:
    demo.require_demo()
    return demo.tamper(conn, _text(body, "plot_id"), _text(body, "kind"))


@demo_router.post("/add-event")
async def demo_add_event(body: dict = Depends(json_body), conn=Depends(get_conn)) -> dict:
    demo.require_demo()
    return demo.add_event(conn, _text(body, "plot_id"), _text(body, "kind"))


@demo_router.post("/reset")
async def demo_reset(conn=Depends(get_conn)) -> dict:
    return demo.reset(conn)


@demo_router.get("/ledger/{plot_id}")
async def demo_ledger(plot_id: str, conn=Depends(get_conn)) -> dict:
    return demo.ledger_view(conn, plot_id)


@demo_router.post("/clock")
async def demo_clock(body: dict = Depends(json_body)) -> dict:
    demo.require_demo()
    return demo.set_clock(body.get("offset_days"))
