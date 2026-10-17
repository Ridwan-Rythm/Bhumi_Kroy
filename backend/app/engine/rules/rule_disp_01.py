from app.engine.rules.base import finding, rule


@rule("R-DISP-01", 1, "CRITICAL", "Q3")
def r_disp_01(ctx):
    """Open case linked to the plot (EXACT or TEXT_MATCH)."""
    out = []
    for r in ctx.sources["court"].records:
        if r["type"] == "COURT_CASE" and r["status"] == "OPEN" and r["linkage"] in ("EXACT", "TEXT_MATCH"):
            conf = "HIGH" if r["linkage"] == "EXACT" else "MEDIUM"
            out.append(finding("R-DISP-01", "CRITICAL", "Q3", [r["record_id"]],
                               {"case_ref": r["case_ref"], "court": r["court"], "linkage": r["linkage"]}, conf))
    return out
