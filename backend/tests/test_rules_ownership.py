from tests.rule_helpers import CLEAN_LAND, A, C, fake_matcher, findings, make_ctx, tier


def test_own_01_fires_when_no_holder_matches():
    ctx = make_ctx(CLEAN_LAND, seller={"name": A["name"], "father_or_husband": A["father"]})
    f = findings(ctx, "R-OWN-01")
    assert len(f) == 1 and f[0]["severity"] == "CRITICAL" and f[0]["question"] == "Q1"


def test_own_01_does_not_fire_on_strong_match():
    assert findings(make_ctx(CLEAN_LAND), "R-OWN-01") == []


def test_own_01_edge_no_holders_means_not_run_not_critical():
    ctx = make_ctx({})
    assert ctx.match["tier"] == "NOT_RUN" and findings(ctx, "R-OWN-01") == []


def test_own_02_fires_on_probable_and_weak_with_tier_param():
    for t in ("PROBABLE", "WEAK"):
        with fake_matcher(tier(t)):
            f = findings(make_ctx(CLEAN_LAND), "R-OWN-02")
        assert len(f) == 1 and f[0]["params"] == {"tier": t} and f[0]["severity"] == "MEDIUM"


def test_own_02_does_not_fire_on_strong_or_none():
    assert findings(make_ctx(CLEAN_LAND), "R-OWN-02") == []
    ctx = make_ctx(CLEAN_LAND, seller={"name": A["name"], "father_or_husband": None})
    assert findings(ctx, "R-OWN-02") == []


def test_own_02_edge_best_tier_among_several_holders_is_used():
    land = {"land_records": [__import__("tests.rule_helpers", fromlist=["survey"]).survey(
        "LND-1", "2018-01-01", "BS", [(A, "1/2"), (C, "1/2")])]}
    ctx = make_ctx(land)  # seller == C exactly -> STRONG even though A does not match
    assert ctx.match["tier"] == "STRONG"
    assert findings(ctx, "R-OWN-01") == [] and len(findings(ctx, "R-INFO-01")) == 1


def test_info_01_fires_on_strong_only_and_never_changes_verdict():
    from app.engine import verdict
    assert len(findings(make_ctx(CLEAN_LAND), "R-INFO-01")) == 1
    with fake_matcher(tier("PROBABLE")):
        assert findings(make_ctx(CLEAN_LAND), "R-INFO-01") == []
    f = findings(make_ctx(CLEAN_LAND), "R-INFO-01")
    assert verdict.compute(f, {q: "COVERED" for q in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6")}) == "GREEN"
