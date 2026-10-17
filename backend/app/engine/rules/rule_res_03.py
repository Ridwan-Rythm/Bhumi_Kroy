from app.engine.rules.base import finding, rule


@rule("R-RES-03", 2, "CRITICAL", "Q4")
def r_res_03(ctx):
    """Acquisition notice or proposal."""
    return [finding("R-RES-03", "CRITICAL", "Q4", [r["record_id"]], {"record_ref": r["record_id"]})
            for r in ctx.sources["khas"].records if r["type"] == "ACQUISITION"]
