"""Create tables and load the deterministic seed.  Run from backend/:  python -m seed.load"""
from __future__ import annotations

import hashlib
import sqlite3

from app.core import db
from app.ledger import chain, checkpoint, signer
from seed import build_golden

SEED_TS = "2026-10-01T00:00:00+06:00"


def load(conn: sqlite3.Connection, seed: int = 42, keep_reports: bool = True) -> None:
    db.init_db(conn)
    db.wipe_seeded(conn, keep_reports=keep_reports)
    data = build_golden.build_all(seed)
    for u in data["admin_units"]:
        conn.execute("INSERT INTO admin_units VALUES (?,?,?,?,?,?)",
                     (u["id"], u["kind"], u["parent_id"], u["name_bn"], u["name_en"], u["jl_no"]))
    for p in data["plots"]:
        load_plot(conn, p)
    conn.commit()


def load_plot(conn: sqlite3.Connection, p: dict) -> None:
    """Insert one plot dict (as produced by PlotBuilder.build) with its ledger and a signed checkpoint."""
    conn.execute("INSERT INTO plots VALUES (?,?,?,?,?,?,?,?)",
                 (p["plot_id"], p["mouza_id"], p["survey"], p["khatian_no"], p["dag_no"],
                  p["area_decimal"], p["land_class"], signer.canonical(p["adapter_config"]).decode()))
    for rec in sorted(p["records"], key=lambda r: (r["date"], r["record_id"])):
        chain.append_record(conn, p["plot_id"], rec, SEED_TS)
    checkpoint.sign_checkpoint(conn, p["plot_id"], ts=SEED_TS)


def load_extra(conn: sqlite3.Connection, name: str) -> dict:
    """Load seed/golden/extra_<name>.json (hand-written Tier-2 plots, NOT part of the ten samples)."""
    import json
    from pathlib import Path
    doc = json.loads((Path(__file__).parent / "golden" / f"extra_{name}.json").read_text(encoding="utf-8"))
    load_plot(conn, doc["plot"])
    conn.commit()
    return doc


def content_hash(conn: sqlite3.Connection) -> str:
    """Hash of all seeded content (checkpoint signatures excluded: they depend on the key)."""
    h = hashlib.sha256()
    queries = [
        "SELECT * FROM admin_units ORDER BY id", "SELECT * FROM plots ORDER BY plot_id",
        "SELECT * FROM records ORDER BY record_id", "SELECT * FROM ledger ORDER BY plot_id, seq",
        "SELECT plot_id, height, head_hash, ts, key_id FROM checkpoints ORDER BY plot_id, height",
    ]
    for q in queries:
        for row in conn.execute(q):
            h.update(signer.canonical(list(row)))
    return h.hexdigest()


def main() -> None:
    conn = db.connect()
    load(conn)
    n_plots = conn.execute("SELECT COUNT(*) FROM plots").fetchone()[0]
    n_rec = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    print(f"seeded {n_plots} plots, {n_rec} records into {db.db_path()} (content hash {content_hash(conn)[:16]})")


if __name__ == "__main__":
    main()
