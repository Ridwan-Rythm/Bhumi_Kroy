import asyncio
import json
import re
from datetime import timedelta

from app.core import clock
from app.core.errors import AppError
from app.engine.pipeline import run_check
from app.engine.report_builder import findings_hash
from app.ledger import chain, signer
from tests.contract_shape import check_report
from tests.helpers import make_db, raises
from tests.rule_helpers import fake_matcher, tier

SAMPLES = {s["sample_id"]: s for s in json.load(open("seed/golden/samples.json", encoding="utf-8"))}


def check(conn, sid, **mod):
    req = json.loads(json.dumps(SAMPLES[sid]["request"]))
    for path, v in mod.items():
        a, b = path.split("__")
        req[a][b] = v
    return asyncio.run(run_check(conn, req))


def test_report_is_signed_stored_and_consistent():
    conn = make_db()
    r = check(conn, "P-001")
    check_report(r)
    assert re.fullmatch(r"RPT-\d{4}-\d{6}", r["report_id"])
    assert re.fullmatch(r"[A-Z2-9]{4}-[A-Z2-9]{4}", r["short_code"]) and not set("IO01L") & set(r["short_code"])
    raw = signer.b64u_decode(r["signed_payload_b64"])
    assert signer.verify(raw, r["signature_b64"])
    p = json.loads(raw)
    assert p["report_id"] == r["report_id"] and p["verdict"] == r["verdict"] and p["key_id"] == r["key_id"]
    assert p["findings_hash"] == findings_hash(r["findings"])
    assert p["ledger_height"] == r["ledger"]["height"] and p["ledger_head"] == r["ledger"]["head_hash"]
    assert clock.parse_iso(r["valid_until"]) - clock.parse_iso(r["issued_at"]) == timedelta(days=7)
    stored = json.loads(conn.execute("SELECT json FROM reports WHERE report_id=?", (r["report_id"],)).fetchone()[0])
    assert stored == r


def test_pinned_checkpoint_matches_ledger_head_and_verifies():
    conn = make_db()
    r = check(conn, "P-001")
    cp = r["ledger"]["checkpoint"]
    assert r["ledger"]["ok"] and cp["height"] == r["ledger"]["height"] and cp["head_hash"] == r["ledger"]["head_hash"]
    msg = chain.checkpoint_message({"plot_id": "P-001", **{k: cp[k] for k in ("height", "head_hash", "ts", "key_id")}})
    assert signer.verify(msg, cp["signature_b64"])


def test_timeline_masks_names_and_flags_evidence():
    conn = make_db()
    r = check(conn, "P-003")
    blob = json.dumps(r["timeline"], ensure_ascii=False)
    full = [h["name"] for rec in conn.execute("SELECT data_json FROM records WHERE plot_id='P-003'")
            for h in json.loads(rec[0]).get("holders", [])]
    assert full and not any(n in blob for n in full)
    assert all("*" in e["to_masked"] for e in r["timeline"] if e["kind"] == "SURVEY_ENTRY")
    flagged = {e["record_ref"]: e["flagged_by"] for e in r["timeline"] if e["flagged_by"]}
    assert {tuple(v) for v in flagged.values()} == {("R-LIEN-01",), ("R-DISP-03",)}
    assert [e["date"] for e in r["timeline"]] == sorted(e["date"] for e in r["timeline"])


def test_holders_summary_and_seller_block():
    r = check(make_db(), "P-001")
    assert r["holders_summary"] == {"holder_count": 1, "seller_share": "1"}
    assert r["seller"]["match"] == {"tier": "STRONG", "score": 1.0} and r["consents"] == {"bank": True}
    assert r["plot"]["district_id"] == "gazipur" and r["plot"]["jl_no"] == "41"


def test_consent_withdrawn_makes_clean_plot_grey_not_green():
    r = check(make_db(), "P-001", consents__bank=False)
    assert r["verdict"] == "GREY" and r["coverage"]["Q5"] == "PARTIAL"
    f = [x for x in r["findings"] if x["rule_id"] == "R-INT-03"]
    assert f[0]["params"] == {"source": "bank", "reason": "consent_required"}
    assert {"code": "source_unavailable", "params": {"source": "bank", "reason": "consent_required"}} in r["not_checked"]


def test_withholding_consent_hides_the_lien_but_never_yields_green():
    r = check(make_db(), "P-003", consents__bank=False)
    assert "R-LIEN-01" not in {f["rule_id"] for f in r["findings"]} and r["verdict"] == "AMBER"


def test_registry_timeout_gives_grey_and_partial_coverage():
    conn = make_db()
    conn.execute("UPDATE plots SET adapter_config_json=? WHERE plot_id='P-001'",
                 (json.dumps({"registry": {"latency_ms": 2000}}),))
    r = asyncio.run(run_check(conn, SAMPLES["P-001"]["request"], timeout_s=0.5))
    assert r["verdict"] == "GREY" and r["coverage"]["Q2"] == "PARTIAL" and r["coverage"]["Q5"] == "PARTIAL"
    assert [s for s in r["sources"] if s["source"] == "registry"][0]["reason"] == "timeout"


