"""SQLite via stdlib sqlite3 (no ORM)."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "landcheck.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS admin_units (
  id TEXT PRIMARY KEY, kind TEXT NOT NULL, parent_id TEXT,
  name_bn TEXT NOT NULL, name_en TEXT NOT NULL, jl_no TEXT);
CREATE TABLE IF NOT EXISTS plots (
  plot_id TEXT PRIMARY KEY, mouza_id TEXT NOT NULL, survey TEXT, khatian_no TEXT NOT NULL,
  dag_no TEXT NOT NULL, area_decimal REAL, land_class TEXT, adapter_config_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS records (
  record_id TEXT PRIMARY KEY, plot_id TEXT NOT NULL, source TEXT NOT NULL, type TEXT NOT NULL,
  data_json TEXT NOT NULL, record_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS ledger (
  plot_id TEXT NOT NULL, seq INTEGER NOT NULL, ts TEXT NOT NULL, source TEXT NOT NULL,
  record_id TEXT NOT NULL, record_hash TEXT NOT NULL, prev_hash TEXT NOT NULL,
  entry_hash TEXT NOT NULL, PRIMARY KEY (plot_id, seq));
CREATE TABLE IF NOT EXISTS checkpoints (
  plot_id TEXT NOT NULL, height INTEGER NOT NULL, head_hash TEXT NOT NULL, ts TEXT NOT NULL,
  key_id TEXT NOT NULL, signature_b64 TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS reports (
  report_id TEXT PRIMARY KEY, short_code TEXT UNIQUE NOT NULL, plot_id TEXT NOT NULL,
  json TEXT NOT NULL, issued_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_records_plot ON records(plot_id);
CREATE INDEX IF NOT EXISTS idx_ckpt_plot ON checkpoints(plot_id, height);
"""

SEEDED_TABLES = ("admin_units", "plots", "records", "ledger", "checkpoints")


def db_path() -> str:
    return os.environ.get("DB_PATH") or str(DEFAULT_DB)


def connect(path: str | None = None) -> sqlite3.Connection:
    path = path or db_path()
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    # timeout: wait (instead of failing) while another request holds the write lock.
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    if path != ":memory:":
        conn.execute("PRAGMA journal_mode=WAL")  # readers do not block the writer
    init_db(conn)
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def wipe_seeded(conn: sqlite3.Connection, keep_reports: bool = True) -> None:
    for t in SEEDED_TABLES:
        conn.execute(f"DELETE FROM {t}")
    if not keep_reports:
        conn.execute("DELETE FROM reports")
    conn.commit()
