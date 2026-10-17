"""Hand-rolled structural check of a Report against contract section 6 (until jsonschema is available)."""
ENUMS = {
    "verdict": {"GREEN", "GREY", "AMBER", "RED", "INTEGRITY_ALERT"},
    "severity": {"INTEGRITY", "CRITICAL", "HIGH", "MEDIUM", "INFO", "COVERAGE"},
    "confidence": {"HIGH", "MEDIUM", "LOW"},
    "coverage": {"COVERED", "PARTIAL", "NOT_COVERED"},
    "tier": {"STRONG", "PROBABLE", "WEAK", "NONE", "NOT_RUN"},
    "status": {"OK", "NO_RECORD", "PARTIAL", "STALE", "UNAVAILABLE", "ERROR"},
    "kind": {"SURVEY_ENTRY", "SALE", "GIFT", "INHERITANCE", "PARTITION", "COURT_DECREE", "ACQUISITION",
             "MORTGAGE", "MORTGAGE_RELEASE", "LT_NOTICE", "MUTATION_PENDING", "MUTATION_APPLIED"},
    "reason": {"hash_mismatch", "link_broken", "checkpoint_mismatch", "signature_invalid", "height_mismatch"},
}
REPORT_KEYS = {"report_id", "short_code", "synthetic", "issued_at", "valid_until", "plot", "seller", "consents",
               "verdict", "coverage", "findings", "sources", "holders_summary", "timeline", "not_checked",
               "ledger", "key_id", "signed_payload_b64", "signature_b64"}
PRIMS = (str, int, float, bool, type(None))


def check_report(r: dict) -> None:
    assert set(r) == REPORT_KEYS, set(r) ^ REPORT_KEYS
    assert r["synthetic"] is True and r["verdict"] in ENUMS["verdict"]
    assert set(r["coverage"]) == {"Q1", "Q2", "Q3", "Q4", "Q5", "Q6"}
    assert all(v in ENUMS["coverage"] for v in r["coverage"].values())
    assert len(r["sources"]) == 6
    for s in r["sources"]:
        assert set(s) == {"source", "status", "as_of", "maturity", "linkage", "latency_ms", "record_count", "reason"}
        assert s["status"] in ENUMS["status"]
    for f in r["findings"]:
        assert set(f) == {"rule_id", "severity", "confidence", "question", "evidence", "params"}
        assert f["severity"] in ENUMS["severity"] and f["confidence"] in ENUMS["confidence"]
        assert all(isinstance(v, PRIMS) for v in f["params"].values()), f
    for e in r["timeline"]:
        assert set(e) == {"date", "kind", "survey", "from_masked", "to_masked", "share", "area_decimal",
                          "record_ref", "source", "flagged_by"}
        assert e["kind"] in ENUMS["kind"]
    for n in r["not_checked"]:
        assert set(n) == {"code", "params"} and all(isinstance(v, PRIMS) for v in n["params"].values())
    assert r["seller"]["match"]["tier"] in ENUMS["tier"]
    assert set(r["ledger"]) == {"ok", "broken_at_seq", "reason", "height", "head_hash", "checkpoint"}
    if r["verdict"] == "INTEGRITY_ALERT":
        for k in ("report_id", "short_code", "valid_until", "signed_payload_b64", "signature_b64"):
            assert r[k] is None, k
    else:
        for k in ("report_id", "short_code", "valid_until", "signed_payload_b64", "signature_b64"):
            assert r[k] is not None, k
