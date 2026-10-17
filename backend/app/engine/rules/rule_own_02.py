from app.engine.rules.base import finding, rule


@rule("R-OWN-02", 1, "MEDIUM", "Q1")
def r_own_02(ctx):
    """Seller matches only at WEAK or PROBABLE tier."""
    tier = ctx.match["tier"]
    if tier not in ("WEAK", "PROBABLE"):
        return []
    return [finding("R-OWN-02", "MEDIUM", "Q1", [], {"tier": tier}, "MEDIUM" if tier == "PROBABLE" else "LOW")]
