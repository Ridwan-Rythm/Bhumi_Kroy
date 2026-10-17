from app.engine.rules.base import finding, rule


@rule("R-CHAIN-02", 2, "HIGH", "Q2")
def r_chain_02(ctx):
    """Invariant I1: shares of a khatian do not sum to 1."""
    return [finding("R-CHAIN-02", "HIGH", "Q2", [a.record_ref], {"share_sum": round(float(a.detail["share_sum"]), 4)})
            for a in ctx.graph.anomalies if a.kind == "SHARE_SUM"]
