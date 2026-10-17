from app.engine.rules.base import finding, rule


@rule("R-LIEN-01", 1, "CRITICAL", "Q5")
def r_lien_01(ctx):
    """Active mortgage or lien (a mortgage with no recorded release)."""
    recs = ctx.sources["bank"].records
    released = {r["mortgage_ref"] for r in recs if r["type"] == "MORTGAGE_RELEASE"}
    return [finding("R-LIEN-01", "CRITICAL", "Q5", [r["record_id"]],
                    {"lien_ref": r["record_id"], "bank_name": r["bank_name"]})
            for r in recs if r["type"] == "MORTGAGE" and r["status"] == "ACTIVE" and r["record_id"] not in released]
