"""Demo console logic (DEMO_MODE only): tamper, add-event, reset, ledger view, clock."""
from __future__ import annotations

import json
import os
import re
import sqlite3
from datetime import datetime

from app.core import clock
from app.core.errors import AppError
from app.ledger import chain, checkpoint, signer

IMPLEMENTED = ("edit_field", "edit_and_rehash", "delete_entry", "swap_signature", "reorder")
NOT_IMPLEMENTED = ("replace_entry", "replay_checkpoint")
BANK = "পদ্মা পল্লী ঋণ ব্যাংক"
APPLICANT = {"name": "নূরুল আমিন সরকার", "father": "মৃত আজিজ মিয়া"}


def require_demo() -> None:
    if os.environ.get("DEMO_MODE") != "1":
        raise AppError("DEMO_DISABLED", "Demo endpoints are disabled", None)


def _need_plot(conn, plot_id: str) -> None:
    if not conn.execute("SELECT 1 FROM plots WHERE plot_id=?", (plot_id,)).fetchone():
        raise AppError("NOT_FOUND", "No such plot", "plot_id")


# --- ledger view ---------------------------------------------------------------------------------
def ledger_view(conn: sqlite3.Connection, plot_id: str) -> dict:
    require_demo()
    _need_plot(conn, plot_id)
    st = chain.verify(conn, plot_id)
    entries = []
    for e in chain.entries(conn, plot_id):
        entries.append({"seq": e["seq"], "ts": e["ts"], "source": e["source"], "record_id": e["record_id"],
                        "record_hash": e["record_hash"], "prev_hash": e["prev_hash"],
                        "entry_hash": e["entry_hash"],
                        "status": "broken" if st.broken_at_seq == e["seq"] else "ok"})
    cp = chain.latest_checkpoint(conn, plot_id)
    cp_out = None
    if cp:
        valid = (signer.verify(chain.checkpoint_message(cp), cp["signature_b64"])
                 and cp["height"] == st.height and cp["head_hash"] == st.head_hash)
        cp_out = {k: cp[k] for k in ("height", "head_hash", "ts", "key_id", "signature_b64")} | {"valid": valid}
    return {"plot_id": plot_id, "ok": st.ok, "broken_at_seq": st.broken_at_seq, "reason": st.reason,
            "entries": entries, "checkpoint": cp_out}


# --- tamper --------------------------------------------------------------------------------------
def _edit_target(conn, plot_id: str) -> dict:
    """The newest land-records entry: edit its area (the current khatian)."""
    row = conn.execute("SELECT * FROM ledger WHERE plot_id=? AND source='land_records' ORDER BY seq DESC LIMIT 1",
                       (plot_id,)).fetchone()
    return dict(row)


def _edit_record(conn, record_id: str) -> None:
    row = conn.execute("SELECT data_json FROM records WHERE record_id=?", (record_id,)).fetchone()
    data = json.loads(row["data_json"])
    data["area_decimal"] = round(float(data.get("area_decimal") or 0) + 5.0, 2)
    conn.execute("UPDATE records SET data_json=? WHERE record_id=?",
                 (signer.canonical(data).decode("utf-8"), record_id))


def _rehash_from(conn, plot_id: str, start_seq: int) -> None:
    rows = chain.entries(conn, plot_id)
    prev = chain.GENESIS if start_seq <= 1 else rows[start_seq - 2]["entry_hash"]
    for e in rows:
        if e["seq"] < start_seq:
            continue
        data = json.loads(conn.execute("SELECT data_json FROM records WHERE record_id=?",
                                       (e["record_id"],)).fetchone()["data_json"])
        row = dict(e)
        row["record_hash"], row["prev_hash"] = chain.record_hash(data), prev
        row["entry_hash"] = chain.entry_hash(row)
        conn.execute("UPDATE records SET record_hash=? WHERE record_id=?", (row["record_hash"], e["record_id"]))
        conn.execute("UPDATE ledger SET record_hash=?, prev_hash=?, entry_hash=? WHERE plot_id=? AND seq=?",
                     (row["record_hash"], row["prev_hash"], row["entry_hash"], plot_id, e["seq"]))
        prev = row["entry_hash"]


