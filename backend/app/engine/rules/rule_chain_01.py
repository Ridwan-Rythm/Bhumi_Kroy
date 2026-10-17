from app.engine.rules.base import finding, rule, usable


@rule("R-CHAIN-01", 2, "HIGH", "Q2")
def r_chain_01(ctx):
    """Invariant I4: a generation's holders are not explained by the previous generation's events."""
    if not usable(ctx, "land_records", "registry", "mutation"):
        return []
    return [finding("R-CHAIN-01", "HIGH", "Q2", [a.record_ref], {}, "MEDIUM")
            for a in ctx.graph.anomalies if a.kind == "GENERATION_UNEXPLAINED"]
