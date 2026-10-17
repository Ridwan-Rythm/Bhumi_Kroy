from app.engine import seller_match
from app.engine.rules.base import finding, rule


@rule("R-DISP-03", 1, "MEDIUM", "Q3")
def r_disp_03(ctx):
    """Pending mutation application. HIGH when the applicant is not the seller."""
    out = []
    for r in ctx.sources["mutation"].records:
        if r["type"] != "MUTATION_PENDING":
            continue
        is_seller = seller_match.is_same_person(ctx.seller["name"], ctx.seller.get("father_or_husband"),
                                                r["applicant"])
        out.append(finding("R-DISP-03", "MEDIUM" if is_seller else "HIGH", "Q3", [r["record_id"]],
                           {"mutation_ref": r["record_id"], "applicant_is_seller": is_seller}))
    return out
