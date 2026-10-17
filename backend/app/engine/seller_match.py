"""Best name-match tier among the current record holders (wraps app.namematch.match_name)."""
from __future__ import annotations

from app import namematch

TIER_RANK = {"NONE": 0, "WEAK": 1, "PROBABLE": 2, "STRONG": 3}


def best_match(seller_name: str, seller_father: str | None, holders: list[dict]) -> dict:
    """Returns {tier, score, holder}. No holders (source unavailable) -> NOT_RUN."""
    if not holders:
        return {"tier": "NOT_RUN", "score": None, "holder": None}
    best = None
    for h in holders:
        r = namematch.match_name(seller_name, seller_father, h["name"], h.get("father"))
        rank = (TIER_RANK[r["tier"]], r["score"])
        if best is None or rank > best[0]:
            best = (rank, r, h)
    _, r, h = best
    return {"tier": r["tier"], "score": round(float(r["score"]), 4), "holder": h}


def is_same_person(seller_name: str, seller_father: str | None, other: dict) -> bool:
    """Used for 'applicant is seller' (R-DISP-03): PROBABLE or STRONG counts as the same person."""
    r = namematch.match_name(seller_name, seller_father, other["name"], other.get("father"))
    return r["tier"] in ("STRONG", "PROBABLE")
