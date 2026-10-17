"""Build a RuleContext by hand from minimal records (no DB)."""
from __future__ import annotations

from app import namematch
from app.adapters.base import DEFAULTS, SOURCES, SourceResult
from app.engine import seller_match
from app.engine.rules import RuleContext, run_rules
from app.engine.title_graph import TitleGraph
from app.ledger.chain import LedgerStatus

A = {"name": "আলম মিয়া", "father": "মৃত করিম মিয়া"}
B = {"name": "জসিম উদ্দিন", "father": "মৃত হাশেম উদ্দিন"}
C = {"name": "সালাম খান", "father": "মৃত বশির খান"}


def survey(rid, date, sv, holders, area=33.0, cls="ধান"):
    return {"record_id": rid, "source": "land_records", "type": "SURVEY_ENTRY", "date": date, "survey": sv,
            "holders": [{**p, "share": s} for p, s in holders], "area_decimal": area, "land_class": cls}


def deed(rid, date, frm, to, share="1", mutated_on=None, rtype="SALE"):
    return {"record_id": rid, "source": "registry", "type": rtype, "date": date, "from": frm, "to": to,
            "share": share, "area_decimal": None, "mutated_on": mutated_on, "deed_no": "D"}


def src(name, records=(), status="OK", linkage="__default__", reason=None):
    d = DEFAULTS[name]
    return SourceResult(name, status, None if status in ("UNAVAILABLE", "ERROR") else "2026-10-16T00:00:00+06:00",
                        d["maturity"], d["linkage"] if linkage == "__default__" else linkage, 0,
                        len(records), reason, list(records))


def make_ctx(records=None, seller=None, overrides=None, ledger=None, holders_from=None):
    """records: {source: [records]}; overrides: {source: SourceResult}."""
    records = records or {}
    sources = {s: src(s, records.get(s, [])) for s in SOURCES}
    sources.update(overrides or {})
    all_recs = [r for s in sources.values() for r in s.records]
    graph = TitleGraph(all_recs)
    seller = seller or {"name": C["name"], "father_or_husband": C["father"]}
    match = seller_match.best_match(seller["name"], seller["father_or_husband"], graph.current_holders)
    ledger = ledger or LedgerStatus(True, None, None, 3, "sha256:" + "0" * 64, None)
    return RuleContext({"plot_id": "T"}, seller, sources, ledger, graph, match)


def findings(ctx, rule_id=None):
    out = run_rules(ctx)
    return [f for f in out if rule_id is None or f["rule_id"] == rule_id]


class fake_matcher:
    """Context manager replacing namematch.match_name (to exercise tiers the stub cannot produce)."""

    def __init__(self, fn):
        self.fn = fn

    def __enter__(self):
        self.old = namematch.match_name
        namematch.match_name = self.fn

    def __exit__(self, *exc):
        namematch.match_name = self.old


def tier(t, score=0.9):
    return lambda *a: {"tier": t, "score": score, "name_score": score, "father_score": None}


CLEAN_LAND = {"land_records": [survey("LND-1", "2018-01-01", "BS", [(C, "1")])]}
