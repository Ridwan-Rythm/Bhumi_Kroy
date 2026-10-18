"""Verification pipeline (plan B8.1): normalise -> fan out -> ledger -> graph -> rules -> verdict -> report."""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime

from app.adapters import ALL_ADAPTERS, Ctx, fetch_all
from app.core import clock
from app.core.errors import AppError
from app.core.normalize import clean_text, normalize_number_string
from app.engine import coverage as cov
from app.engine import report_builder, seller_match
from app.engine import verdict as verdict_mod
from app.engine.rules import RuleContext, run_rules
from app.engine.title_graph import TitleGraph
from app.ledger import chain

SURVEYS = {"CS", "SA", "RS", "BS"}
NUM_RE = re.compile(r"^\d+([/-]\d+)?$")
MAX_TEXT = 120


def _req_str(d: dict, key: str, field: str) -> str:
    v = d.get(key)
    if not isinstance(v, str) or not v.strip():
        raise AppError("VALIDATION_ERROR", f"{field} is required", field)
    return v


def normalize_request(req: dict) -> dict:
    if not isinstance(req, dict) or not isinstance(req.get("plot"), dict) or not isinstance(req.get("seller"), dict):
        raise AppError("VALIDATION_ERROR", "plot and seller are required", "plot")
    p, s = req["plot"], req["seller"]
    out_plot = {k: clean_text(_req_str(p, k, f"plot.{k}")) for k in ("district_id", "upazila_id", "mouza_id")}
    for k in ("khatian_no", "dag_no"):
        v = normalize_number_string(_req_str(p, k, f"plot.{k}"))
        if not NUM_RE.match(v) or len(v) > 20:
            raise AppError("VALIDATION_ERROR", f"plot.{k} must be a number", f"plot.{k}")
        out_plot[k] = v
    survey = p.get("survey")
    if survey is not None and (not isinstance(survey, str) or survey not in SURVEYS):
        raise AppError("VALIDATION_ERROR", "plot.survey must be CS, SA, RS or BS", "plot.survey")
    out_plot["survey"] = survey
    name = clean_text(_req_str(s, "name", "seller.name"))
    father = s.get("father_or_husband")
    if father is not None and not isinstance(father, str):
        # A wrong type is an error, not "no father given": silently dropping it would weaken the match.
        raise AppError("VALIDATION_ERROR", "seller.father_or_husband must be text", "seller.father_or_husband")
    father = clean_text(father) if father is not None and clean_text(father) else None
    if len(name) > MAX_TEXT:
        raise AppError("VALIDATION_ERROR", "name is too long", "seller.name")
    if father and len(father) > MAX_TEXT:
        raise AppError("VALIDATION_ERROR", "name is too long", "seller.father_or_husband")
    consents = req.get("consents")
    if consents is None:
        consents = {}
    if not isinstance(consents, dict):
        raise AppError("VALIDATION_ERROR", "consents must be an object like {\"bank\": true}", "consents")
    bank = consents.get("bank", True)
    if not isinstance(bank, bool):
        raise AppError("VALIDATION_ERROR", "consents.bank must be true or false", "consents.bank")
    return {"plot": out_plot, "seller": {"name": name, "father_or_husband": father}, "consents": {"bank": bank}}


def resolve_plot(conn: sqlite3.Connection, req: dict) -> dict:
    p = req["plot"]
    m = conn.execute("SELECT * FROM admin_units WHERE id=? AND kind='mouza'", (p["mouza_id"],)).fetchone()
    up = conn.execute("SELECT * FROM admin_units WHERE id=?", (m["parent_id"],)).fetchone() if m else None
    if not m or not up or up["id"] != p["upazila_id"] or up["parent_id"] != p["district_id"]:
        raise AppError("NOT_FOUND", "No such location", "plot.mouza_id")
    sql = "SELECT * FROM plots WHERE mouza_id=? AND khatian_no=? AND dag_no=?"
    args = [p["mouza_id"], p["khatian_no"], p["dag_no"]]
    if p["survey"]:
        sql, args = sql + " AND survey=?", args + [p["survey"]]
    row = conn.execute(sql, args).fetchone()
    if not row:
        raise AppError("NOT_FOUND", "No plot with these identifiers", "plot")
    return {"plot_id": row["plot_id"], "district_id": p["district_id"], "upazila_id": p["upazila_id"],
            "mouza_id": row["mouza_id"], "jl_no": m["jl_no"], "survey": row["survey"],
            "khatian_no": row["khatian_no"], "dag_no": row["dag_no"], "area_decimal": row["area_decimal"],
            "land_class": row["land_class"]}


async def run_check(conn: sqlite3.Connection, raw_req: dict, now: datetime | None = None,
                    timeout_s: float = 1.5) -> dict:
    req = normalize_request(raw_req)
    plot = resolve_plot(conn, req)
    now = now or clock.now()
    sources = await fetch_all(plot["plot_id"], Ctx(conn, req["consents"], now, timeout_s), ALL_ADAPTERS)
    ledger = chain.verify(conn, plot["plot_id"])
    graph = TitleGraph([r for s in sources.values() for r in s.records])
    match = seller_match.best_match(req["seller"]["name"], req["seller"]["father_or_husband"],
                                    graph.current_holders)
    findings = run_rules(RuleContext(plot, req["seller"], sources, ledger, graph, match))
    coverage = cov.compute(sources, ledger.ok)
    verdict = verdict_mod.compute(findings, coverage)
    return report_builder.build(conn, plot, req, sources, ledger, graph, match, findings, coverage, verdict, now)
