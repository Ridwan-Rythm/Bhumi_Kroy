"""POST /verify logic. Precedence: TAMPERED > UNKNOWN > INTEGRITY_ALERT > GENUINE_SUPERSEDED
> GENUINE_EXPIRED > GENUINE_CURRENT (contract section 5)."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from app.core import clock
from app.core.errors import AppError
from app.engine.report_builder import normalize_short_code
from app.ledger import chain, signer

REPORT_KEYS = ("report_id", "short_code", "plot_id", "verdict", "issued_at", "valid_until")
NOT_CHECKED = {"ok": False, "broken_at_seq": None, "reason": None}  # ledger not examined for this state


def _result(state, sig_valid, report, diff, ledger, now):
    return {"state": state, "signature_valid": sig_valid, "report": report, "diff": diff,
            "ledger": ledger, "checked_at": clock.iso(now)}


def verify(conn: sqlite3.Connection, short_code: str | None = None, payload_b64: str | None = None,
           signature_b64: str | None = None, now: datetime | None = None) -> dict:
    now = now or clock.now()
    if payload_b64 is not None or signature_b64 is not None:
        if not payload_b64 or not signature_b64:
            raise AppError("VALIDATION_ERROR", "payload_b64 and signature_b64 are both required", "payload_b64")
        raw, sig = _decode(payload_b64), signature_b64
    elif short_code:
        row = conn.execute("SELECT json FROM reports WHERE REPLACE(short_code,'-','')=?",
                           (normalize_short_code(short_code),)).fetchone()
        if row is None:
            return _result("UNKNOWN", False, None, None, NOT_CHECKED, now)
        stored = json.loads(row["json"])
        raw, sig = _decode(stored["signed_payload_b64"]), stored["signature_b64"]
    else:
        raise AppError("VALIDATION_ERROR", "short_code or payload_b64 + signature_b64 is required", "short_code")

    payload = _parse(raw) if raw is not None else None
    if payload is None or not signer.verify(raw, sig):
        return _result("TAMPERED", False, None, None, NOT_CHECKED, now)
    report = {k: payload.get(k) for k in REPORT_KEYS}

    plot_id = payload.get("plot_id")
    if not conn.execute("SELECT 1 FROM plots WHERE plot_id=?", (plot_id,)).fetchone():
        return _result("UNKNOWN", True, None, None, NOT_CHECKED, now)
    st = chain.verify(conn, plot_id)
    ledger = {"ok": st.ok, "broken_at_seq": st.broken_at_seq, "reason": st.reason}
    if not st.ok:
        return _result("INTEGRITY_ALERT", True, report, None, ledger, now)

    newer = conn.execute("SELECT record_id FROM ledger WHERE plot_id=? AND seq>? ORDER BY seq",
                         (plot_id, payload["ledger_height"])).fetchall()
    if newer:
        diff = []
        for e in newer:
            data = json.loads(conn.execute("SELECT data_json FROM records WHERE record_id=?",
                                           (e["record_id"],)).fetchone()["data_json"])
            diff.append({"change": "ADDED", "kind": data["type"], "record_ref": e["record_id"],
                         "date": data.get("date", "")})
        return _result("GENUINE_SUPERSEDED", True, report, diff, ledger, now)
    if now > clock.parse_iso(payload["valid_until"]):
        return _result("GENUINE_EXPIRED", True, report, None, ledger, now)
    return _result("GENUINE_CURRENT", True, report, None, ledger, now)


def _decode(text: str) -> bytes | None:
    try:
        return signer.b64u_decode(text)
    except Exception:  # noqa: BLE001 - any malformed input is simply "tampered"
        return None


def _parse(raw: bytes) -> dict | None:
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    need = {"report_id", "short_code", "plot_id", "verdict", "issued_at", "valid_until", "ledger_height"}
    return obj if isinstance(obj, dict) and need <= set(obj) else None
