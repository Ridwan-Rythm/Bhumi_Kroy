"""Signed checkpoints: {plot_id, height, head_hash, ts, key_id} signed with Ed25519."""
from __future__ import annotations

import sqlite3

from app.core import clock
from app.ledger import chain, signer


def sign_checkpoint(conn: sqlite3.Connection, plot_id: str, ts: str | None = None) -> dict:
    height, head_hash = chain.head(conn, plot_id)
    cp = {"plot_id": plot_id, "height": height, "head_hash": head_hash,
          "ts": ts or clock.iso(clock.now()), "key_id": signer.KEY_ID}
    cp["signature_b64"] = signer.sign(chain.checkpoint_message(cp))
    conn.execute("INSERT INTO checkpoints VALUES (?,?,?,?,?,?)",
                 (plot_id, cp["height"], cp["head_hash"], cp["ts"], cp["key_id"], cp["signature_b64"]))
    return cp
