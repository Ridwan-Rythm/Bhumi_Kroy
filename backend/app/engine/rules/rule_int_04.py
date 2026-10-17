from app.engine.rules.base import finding, rule


@rule("R-INT-04", 2, "HIGH", "Q6")
def r_int_04(ctx):
    """Cross-source conflict: the registry shows a sale to B, land records still show the old holder,
    and there is no LT_NOTICE for that deed."""
    g = ctx.graph
    if not g.snapshots:
        return []
    last = g.snapshots[-1]
    holders = {(h["name"], h.get("father")) for h in last["holders"]}
    noticed = {r["sale_ref"] for r in g.of_type("LT_NOTICE")}
    out = []
    for d in g.of_type("SALE", "GIFT"):
        if d["date"] > last["date"] and (d["to"]["name"], d["to"].get("father")) not in holders \
                and d["record_id"] not in noticed:
            out.append(finding("R-INT-04", "HIGH", "Q6", [d["record_id"], last["record_id"]],
                               {"source_a": "registry", "source_b": "land_records"}, "MEDIUM"))
    return out
