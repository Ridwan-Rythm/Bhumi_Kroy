from app.ledger.chain import LedgerStatus
from tests.rule_helpers import findings, make_ctx, src


def test_int_01_fires_with_reason_and_seq():
    bad = LedgerStatus(False, 3, "hash_mismatch", 5, "h", None)
    f = findings(make_ctx(ledger=bad), "R-INT-01")
    assert len(f) == 1 and f[0]["severity"] == "INTEGRITY"
    assert f[0]["params"] == {"reason": "hash_mismatch", "broken_at_seq": 3}


def test_int_01_does_not_fire_on_clean_ledger():
    assert findings(make_ctx(), "R-INT-01") == []


def test_int_01_edge_checkpoint_level_failure_has_no_seq():
    bad = LedgerStatus(False, None, "checkpoint_mismatch", 5, "h", None)
    assert findings(make_ctx(ledger=bad), "R-INT-01")[0]["params"]["broken_at_seq"] is None


def test_int_02_fires_on_stale_source_with_as_of():
    f = findings(make_ctx(overrides={"khas": src("khas", status="STALE", reason="stale")}), "R-INT-02")
    assert len(f) == 1 and f[0]["severity"] == "COVERAGE" and f[0]["params"]["source"] == "khas"
    assert f[0]["params"]["as_of"] is not None


def test_int_02_does_not_fire_when_fresh():
    assert findings(make_ctx(), "R-INT-02") == []


def test_int_02_edge_stale_never_creates_amber_or_red():
    from app.engine import verdict
    f = findings(make_ctx(overrides={"khas": src("khas", status="STALE")}))
    assert verdict.compute(f, {q: "COVERED" for q in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6")}) == "GREEN"


def test_int_03_fires_on_unavailable_and_error_with_reason():
    ov = {"bank": src("bank", status="UNAVAILABLE", reason="consent_required"), "court": src("court", status="ERROR")}
    f = {x["params"]["source"]: x for x in findings(make_ctx(overrides=ov), "R-INT-03")}
    assert f["bank"]["params"]["reason"] == "consent_required" and f["court"]["params"]["reason"] == "error"


def test_int_03_does_not_fire_when_all_sources_answer():
    assert findings(make_ctx(), "R-INT-03") == []


def test_int_03_edge_partial_is_not_unavailable():
    assert findings(make_ctx(overrides={"court": src("court", status="PARTIAL")}), "R-INT-03") == []
