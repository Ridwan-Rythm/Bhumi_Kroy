"""Tier-2 rules: hand-built contexts plus the five extra plots (seed/golden/extra_*.json)."""
import asyncio
import json

from app.engine.pipeline import run_check
from seed import load
from tests.helpers import make_db
from tests.rule_helpers import A, B, C, deed, findings, make_ctx, survey

NO_RULES = {"R-OWN-03", "R-CHAIN-01", "R-CHAIN-02", "R-RES-03", "R-INT-04"}


# --- R-OWN-03 ----------------------------------------------------------------------------------
def test_own_03_fires_when_seller_conveys_more_than_held():
    recs = {"land_records": [survey("L1", "1993-01-01", "RS", [(A, "1/2"), (B, "1/2")]),
                             survey("L2", "2018-01-01", "BS", [(C, "1")])],
            "registry": [deed("R1", "2010-01-01", A, C, "1")]}
    f = findings(make_ctx(recs), "R-OWN-03")
    assert len(f) == 1 and f[0]["severity"] == "CRITICAL" and f[0]["evidence"] == ["R1"]
    assert f[0]["params"] == {"seller_share": "1/2", "selling_share": "1"}


def test_own_03_does_not_fire_when_seller_held_enough():
    recs = {"land_records": [survey("L1", "1993-01-01", "RS", [(A, "1")]), survey("L2", "2018-01-01", "BS", [(C, "1")])],
            "registry": [deed("R1", "2010-01-01", A, C, "1")]}
    assert findings(make_ctx(recs), "R-OWN-03") == []


def test_own_03_edge_double_sale_deeds_are_not_reported_twice():
    recs = {"land_records": [survey("L1", "2018-01-01", "BS", [(A, "1")])],
            "registry": [deed("R1", "2024-02-10", A, B), deed("R2", "2024-03-05", A, C)]}
    ctx = make_ctx(recs)
    assert len(findings(ctx, "R-SALE-01")) == 1 and findings(ctx, "R-OWN-03") == []


# --- R-CHAIN-01 --------------------------------------------------------------------------------
def test_chain_01_fires_on_unexplained_generation():
    recs = {"land_records": [survey("L1", "1993-01-01", "RS", [(A, "1")]), survey("L2", "2018-01-01", "BS", [(C, "1")])]}
    f = findings(make_ctx(recs), "R-CHAIN-01")
    assert len(f) == 1 and f[0]["severity"] == "HIGH" and f[0]["evidence"] == ["L2"]


def test_chain_01_does_not_fire_when_a_deed_explains_it():
    recs = {"land_records": [survey("L1", "1993-01-01", "RS", [(A, "1")]), survey("L2", "2018-01-01", "BS", [(C, "1")])],
            "registry": [deed("R1", "2010-01-01", A, C)]}
    assert findings(make_ctx(recs), "R-CHAIN-01") == []


def test_chain_01_edge_single_survey_has_no_previous_generation():
    assert findings(make_ctx({"land_records": [survey("L1", "2018-01-01", "BS", [(C, "1")])]}), "R-CHAIN-01") == []


# --- R-CHAIN-02 --------------------------------------------------------------------------------
def test_chain_02_fires_when_shares_do_not_sum_to_one():
    f = findings(make_ctx({"land_records": [survey("L1", "2018-01-01", "BS", [(C, "1/2"), (A, "1/4")])]}), "R-CHAIN-02")
    assert len(f) == 1 and f[0]["params"] == {"share_sum": 0.75}


def test_chain_02_does_not_fire_on_exact_fractions_summing_to_one():
    land = {"land_records": [survey("L1", "2018-01-01", "BS", [(C, "1/3"), (A, "1/3"), (B, "1/3")])]}
    assert findings(make_ctx(land), "R-CHAIN-02") == []  # Fraction arithmetic: no float drift


def test_chain_02_edge_over_one_also_fires():
    land = {"land_records": [survey("L1", "2018-01-01", "BS", [(C, "1"), (A, "1/4")])]}
    assert findings(make_ctx(land), "R-CHAIN-02")[0]["params"]["share_sum"] == 1.25


# --- R-RES-03 ----------------------------------------------------------------------------------
def acq(rid="KHS-1"):
    return {"record_id": rid, "source": "khas", "type": "ACQUISITION", "date": "2025-04-01", "list": None}


def test_res_03_fires_on_acquisition():
    f = findings(make_ctx({"khas": [acq()]}), "R-RES-03")
    assert len(f) == 1 and f[0]["severity"] == "CRITICAL" and f[0]["params"] == {"record_ref": "KHS-1"}


def test_res_03_does_not_fire_without_acquisition():
    assert findings(make_ctx({}), "R-RES-03") == []


def test_res_03_edge_khas_record_is_res_01_only():
    ctx = make_ctx({"khas": [{**acq(), "type": "KHAS"}]})
    assert findings(ctx, "R-RES-03") == [] and len(findings(ctx, "R-RES-01")) == 1


# --- R-INT-04 ----------------------------------------------------------------------------------
BS = survey("L1", "2018-01-01", "BS", [(C, "1")])


def test_int_04_fires_on_unreflected_sale_without_notice():
    f = findings(make_ctx({"land_records": [BS], "registry": [deed("R1", "2025-06-10", C, A)]}), "R-INT-04")
    assert len(f) == 1 and f[0]["severity"] == "HIGH" and f[0]["evidence"] == ["R1", "L1"]
    assert f[0]["params"] == {"source_a": "registry", "source_b": "land_records"}


def test_int_04_does_not_fire_when_lt_notice_exists_or_deed_is_older():
    lt = {"record_id": "R2", "source": "registry", "type": "LT_NOTICE", "date": "2025-06-12", "sale_ref": "R1"}
    assert findings(make_ctx({"land_records": [BS], "registry": [deed("R1", "2025-06-10", C, A), lt]}), "R-INT-04") == []
    assert findings(make_ctx({"land_records": [BS], "registry": [deed("R1", "2010-06-10", B, C)]}), "R-INT-04") == []


def test_int_04_edge_buyer_already_shown_as_holder_is_consistent():
    assert findings(make_ctx({"land_records": [BS], "registry": [deed("R1", "2018-06-10", A, C)]}), "R-INT-04") == []


# --- the five extra plots through the whole pipeline ------------------------------------------
def test_extra_plots_trigger_their_rule_and_no_golden_does():
    conn = make_db()
    for name in ("x001", "x002", "x003", "x004", "x005"):
        doc = load.load_extra(conn, name)
        p = doc["plot"]
        req = {"plot": {"district_id": "gazipur", "upazila_id": "kaliakair", "mouza_id": p["mouza_id"],
                        "survey": "BS", "khatian_no": p["khatian_no"], "dag_no": p["dag_no"]},
               "seller": doc["seller"], "consents": {"bank": True}}
        r = asyncio.run(run_check(conn, req))
        got = {f["rule_id"] for f in r["findings"]}
        assert set(doc["expected_rules"]) <= got, (name, got)
        assert r["verdict"] in ("RED", "AMBER")


def test_no_golden_sample_triggers_a_tier2_rule():
    conn = make_db()
    samples = json.load(open("seed/golden/samples.json", encoding="utf-8"))
    for s in samples:
        if s["sample_id"] in ("P-008", "P-008B"):
            continue
        r = asyncio.run(run_check(conn, s["request"]))
        assert not ({f["rule_id"] for f in r["findings"]} & NO_RULES), s["sample_id"]
