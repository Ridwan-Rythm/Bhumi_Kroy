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
        code = normalize_short_code(short_code)
        row = None
        if code is not None:  # a malformed code can never match; do not "repair" it into one that does
            row = conn.execute("SELECT json FROM reports WHERE REPLACE(short_code,'-','')=?",
                               (code,)).fetchone()
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

    # The ledger itself is internally consistent. Now check it against what the report pinned.
    pinned = _pinned_mismatch(conn, plot_id, payload, st)
    if pinned is not None:
        ledger = {"ok": False, "broken_at_seq": None, "reason": pinned}
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


def _pinned_mismatch(conn: sqlite3.Connection, plot_id: str, payload: dict, st) -> str | None:
    """Compare the ledger_height / ledger_head the signed report pinned with the chain as it is now.

    - height above the current height: entries the report relied on are gone (rolled back), whether or
      not someone also removed the matching checkpoints.  -> "height_mismatch"
    - the entry at the pinned height has a different hash than the pinned head: history was replaced
      (for example reloaded from a different seed) even though the height is unchanged or higher.
      -> "checkpoint_mismatch"
    Entries *after* the pinned height are fine: that is a legitimate update (GENUINE_SUPERSEDED)."""
    height = payload["ledger_height"]
    if height > st.height:
        return "height_mismatch"
    if height == 0:
        pinned_now = chain.GENESIS
    else:
        row = conn.execute("SELECT entry_hash FROM ledger WHERE plot_id=? AND seq=?",
                           (plot_id, height)).fetchone()
        pinned_now = row["entry_hash"] if row else None
    if pinned_now != payload["ledger_head"]:
        return "checkpoint_mismatch"
    return None


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
    need = {"report_id", "short_code", "plot_id", "verdict", "issued_at", "valid_until", "ledger_height",
            "ledger_head"}
    if not isinstance(obj, dict) or not need <= set(obj):
        return None
    height = obj["ledger_height"]
    if isinstance(height, bool) or not isinstance(height, int) or height < 0:
        return None
    if not isinstance(obj["ledger_head"], str) or not isinstance(obj["plot_id"], str):
        return None
    try:
        clock.parse_iso(obj["valid_until"])
    except (TypeError, ValueError):
        return None
    return obj
