from app.engine.rules.base import finding, rule


@rule("R-CHAIN-04", 1, "MEDIUM", "Q2")
def r_chain_04(ctx):
    """Land class changed with no conversion record."""
    return [finding("R-CHAIN-04", "MEDIUM", "Q2", [c["record_ref"]],
                    {"from_class": c["from_class"], "to_class": c["to_class"]})
            for c in ctx.graph.class_changes() if not c["explained"]]
