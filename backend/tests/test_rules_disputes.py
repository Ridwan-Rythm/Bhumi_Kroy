from tests.rule_helpers import A, C, findings, make_ctx

CASE = {"record_id": "CRT-1", "source": "court", "type": "COURT_CASE", "date": "2026-06-02", "case_ref": "TS-1/2026",
        "court": "c", "status": "OPEN", "linkage": "TEXT_MATCH"}


def case(**kw):
    return {**CASE, **kw}


def test_disp_01_fires_on_open_text_match_and_exact():
    for linkage in ("TEXT_MATCH", "EXACT"):
        f = findings(make_ctx({"court": [case(linkage=linkage)]}), "R-DISP-01")
        assert len(f) == 1 and f[0]["severity"] == "CRITICAL"
        assert f[0]["params"] == {"case_ref": "TS-1/2026", "court": "c", "linkage": linkage}


def test_disp_01_does_not_fire_on_disposed_case():
    assert findings(make_ctx({"court": [case(status="DISPOSED")]}), "R-DISP-01") == []


def test_disp_01_edge_party_name_only_is_disp_02_not_disp_01():
    ctx = make_ctx({"court": [case(linkage="PARTY_NAME_ONLY")]})
    assert findings(ctx, "R-DISP-01") == [] and len(findings(ctx, "R-DISP-02")) == 1


def test_disp_02_fires_on_party_name_only_open_case():
    f = findings(make_ctx({"court": [case(linkage="PARTY_NAME_ONLY")]}), "R-DISP-02")
    assert len(f) == 1 and f[0]["severity"] == "MEDIUM" and f[0]["params"] == {"case_ref": "TS-1/2026"}


def test_disp_02_does_not_fire_on_linked_case():
    assert findings(make_ctx({"court": [case()]}), "R-DISP-02") == []


def test_disp_02_edge_disposed_party_name_case_is_quiet():
    assert findings(make_ctx({"court": [case(linkage="PARTY_NAME_ONLY", status="DISPOSED")]}), "R-DISP-02") == []


def pending(applicant):
    return {"record_id": "MUT-1", "source": "mutation", "type": "MUTATION_PENDING", "date": "2026-09-20",
            "applicant": applicant, "case_no": "M-1"}


def test_disp_03_high_when_applicant_is_not_seller():
    f = findings(make_ctx({"mutation": [pending(A)]}), "R-DISP-03")
    assert len(f) == 1 and f[0]["severity"] == "HIGH"
    assert f[0]["params"] == {"mutation_ref": "MUT-1", "applicant_is_seller": False}


def test_disp_03_medium_when_applicant_is_seller():
    f = findings(make_ctx({"mutation": [pending(C)]}), "R-DISP-03")
    assert len(f) == 1 and f[0]["severity"] == "MEDIUM" and f[0]["params"]["applicant_is_seller"] is True


def test_disp_03_edge_no_pending_or_applied_mutation_is_quiet():
    applied = {**pending(A), "type": "MUTATION_APPLIED"}
    assert findings(make_ctx({"mutation": [applied]}), "R-DISP-03") == []
    assert findings(make_ctx({}), "R-DISP-03") == []
