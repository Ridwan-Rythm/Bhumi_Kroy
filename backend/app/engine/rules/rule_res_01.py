from app.engine.rules.base import finding, rule


@rule("R-RES-01", 1, "CRITICAL", "Q4")
def r_res_01(ctx):
    """Khas record: a private sale is not valid."""
    return [finding("R-RES-01", "CRITICAL", "Q4", [r["record_id"]], {"record_ref": r["record_id"]})
            for r in ctx.sources["khas"].records if r["type"] == "KHAS"]
