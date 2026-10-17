from app.engine.rules.base import finding, rule


@rule("R-INFO-01", 1, "INFO", "Q1")
def r_info_01(ctx):
    """STRONG name match: still confirm NID and father's name (never auto-clear)."""
    return [finding("R-INFO-01", "INFO", "Q1")] if ctx.match["tier"] == "STRONG" else []


@rule("R-INFO-02", 1, "INFO", "Q2")
def r_info_02(ctx):
    return [finding("R-INFO-02", "INFO", "Q2", [], {"depth": ctx.graph.depth})] if ctx.graph.depth else []


@rule("R-INFO-03", 1, "INFO", "Q2")
def r_info_03(ctx):
    if not ctx.graph.depth:
        return []
    return [finding("R-INFO-03", "INFO", "Q2", [], {"last_transfer_date": ctx.graph.last_transfer_date()})]
