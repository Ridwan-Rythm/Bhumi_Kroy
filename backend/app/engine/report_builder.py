"""Fill every Report field (contract section 6), sign it and store it."""
from __future__ import annotations

import json
import secrets
import sqlite3
from datetime import datetime, timedelta

from app.core import clock
from app.core.errors import AppError
from app.engine import coverage as cov
from app.engine.title_graph import frac_text
from app.ledger import chain, checkpoint, signer

SHORT_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
VALID_DAYS = 7
MAX_ISSUE_ATTEMPTS = 25
SHORT_LEN = 8


def normalize_short_code(code: object) -> str | None:
    """'k7m2-9qxa' / 'K7M2 9QXA' -> 'K7M29QXA'. Returns None unless the text is exactly 8 characters
    from SHORT_ALPHABET once case, one optional hyphen or space in the middle and the ends are
    ignored. Stray or look-alike characters (I, L, O, 0, 1) make the code invalid; they are never
    silently dropped, because 'NQJ45NNW0000' must not resolve to a real report."""
    if not isinstance(code, str):
        return None
    text = code.strip().upper()
    if len(text) == SHORT_LEN + 1 and text[4] in "- ":
        text = text[:4] + text[5:]
    if len(text) != SHORT_LEN or any(ch not in SHORT_ALPHABET for ch in text):
        return None
    return text


def new_short_code(conn: sqlite3.Connection) -> str:
    while True:
        raw = "".join(secrets.choice(SHORT_ALPHABET) for _ in range(SHORT_LEN))
        code = f"{raw[:4]}-{raw[4:]}"
        if not conn.execute("SELECT 1 FROM reports WHERE short_code=?", (code,)).fetchone():
            return code


def new_report_id(conn: sqlite3.Connection, now: datetime, skip: int = 0) -> str:
    """Next free RPT-<year>-<n>. n is MAX+1 (never COUNT+1, which repeats after any gap).
    `skip` lets the caller step past an id that another writer took between this read and the INSERT."""
    prefix = f"RPT-{now.year}-"
    row = conn.execute("SELECT MAX(CAST(SUBSTR(report_id, ?) AS INTEGER)) FROM reports WHERE report_id LIKE ?",
                       (len(prefix) + 1, prefix + "%")).fetchone()
    return f"{prefix}{(row[0] or 0) + 1 + skip:06d}"


def findings_hash(findings: list[dict]) -> str:
    ordered = sorted(findings, key=lambda f: (f["rule_id"], f["evidence"]))
    return chain.sha256_hex(signer.canonical(ordered))


def build(conn: sqlite3.Connection, plot: dict, req: dict, sources: dict, ledger, graph, match: dict,
          findings: list[dict], coverage: dict, verdict: str, now: datetime) -> dict:
    timeline = graph.timeline()
    flagged: dict[str, list[str]] = {}
    for f in findings:
        for ref in f["evidence"]:
            flagged.setdefault(ref, []).append(f["rule_id"])
    for ev in timeline:
        ev["flagged_by"] = sorted(set(flagged.get(ev["record_ref"], [])))

    seller_share = None
    if match["holder"] is not None and match["tier"] not in ("NONE", "NOT_RUN"):
        seller_share = frac_text(match["holder"]["share"])

    issuing = verdict != "INTEGRITY_ALERT"
    cp_block = ledger.checkpoint
    if issuing:
        cp = checkpoint.sign_checkpoint(conn, plot["plot_id"], ts=clock.iso(now))
        cp_block = {k: cp[k] for k in ("height", "head_hash", "ts", "key_id", "signature_b64")}

    report = {
        "report_id": None, "short_code": None, "synthetic": True, "issued_at": clock.iso(now),
        "valid_until": None,
        "plot": {k: plot[k] for k in ("plot_id", "district_id", "upazila_id", "mouza_id", "jl_no", "survey",
                                      "khatian_no", "dag_no", "area_decimal", "land_class")},
        "seller": {"name": req["seller"]["name"], "father_or_husband": req["seller"].get("father_or_husband"),
                   "match": {"tier": match["tier"], "score": match["score"]}},
        "consents": {"bank": bool(req["consents"]["bank"])},
        "verdict": verdict, "coverage": coverage, "findings": findings,
        "sources": [sources[s].public() for s in ("land_records", "registry", "mutation", "court", "khas", "bank")],
        "holders_summary": {"holder_count": len(graph.current_holders), "seller_share": seller_share},
        "timeline": timeline, "not_checked": cov.not_checked(sources),
        "ledger": {"ok": ledger.ok, "broken_at_seq": ledger.broken_at_seq, "reason": ledger.reason,
                   "height": ledger.height, "head_hash": ledger.head_hash, "checkpoint": cp_block},
        "key_id": signer.KEY_ID, "signed_payload_b64": None, "signature_b64": None,
    }
    if not issuing:
        return report  # INTEGRITY_ALERT: nothing issued, nothing stored

    valid_until = now + timedelta(days=VALID_DAYS)
    report["valid_until"] = clock.iso(valid_until)
    _issue(conn, report, plot["plot_id"], verdict, findings, ledger, now)
    return report


def _issue(conn: sqlite3.Connection, report: dict, plot_id: str, verdict: str, findings: list[dict],
           ledger, now: datetime) -> None:
    """Pick a free report_id and short code, sign, and INSERT. report_id and short_code are PRIMARY KEY
    and UNIQUE: if a concurrent writer takes the same id first, the INSERT raises IntegrityError and
    we sign again with the next id. The id is inside the signed payload, so it cannot be patched after."""
    for attempt in range(MAX_ISSUE_ATTEMPTS):
        report["report_id"] = new_report_id(conn, now, skip=attempt)
        report["short_code"] = new_short_code(conn)
        payload = {"v": 1, "report_id": report["report_id"], "short_code": report["short_code"],
                   "plot_id": plot_id, "verdict": verdict, "issued_at": report["issued_at"],
                   "valid_until": report["valid_until"], "ledger_height": ledger.height,
                   "ledger_head": ledger.head_hash, "findings_hash": findings_hash(findings),
                   "key_id": signer.KEY_ID}
        raw = signer.canonical(payload)
        report["signed_payload_b64"] = signer.b64u(raw)
        report["signature_b64"] = signer.sign(raw)
        try:
            conn.execute("INSERT INTO reports VALUES (?,?,?,?,?)",
                         (report["report_id"], report["short_code"], plot_id,
                          json.dumps(report, ensure_ascii=False), report["issued_at"]))
        except sqlite3.IntegrityError:
            continue
        conn.commit()
        return
    raise AppError("INTERNAL", "could not allocate a unique report id")
