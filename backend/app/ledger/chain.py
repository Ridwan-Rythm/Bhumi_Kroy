"""Per-plot hash chain (contract section 7, plan B4.3).

Entry fields hashed into entry_hash: {plot_id, seq, ts, source, record_id, record_hash, prev_hash}.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass

from app.ledger import signer

GENESIS = "sha256:" + "0" * 64


def sha256_hex(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def record_hash(data: dict) -> str:
    return sha256_hex(signer.canonical(data))


def entry_fields(e) -> dict:
    return {k: e[k] for k in ("plot_id", "seq", "ts", "source", "record_id", "record_hash", "prev_hash")}


def entry_hash(e) -> str:
    return sha256_hex(signer.canonical(entry_fields(e)))


@dataclass
class LedgerStatus:
    ok: bool
    broken_at_seq: int | None
    reason: str | None
    height: int
    head_hash: str
    checkpoint: dict | None = None


def entries(conn: sqlite3.Connection, plot_id: str) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM ledger WHERE plot_id=? ORDER BY seq", (plot_id,)).fetchall()


def head(conn: sqlite3.Connection, plot_id: str) -> tuple[int, str]:
    row = conn.execute("SELECT seq, entry_hash FROM ledger WHERE plot_id=? ORDER BY seq DESC LIMIT 1",
                       (plot_id,)).fetchone()
    return (row["seq"], row["entry_hash"]) if row else (0, GENESIS)


def append(conn: sqlite3.Connection, plot_id: str, source: str, record_id: str,
           record_data: dict, ts: str) -> dict:
    """Append one entry (does not touch the records table; see append_record)."""
    height, prev = head(conn, plot_id)
    e = {"plot_id": plot_id, "seq": height + 1, "ts": ts, "source": source, "record_id": record_id,
         "record_hash": record_hash(record_data), "prev_hash": prev}
    e["entry_hash"] = entry_hash(e)
    conn.execute("INSERT INTO ledger VALUES (?,?,?,?,?,?,?,?)",
                 (e["plot_id"], e["seq"], e["ts"], e["source"], e["record_id"], e["record_hash"],
                  e["prev_hash"], e["entry_hash"]))
    return e


def append_record(conn: sqlite3.Connection, plot_id: str, record: dict, ts: str) -> dict:
    """Insert a record row and its ledger entry. record must carry record_id, source, type."""
    rh = record_hash(record)
    conn.execute("INSERT INTO records VALUES (?,?,?,?,?,?)",
                 (record["record_id"], plot_id, record["source"], record["type"],
                  signer.canonical(record).decode("utf-8"), rh))
    return append(conn, plot_id, record["source"], record["record_id"], record, ts)


def latest_checkpoint(conn: sqlite3.Connection, plot_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM checkpoints WHERE plot_id=? ORDER BY height DESC, rowid DESC LIMIT 1",
                       (plot_id,)).fetchone()
    return dict(row) if row else None


def checkpoint_message(cp: dict) -> bytes:
    return signer.canonical({k: cp[k] for k in ("plot_id", "height", "head_hash", "ts", "key_id")})


def verify(conn: sqlite3.Connection, plot_id: str) -> LedgerStatus:
    rows = entries(conn, plot_id)
    height, head_hash = (rows[-1]["seq"], rows[-1]["entry_hash"]) if rows else (0, GENESIS)
    cp = latest_checkpoint(conn, plot_id)
    cp_public = _public_cp(cp)

    def fail(seq, reason):
        return LedgerStatus(False, seq, reason, height, head_hash, cp_public)

    prev = GENESIS
    for idx, e in enumerate(rows):
        if e["seq"] != idx + 1:
            return fail(e["seq"], "link_broken")
        rec = conn.execute("SELECT data_json FROM records WHERE record_id=? AND plot_id=?",
                           (e["record_id"], plot_id)).fetchone()
        if rec is None or record_hash(json.loads(rec["data_json"])) != e["record_hash"]:
            return fail(e["seq"], "hash_mismatch")
        if e["prev_hash"] != prev:
            return fail(e["seq"], "link_broken")
        if entry_hash(e) != e["entry_hash"]:
            return fail(e["seq"], "hash_mismatch")
        prev = e["entry_hash"]

    if cp is None:
        return fail(None, "checkpoint_mismatch")
    if not signer.verify(checkpoint_message(cp), cp["signature_b64"]):
        return fail(None, "signature_invalid")
    if cp["height"] != height:
        return fail(None, "height_mismatch")
    if cp["head_hash"] != head_hash:
        return fail(None, "checkpoint_mismatch")
    return LedgerStatus(True, None, None, height, head_hash, cp_public)


def _public_cp(cp: dict | None) -> dict | None:
    if cp is None:
        return None
    return {k: cp[k] for k in ("height", "head_hash", "ts", "key_id", "signature_b64")}
