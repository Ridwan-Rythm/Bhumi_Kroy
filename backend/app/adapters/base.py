"""One contract for every adapter (plan B7.1, contract SourceResult)."""
from __future__ import annotations

import asyncio
import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.core import clock

SOURCES = ("land_records", "registry", "mutation", "court", "khas", "bank")
MATURITY_ORDER = {"M0": 0, "M1": 1, "M2": 2, "M3": 3, "M4": 4}
STALE_DAYS = 30
TIMEOUT_S = 1.5

# Default setup per contract 8.1; latency is simulated (ms).
DEFAULTS = {
    "land_records": {"maturity": "M3", "linkage": None, "latency_ms": 120},
    "registry": {"maturity": "M2", "linkage": None, "latency_ms": 200},
    "mutation": {"maturity": "M3", "linkage": None, "latency_ms": 150},
    "court": {"maturity": "M2", "linkage": "TEXT_MATCH", "latency_ms": 250},
    "khas": {"maturity": "M2", "linkage": None, "latency_ms": 180},
    "bank": {"maturity": "M3", "linkage": None, "latency_ms": 220},
}
BASE_CFG = {"status": None, "reason": None, "as_of_age_days": 1}


@dataclass
class Ctx:
    conn: sqlite3.Connection
    consents: dict = field(default_factory=lambda: {"bank": True})
    now: datetime = field(default_factory=clock.now)
    timeout_s: float = TIMEOUT_S


@dataclass
class SourceResult:
    source: str
    status: str
    as_of: str | None
    maturity: str
    linkage: str | None
    latency_ms: int
    record_count: int
    reason: str | None
    records: list = field(default_factory=list)

    def public(self) -> dict:
        d = {k: getattr(self, k) for k in ("source", "status", "as_of", "maturity", "linkage",
                                           "latency_ms", "record_count", "reason")}
        return d


class BaseAdapter:
    source: str = ""

    def config(self, conn: sqlite3.Connection, plot_id: str) -> dict:
        row = conn.execute("SELECT adapter_config_json FROM plots WHERE plot_id=?", (plot_id,)).fetchone()
        overrides = json.loads(row["adapter_config_json"]).get(self.source, {}) if row else {}
        return {**BASE_CFG, **DEFAULTS[self.source], **overrides}

    def read_records(self, conn: sqlite3.Connection, plot_id: str) -> list[dict]:
        rows = conn.execute("SELECT data_json FROM records WHERE plot_id=? AND source=? ORDER BY record_id",
                            (plot_id, self.source)).fetchall()
        return [json.loads(r["data_json"]) for r in rows]

    def _unavailable(self, cfg: dict, reason: str, latency_ms: int) -> SourceResult:
        return SourceResult(self.source, "UNAVAILABLE", None, cfg["maturity"], cfg["linkage"],
                            latency_ms, 0, reason, [])

    async def fetch(self, plot_id: str, ctx: Ctx) -> SourceResult:
        cfg = self.config(ctx.conn, plot_id)
        if not self.consent_ok(ctx):
            return self._unavailable(cfg, "consent_required", 0)
        latency = int(cfg["latency_ms"])
        try:
            await asyncio.wait_for(asyncio.sleep(latency / 1000), timeout=ctx.timeout_s)
        except TimeoutError:
            return self._unavailable(cfg, "timeout", int(ctx.timeout_s * 1000))
        if cfg["status"] in ("UNAVAILABLE", "ERROR"):
            return SourceResult(self.source, cfg["status"], None, cfg["maturity"], cfg["linkage"], latency, 0,
                                cfg["reason"] or ("outage" if cfg["status"] == "UNAVAILABLE" else None), [])
        records = self.read_records(ctx.conn, plot_id)
        as_of_dt = ctx.now - timedelta(days=float(cfg["as_of_age_days"]))
        status = cfg["status"] or self.default_status(records)
        reason = cfg["reason"]
        if status in ("OK", "NO_RECORD") and ctx.now - as_of_dt > timedelta(days=STALE_DAYS):
            status, reason = "STALE", "stale"
        return SourceResult(self.source, status, clock.iso(as_of_dt), cfg["maturity"], cfg["linkage"],
                            latency, len(records), reason, records)

    def default_status(self, records: list[dict]) -> str:
        return "OK"

    def consent_ok(self, ctx: Ctx) -> bool:
        return True


async def fetch_all(plot_id: str, ctx: Ctx, adapters) -> dict[str, SourceResult]:
    results = await asyncio.gather(*(a.fetch(plot_id, ctx) for a in adapters))
    return {r.source: r for r in results}
