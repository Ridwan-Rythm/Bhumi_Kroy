"""Property: whatever the sources do, a GREEN verdict never coexists with an uncovered question."""
import asyncio
import json
import random
from pathlib import Path

from app.adapters.base import DEFAULTS, SOURCES, SourceResult
from app.engine import coverage, verdict
from app.engine.pipeline import run_check
from tests.helpers import make_db

STATUSES = ["OK", "NO_RECORD", "PARTIAL", "STALE", "UNAVAILABLE", "ERROR"]
SAMPLE = json.loads(Path("seed/golden/samples.json").read_text(encoding="utf-8"))[0]["request"]


def random_sources(rng):
    out = {}
    for s in SOURCES:
        out[s] = SourceResult(s, rng.choice(STATUSES), None, rng.choice(["M0", "M1", "M2", "M3", "M4"]),
                              rng.choice([None, "EXACT", "TEXT_MATCH", "PARTY_NAME_ONLY"]), 0, 0, None, [])
    return out


def test_pure_functions_never_green_with_a_gap_and_always_green_when_fully_covered():
    rng = random.Random(2026)
    greens = 0
    for _ in range(2000):
        src = random_sources(rng)
        if rng.random() < 0.4:  # push towards the interesting region: many covered sources
            for s in src.values():
                s.status, s.linkage = "OK", None
        ledger_ok = rng.random() < 0.9
        findings = [{"severity": rng.choice(["INFO", "COVERAGE"])} for _ in range(rng.randint(0, 3))]
        cov = coverage.compute(src, ledger_ok)
        v = verdict.compute(findings, cov)
        all_covered = all(x == "COVERED" for x in cov.values())
        assert (v == "GREEN") == all_covered, (v, cov)
        greens += v == "GREEN"
    assert greens > 100  # the property was exercised on both sides


def test_pipeline_never_green_with_uncovered_questions_over_random_adapter_configs():
    rng = random.Random(7)
    conn = make_db()
    seen = set()
    for _ in range(40):
        cfg = {}
        for s in SOURCES:
            c = {"latency_ms": 0}
            if rng.random() < 0.3:
                c["status"] = rng.choice(["UNAVAILABLE", "ERROR", "PARTIAL", "NO_RECORD"])
            if rng.random() < 0.2:
                c["as_of_age_days"] = rng.choice([5, 29, 45, 90])
            if rng.random() < 0.2:
                c["maturity"] = rng.choice(["M0", "M1", "M2"])
            if s == "court" and rng.random() < 0.3:
                c["linkage"] = "PARTY_NAME_ONLY"
            cfg[s] = c
        conn.execute("UPDATE plots SET adapter_config_json=? WHERE plot_id='P-001'", (json.dumps(cfg),))
        r = asyncio.run(run_check(conn, SAMPLE))
        seen.add(r["verdict"])
        if r["verdict"] == "GREEN":
            assert all(v == "COVERED" for v in r["coverage"].values()), (cfg, r["coverage"])
        else:
            assert r["verdict"] in ("GREY", "AMBER", "RED")
    assert "GREY" in seen


def test_defaults_table_matches_contract_maturities():
    assert {k: v["maturity"] for k, v in DEFAULTS.items()} == {
        "land_records": "M3", "registry": "M2", "mutation": "M3", "court": "M2", "khas": "M2", "bank": "M3"}
