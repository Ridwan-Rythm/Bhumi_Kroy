from app.engine.rules.base import finding, rule


@rule("R-CHAIN-03", 1, "HIGH", "Q2")
def r_chain_03(ctx):
    """Invariant I5: area drift between surveys. <=3% ignored, <=10% MEDIUM, above HIGH; unless explained."""
    out = []
    for d in ctx.graph.area_drifts():
        if d["explained"] or d["drift_pct"] <= 3:
            continue
        sev = "MEDIUM" if d["drift_pct"] <= 10 else "HIGH"
        out.append(finding("R-CHAIN-03", sev, "Q2", [d["record_ref"]],
                           {k: d[k] for k in ("from_survey", "to_survey", "from_area", "to_area", "drift_pct")}))
    return out
