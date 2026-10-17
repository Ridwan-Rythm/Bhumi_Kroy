from app.engine.rules.base import finding, rule
from app.engine.title_graph import frac_text


@rule("R-SALE-01", 1, "CRITICAL", "Q5")
def r_sale_01(ctx):
    """Invariant I7: overlapping in time AND in share. A -> B -> C is not a double sale."""
    return [finding("R-SALE-01", "CRITICAL", "Q5", [d.deed_a, d.deed_b],
                    {"deed_a": d.deed_a, "deed_b": d.deed_b, "overlap": frac_text(d.overlap)})
            for d in ctx.graph.double_sales]