def tamper(conn: sqlite3.Connection, plot_id: str, kind: str) -> dict:
    """Mutate stored data BEHIND the ledger's back. edit_and_rehash recomputes the chain but cannot re-sign."""
    require_demo()
    _need_plot(conn, plot_id)
    if kind in NOT_IMPLEMENTED:
        raise AppError("NOT_IMPLEMENTED", f"tamper kind '{kind}' is not implemented", "kind")
    if kind not in IMPLEMENTED:
        raise AppError("VALIDATION_ERROR", f"unknown tamper kind '{kind}'", "kind")
    height = chain.head(conn, plot_id)[0]
    if kind == "edit_field":
        _edit_record(conn, _edit_target(conn, plot_id)["record_id"])
    elif kind == "edit_and_rehash":
        t = _edit_target(conn, plot_id)
        _edit_record(conn, t["record_id"])
        _rehash_from(conn, plot_id, t["seq"])
    elif kind == "delete_entry":
        conn.execute("DELETE FROM ledger WHERE plot_id=? AND seq=?", (plot_id, 2 if height >= 3 else 1))
    elif kind == "swap_signature":
        other = conn.execute("SELECT signature_b64 FROM checkpoints WHERE plot_id<>? ORDER BY rowid DESC LIMIT 1",
                             (plot_id,)).fetchone()
        sig = other["signature_b64"] if other else signer.sign(b"swapped")
        latest = chain.latest_checkpoint(conn, plot_id)
        conn.execute("UPDATE checkpoints SET signature_b64=? WHERE plot_id=? AND height=? AND ts=?",
                     (sig, plot_id, latest["height"], latest["ts"]))
    elif kind == "reorder":
        if height < 3:
            raise AppError("NOT_IMPLEMENTED", "plot has too few entries to reorder", "kind")
        rows = {e["seq"]: e for e in chain.entries(conn, plot_id)}
        cols = ("ts", "source", "record_id", "record_hash", "prev_hash", "entry_hash")
        for a, b in ((2, 3), (3, 2)):
            conn.execute(f"UPDATE ledger SET {','.join(c + '=?' for c in cols)} WHERE plot_id=? AND seq=?",
                         (*[rows[a][c] for c in cols], plot_id, b))
    conn.commit()
    return ledger_view(conn, plot_id)


# --- add-event -----------------------------------------------------------------------------------
def _next_id(conn, prefix: str) -> str:
    best = 0
    for r in conn.execute("SELECT record_id FROM records WHERE record_id LIKE ?", (prefix + "-%",)):
        m = re.match(rf"{prefix}-(\d+)$", r["record_id"])
        best = max(best, int(m.group(1)) if m else 0)
    return f"{prefix}-{best + 1:04d}"


def add_event(conn: sqlite3.Connection, plot_id: str, kind: str, now: datetime | None = None) -> dict:
    """Legitimately append a record, a ledger entry and a NEW signed checkpoint."""
    require_demo()
    _need_plot(conn, plot_id)
    now = now or clock.now()
    if not chain.verify(conn, plot_id).ok:
        # Never sign a checkpoint over a chain that fails verification: that would launder the tamper.
        raise AppError("VALIDATION_ERROR", "ledger for this plot is not intact; reset first", "plot_id")
    date = now.date().isoformat()
    if kind == "new_mortgage":
        holder = _current_holder(conn, plot_id)
        rec = {"record_id": _next_id(conn, "BNK"), "source": "bank", "type": "MORTGAGE", "date": date,
               "mortgagor": holder, "bank_name": BANK, "amount_bdt": 1500000, "status": "ACTIVE"}
    elif kind == "new_mutation_pending":
        rid = _next_id(conn, "MUT")
        rec = {"record_id": rid, "source": "mutation", "type": "MUTATION_PENDING", "date": date,
               "applicant": APPLICANT, "case_no": "M-" + rid[4:]}
    else:
        raise AppError("VALIDATION_ERROR", f"unknown event kind '{kind}'", "kind")
    chain.append_record(conn, plot_id, rec, clock.iso(now))
    checkpoint.sign_checkpoint(conn, plot_id, ts=clock.iso(now))
    conn.commit()
    return {"ok": True, "added": {"record_ref": rec["record_id"], "kind": rec["type"], "date": date}}


def _current_holder(conn, plot_id: str) -> dict:
    row = conn.execute("SELECT data_json FROM records WHERE plot_id=? AND type='SURVEY_ENTRY' "
                       "ORDER BY json_extract(data_json,'$.date') DESC LIMIT 1", (plot_id,)).fetchone()
    h = json.loads(row["data_json"])["holders"][0]
    return {"name": h["name"], "father": h["father"]}


# --- reset / clock -------------------------------------------------------------------------------
def reset(conn: sqlite3.Connection, seed: int = 42) -> dict:
    """Rebuild plots, records, ledger and checkpoints from the seed; KEEP the reports table."""
    require_demo()
    from seed import load
    load.load(conn, seed=seed, keep_reports=True)
    clock.set_offset_days(0)
    return {"ok": True}


def set_clock(offset_days: int) -> dict:
    require_demo()
    if not isinstance(offset_days, int) or isinstance(offset_days, bool) or abs(offset_days) > 3650:
        raise AppError("VALIDATION_ERROR", "offset_days must be an integer", "offset_days")
    clock.set_offset_days(offset_days)
    return {"ok": True, "now": clock.iso(clock.now())}
