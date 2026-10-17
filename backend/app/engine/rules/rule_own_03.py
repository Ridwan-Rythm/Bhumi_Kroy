from app.engine.rules.base import finding, rule, usable
from app.engine.title_graph import frac_text


@rule("R-OWN-03", 2, "CRITICAL", "Q1")
def r_own_03(ctx):
    """Invariant I2: share sold exceeds what the seller held at the deed date.
    Deeds already reported as a double sale (R-SALE-01) are not reported twice."""
    doubles = {d.deed_a for d in ctx.graph.double_sales} | {d.deed_b for d in ctx.graph.double_sales}
    if not usable(ctx, "land_records", "registry", "mutation"):
        return []
    return [finding("R-OWN-03", "CRITICAL", "Q1", [a.record_ref],
                    {"seller_share": frac_text(a.detail["seller_share"]),
                     "selling_share": frac_text(a.detail["selling_share"])})
            for a in ctx.graph.anomalies if a.kind == "OVERSELL" and a.record_ref not in doubles]
