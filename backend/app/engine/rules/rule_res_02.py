from app.engine.rules.base import finding, rule


@rule("R-RES-02", 1, "CRITICAL", "Q4")
def r_res_02(ctx):
    """Vested (Ka / Kha) or abandoned listing."""
    out = []
    for r in ctx.sources["khas"].records:
        if r["type"] in ("VESTED", "ABANDONED"):
            lst = r.get("list") or ("ABANDONED" if r["type"] == "ABANDONED" else "KA")
            out.append(finding("R-RES-02", "CRITICAL", "Q4", [r["record_id"]],
                               {"list": lst, "record_ref": r["record_id"]}))
    return out
