import asyncio
import json
from datetime import timedelta

from app.adapters import ALL_ADAPTERS, Ctx, fetch_all
from app.core import clock
from seed import load
from tests.helpers import make_db

STATUSES = {"OK", "NO_RECORD", "PARTIAL", "STALE", "UNAVAILABLE", "ERROR"}
MATURITY = {"M0", "M1", "M2", "M3", "M4"}
LINKAGE = {"EXACT", "TEXT_MATCH", "PARTY_NAME_ONLY", None}
REASONS = {"consent_required", "timeout", "outage", "stale", "not_digitised", None}


def run(conn, plot_id, **ctx_kw):
    return asyncio.run(fetch_all(plot_id, Ctx(conn, **ctx_kw), ALL_ADAPTERS))


def test_every_adapter_returns_contract_valid_fields():
    conn = make_db()
    for plot_id in ("P-001", "P-003", "P-009"):
        res = run(conn, plot_id)
        assert set(res) == {"land_records", "registry", "mutation", "court", "khas", "bank"}
        for r in res.values():
            d = r.public()
            assert d["status"] in STATUSES and d["maturity"] in MATURITY
            assert d["linkage"] in LINKAGE and d["reason"] in REASONS
            assert isinstance(d["latency_ms"], int) and d["record_count"] == len(r.records)


def test_default_setup_p001():
    res = run(make_db(), "P-001")
    assert {k: v.maturity for k, v in res.items()} == {
        "land_records": "M3", "registry": "M2", "mutation": "M3", "court": "M2", "khas": "M2", "bank": "M3"}
    assert res["court"].status == "NO_RECORD" and res["court"].linkage == "TEXT_MATCH"
    assert all(res[s].status == "OK" for s in ("land_records", "registry", "mutation", "khas", "bank"))


def test_timeout_path_gives_unavailable_timeout():
    conn = make_db()
    conn.execute("UPDATE plots SET adapter_config_json=? WHERE plot_id='P-001'",
                 (json.dumps({"registry": {"latency_ms": 2000}}),))
    res = run(conn, "P-001", timeout_s=0.5)
    assert res["registry"].status == "UNAVAILABLE" and res["registry"].reason == "timeout"
    assert res["registry"].records == [] and res["registry"].as_of is None
    assert res["land_records"].status == "OK"


def test_bank_consent_required_when_consent_false():
    res = run(make_db(), "P-003", consents={"bank": False})
    assert res["bank"].status == "UNAVAILABLE" and res["bank"].reason == "consent_required"
    assert res["bank"].records == []


def test_stale_when_as_of_older_than_30_days():
    conn = make_db()
    conn.execute("UPDATE plots SET adapter_config_json=? WHERE plot_id='P-001'",
                 (json.dumps({"khas": {"as_of_age_days": 45}}),))
    res = run(conn, "P-001")
    assert res["khas"].status == "STALE" and res["khas"].reason == "stale"
    assert res["khas"].as_of is not None


def test_clock_offset_makes_everything_fresh_again():
    # as_of is relative to "now", so fresh data stays fresh when the clock is shifted consistently
    conn = make_db()
    res = run(conn, "P-001", now=clock.now() + timedelta(days=60))
    assert res["land_records"].status == "OK"


def test_p009_court_party_name_only_and_bank_outage():
    res = run(make_db(), "P-009")
    assert res["court"].status == "NO_RECORD" and res["court"].linkage == "PARTY_NAME_ONLY"
    assert res["bank"].status == "UNAVAILABLE" and res["bank"].reason == "outage"


def test_court_case_returned_as_ok_with_linkage_on_record():
    res = run(make_db(), "P-004")
    assert res["court"].status == "OK" and res["court"].records[0]["linkage"] == "TEXT_MATCH"


def test_seed_is_deterministic():
    a, b = make_db(seed=7), make_db(seed=7)
    assert load.content_hash(a) == load.content_hash(b)
    assert load.content_hash(a) != load.content_hash(make_db(seed=8))
