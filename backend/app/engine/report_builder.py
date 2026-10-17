"""Fill every Report field (contract section 6), sign it and store it."""
from __future__ import annotations

import json
import secrets
import sqlite3
from datetime import datetime, timedelta

from app.core import clock
from app.engine import coverage as cov
from app.engine.title_graph import frac_text
from app.ledger import chain, checkpoint, signer

SHORT_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
VALID_DAYS = 7


def normalize_short_code(code: str) -> str:
    return "".join(ch for ch in code.upper() if ch in SHORT_ALPHABET)


def new_short_code(conn: sqlite3.Connection) -> str:
    while True:
        raw = "".join(secrets.choice(SHORT_ALPHABET) for _ in range(8))
        code = f"{raw[:4]}-{raw[4:]}"
        if not conn.execute("SELECT 1 FROM reports WHERE short_code=?", (code,)).fetchone():
            return code


def new_report_id(conn: sqlite3.Connection, now: datetime) -> str:
    n = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0] + 1
    while True:
        rid = f"RPT-{now.year}-{n:06d}"
        if not conn.execute("SELECT 1 FROM reports WHERE report_id=?", (rid,)).fetchone():
            return rid
        n += 1


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
    report["report_id"] = new_report_id(conn, now)
    report["short_code"] = new_short_code(conn)
    report["valid_until"] = clock.iso(valid_until)
    payload = {"v": 1, "report_id": report["report_id"], "short_code": report["short_code"],
               "plot_id": plot["plot_id"], "verdict": verdict, "issued_at": report["issued_at"],
               "valid_until": report["valid_until"], "ledger_height": ledger.height,
               "ledger_head": ledger.head_hash, "findings_hash": findings_hash(findings), "key_id": signer.KEY_ID}
    raw = signer.canonical(payload)
    report["signed_payload_b64"] = signer.b64u(raw)
    report["signature_b64"] = signer.sign(raw)
    conn.execute("INSERT INTO reports VALUES (?,?,?,?,?)",
                 (report["report_id"], report["short_code"], plot["plot_id"],
                  json.dumps(report, ensure_ascii=False), report["issued_at"]))
    conn.commit()
    return report
