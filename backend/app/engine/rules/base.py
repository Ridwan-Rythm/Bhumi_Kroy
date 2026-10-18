"""Rule registry. A rule is a function(ctx) -> list[Finding dict], registered by ID with metadata."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

SEVERITY_ORDER = {"INTEGRITY": 0, "CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "INFO": 4, "COVERAGE": 5}


@dataclass
class RuleContext:
    plot: dict
    seller: dict            # {"name", "father_or_husband"}
    sources: dict           # source name -> SourceResult
    ledger: object          # LedgerStatus
    graph: object           # TitleGraph
    match: dict             # seller_match.best_match output


@dataclass
class RuleMeta:
    rule_id: str
    tier: int
    severity: str           # default severity (a rule may emit a different one, see contract 8.2)
    question: str
    func: Callable


REGISTRY: dict[str, RuleMeta] = {}

USABLE = ("OK", "NO_RECORD", "STALE")


def usable(ctx: RuleContext, *names: str) -> bool:
    """True when every named source answered completely. Rules that INFER something from replaying
    several sources must not fire on a data gap (a missing deed is not evidence of a broken chain)."""
    return all(ctx.sources[n].status in USABLE for n in names)


def rule(rule_id: str, tier: int, severity: str, question: str):
    def deco(fn):
        REGISTRY[rule_id] = RuleMeta(rule_id, tier, severity, question, fn)
        return fn
    return deco


def finding(rule_id: str, severity: str, question: str, evidence=(), params=None,
            confidence: str = "HIGH") -> dict:
    return {"rule_id": rule_id, "severity": severity, "confidence": confidence, "question": question,
            "evidence": list(evidence), "params": dict(params or {})}


def run_rules(ctx: RuleContext, max_tier: int = 2) -> list[dict]:
    out: list[dict] = []
    for meta in REGISTRY.values():
        if meta.tier <= max_tier:
            out.extend(meta.func(ctx))
    out.sort(key=lambda f: (SEVERITY_ORDER[f["severity"]], f["rule_id"], f["evidence"]))
    return out
