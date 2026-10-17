"""Per-question coverage and the 'what we did not check' list (contract 8.1, 8.3)."""
from __future__ import annotations

from app.adapters.base import MATURITY_ORDER, SOURCES

REQUIRED = {"Q1": ("land_records", "mutation"), "Q2": ("land_records", "registry"),
            "Q3": ("mutation", "court"), "Q4": ("khas",), "Q5": ("bank", "registry")}
STATIC_CODES = ["static_physical_possession", "static_boundaries", "static_unregistered_agreements",
                "static_equitable_mortgage", "static_seller_documents", "static_legal_review"]


def qualifies(r) -> bool:
    if r.status == "OK":
        return True
    return (r.status == "NO_RECORD" and MATURITY_ORDER[r.maturity] >= MATURITY_ORDER["M2"]
            and r.linkage in ("EXACT", "TEXT_MATCH", None))


def compute(sources: dict, ledger_ok: bool) -> dict:
    cov = {}
    for q, req in REQUIRED.items():
        n = sum(1 for s in req if qualifies(sources[s]))
        cov[q] = "COVERED" if n == len(req) else ("PARTIAL" if n else "NOT_COVERED")
    cov["Q6"] = "COVERED" if ledger_ok else "NOT_COVERED"
    return {q: cov[q] for q in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6")}


def not_checked(sources: dict) -> list[dict]:
    out = []
    for name in SOURCES:
        r = sources[name]
        if r.status in ("UNAVAILABLE", "ERROR"):
            out.append({"code": "source_unavailable",
                        "params": {"source": name, "reason": r.reason or r.status.lower()}})
        elif r.status == "STALE":
            out.append({"code": "source_stale", "params": {"source": name, "as_of": r.as_of}})
        elif r.status == "PARTIAL":
            out.append({"code": "source_partial", "params": {"source": name}})
        elif r.status == "NO_RECORD" and r.linkage == "PARTY_NAME_ONLY":
            out.append({"code": "linkage_party_name_only", "params": {"source": name}})
        if MATURITY_ORDER[r.maturity] < MATURITY_ORDER["M2"]:
            out.append({"code": "low_maturity", "params": {"source": name, "maturity": r.maturity}})
    out += [{"code": c, "params": {}} for c in STATIC_CODES]
    return out
