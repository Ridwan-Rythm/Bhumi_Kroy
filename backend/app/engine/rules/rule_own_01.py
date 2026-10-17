from app.engine.rules.base import finding, rule


@rule("R-OWN-01", 1, "CRITICAL", "Q1")
def r_own_01(ctx):
    """No current record holder matches the seller (tier NONE)."""
    if ctx.match["tier"] != "NONE":
        return []
    conf = "HIGH" if ctx.seller.get("father_or_husband") else "MEDIUM"
    return [finding("R-OWN-01", "CRITICAL", "Q1", [], {}, conf)]
