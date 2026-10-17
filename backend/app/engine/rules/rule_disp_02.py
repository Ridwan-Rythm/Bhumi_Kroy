from app.engine.rules.base import finding, rule


@rule("R-DISP-02", 1, "MEDIUM", "Q3")
def r_disp_02(ctx):
    """Open case that matches only by party name."""
    return [finding("R-DISP-02", "MEDIUM", "Q3", [r["record_id"]], {"case_ref": r["case_ref"]}, "LOW")
            for r in ctx.sources["court"].records
            if r["type"] == "COURT_CASE" and r["status"] == "OPEN" and r["linkage"] == "PARTY_NAME_ONLY"]