def test_stale_source_gives_grey_with_stale_finding():
    conn = make_db()
    conn.execute("UPDATE plots SET adapter_config_json=? WHERE plot_id='P-001'",
                 (json.dumps({"khas": {"as_of_age_days": 45}}),))
    r = asyncio.run(run_check(conn, SAMPLES["P-001"]["request"]))
    assert r["verdict"] == "GREY" and r["coverage"]["Q4"] == "NOT_COVERED"  # Q4 needs only khas
    assert "R-INT-02" in {f["rule_id"] for f in r["findings"]}


def test_engine_wiring_for_name_variants_with_a_fake_matcher():
    """Engine wiring only; real accuracy is verified against Nazifa's matcher."""
    conn = make_db()
    with fake_matcher(tier("PROBABLE", 0.88)):
        r = check(conn, "P-008")
    assert r["verdict"] == "AMBER" and r["findings"][0]["params"] == {"tier": "PROBABLE"}
    assert r["seller"]["match"] == {"tier": "PROBABLE", "score": 0.88}
    with fake_matcher(tier("STRONG", 0.97)):
        r = check(conn, "P-008B")
    assert r["verdict"] == "GREEN" and "R-INFO-01" in {f["rule_id"] for f in r["findings"]}


# --- input robustness --------------------------------------------------------------------------
def test_bangla_digits_and_zero_width_characters_are_normalised():
    conn = make_db()
    r = check(conn, "P-001", plot__khatian_no="১২০৩", plot__dag_no="৪৫২১")
    assert r["plot"]["khatian_no"] == "1203" and r["verdict"] == "GREEN"
    name = SAMPLES["P-001"]["request"]["seller"]["name"]
    r = check(conn, "P-001", seller__name="\u200b" + name.replace(" ", "  ") + "\u200d")
    assert r["seller"]["name"] == name and r["verdict"] == "GREEN"


def test_validation_and_not_found_errors_carry_field():
    conn = make_db()
    base = SAMPLES["P-001"]["request"]

    def go(req):
        return raises(AppError, lambda: asyncio.run(run_check(conn, req)))

    bad = json.loads(json.dumps(base)); bad["plot"]["khatian_no"] = "12ab"
    e = go(bad); assert (e.code, e.field, e.http_status) == ("VALIDATION_ERROR", "plot.khatian_no", 422)
    bad = json.loads(json.dumps(base)); bad["seller"]["name"] = "   "
    assert go(bad).field == "seller.name"
    bad = json.loads(json.dumps(base)); bad["plot"]["survey"] = "XX"
    assert go(bad).field == "plot.survey"
    bad = json.loads(json.dumps(base)); bad["consents"] = {"bank": "yes"}
    assert go(bad).field == "consents.bank"
    bad = json.loads(json.dumps(base)); bad["plot"]["dag_no"] = "99999"
    e = go(bad); assert (e.code, e.http_status) == ("NOT_FOUND", 404)
    bad = json.loads(json.dumps(base)); bad["plot"]["upazila_id"] = "sreepur"  # mouza is not in that upazila
    assert go(bad).code == "NOT_FOUND"
    assert go({}).code == "VALIDATION_ERROR" and go("x").code == "VALIDATION_ERROR"


def test_markup_in_names_is_data_never_interpreted():
    evil = '<script>alert(1)</script>"; DROP TABLE plots;--'
    conn = make_db()
    r = check(conn, "P-001", seller__name=evil)
    assert r["seller"]["name"] == evil and r["verdict"] == "RED"  # no holder matches
    assert conn.execute("SELECT COUNT(*) FROM plots").fetchone()[0] == 9
    json.dumps(r)  # serialisable; the API returns JSON only, never HTML


def test_overlong_name_is_rejected():
    e = raises(AppError, lambda: asyncio.run(run_check(make_db(), {**SAMPLES["P-001"]["request"],
               "seller": {"name": "ক" * 500}})))
    assert e.field == "seller.name"


def test_a_source_outage_never_creates_a_replay_finding():
    """Regression: registry down made R-CHAIN-01 fire because the sale deed was 'missing'."""
    for src in ("registry", "mutation"):
        conn = make_db()
        conn.execute("UPDATE plots SET adapter_config_json=? WHERE plot_id='P-001'",
                     (json.dumps({src: {"status": "UNAVAILABLE", "reason": "outage"}}),))
        r = asyncio.run(run_check(conn, SAMPLES["P-001"]["request"]))
        assert {f["rule_id"] for f in r["findings"] if f["severity"] != "INFO"} == {"R-INT-03"}, src
        assert r["verdict"] == "GREY"
