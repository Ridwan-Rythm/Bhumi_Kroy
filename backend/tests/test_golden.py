"""The ten golden samples (contract section 9): verdict, EXACT set of non-INFO rule_ids, coverage."""
import asyncio
import json

from app import namematch
from app.engine.pipeline import run_check
from tests.contract_shape import check_report
from tests.helpers import make_db, skip

SAMPLES = {s["sample_id"]: s for s in json.load(open("seed/golden/samples.json", encoding="utf-8"))}
ALL_COVERED = {q: "COVERED" for q in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6")}

# sample -> (verdict, non-INFO rule_ids, coverage)
EXPECTED = {
    "P-001": ("GREEN", set(), ALL_COVERED),
    "P-002": ("RED", {"R-OWN-01"}, ALL_COVERED),
    "P-003": ("RED", {"R-LIEN-01", "R-DISP-03"}, ALL_COVERED),
    "P-004": ("RED", {"R-DISP-01"}, ALL_COVERED),
    "P-005": ("RED", {"R-RES-01"}, ALL_COVERED),
    "P-006": ("RED", {"R-SALE-01"}, ALL_COVERED),
    "P-007": ("AMBER", {"R-CHAIN-03", "R-CHAIN-04"}, ALL_COVERED),
    "P-008": ("AMBER", {"R-OWN-02"}, ALL_COVERED),
    "P-008B": ("GREEN", set(), ALL_COVERED),
    "P-009": ("GREY", {"R-INT-03"}, {**ALL_COVERED, "Q3": "PARTIAL", "Q5": "PARTIAL"}),
}
NEEDS_REAL_MATCHER = {"P-008", "P-008B"}


def run(conn, sid):
    r = asyncio.run(run_check(conn, SAMPLES[sid]["request"]))
    check_report(r)
    return r


def non_info(r):
    return {f["rule_id"] for f in r["findings"] if f["severity"] != "INFO"}


def _assert_sample(conn, sid):
    verdict, rules, cov = EXPECTED[sid]
    r = run(conn, sid)
    assert r["verdict"] == verdict, (sid, r["verdict"], [f["rule_id"] for f in r["findings"]])
    assert SAMPLES[sid]["expected_verdict"] == verdict
    assert non_info(r) == rules, (sid, non_info(r))
    assert r["coverage"] == cov, (sid, r["coverage"])
    return r


def test_samples_endpoint_data_has_the_ten_samples():
    assert list(SAMPLES) == ["P-001", "P-002", "P-003", "P-004", "P-005", "P-006", "P-007", "P-008", "P-008B", "P-009"]
    for s in SAMPLES.values():
        assert s["label_bn"] and s["label_en"] and s["request"]["plot"]["khatian_no"]


def test_golden_samples_without_name_variants():
    conn = make_db()
    for sid in EXPECTED:
        if sid not in NEEDS_REAL_MATCHER:
            _assert_sample(conn, sid)


def test_p003_severities_and_params():
    r = run(make_db(), "P-003")
    by = {f["rule_id"]: f for f in r["findings"]}
    assert by["R-LIEN-01"]["severity"] == "CRITICAL" and by["R-LIEN-01"]["params"]["lien_ref"].startswith("BNK-")
    assert by["R-DISP-03"]["severity"] == "HIGH" and by["R-DISP-03"]["params"]["applicant_is_seller"] is False


def test_p007_severities():
    by = {f["rule_id"]: f for f in run(make_db(), "P-007")["findings"]}
    assert by["R-CHAIN-03"]["severity"] == "HIGH" and by["R-CHAIN-03"]["params"]["drift_pct"] == 27.5
    assert by["R-CHAIN-04"]["severity"] == "MEDIUM"
    assert by["R-CHAIN-04"]["params"] == {"from_class": "ধান", "to_class": "বাড়ি"}


def test_p009_unknown_is_not_safe():
    r = run(make_db(), "P-009")
    codes = {n["code"] for n in r["not_checked"]}
    assert {"linkage_party_name_only", "source_unavailable"} <= codes
    assert r["verdict"] == "GREY"


def test_p008_and_p008b_need_the_real_matcher():
    if getattr(namematch, "IS_STUB", False):
        skip("namematch is still the stub; P-008/P-008B are verified at the integration step")
    r = _assert_sample(make_db(), "P-008")
    assert r["findings"][0]["params"]["tier"] == "PROBABLE"
    r = _assert_sample(make_db(), "P-008B")
    assert "R-INFO-01" in {f["rule_id"] for f in r["findings"]}
