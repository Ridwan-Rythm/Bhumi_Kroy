"""Verdict precedence (contract 8.1). A GREEN with any question not COVERED is a bug."""
from __future__ import annotations


def compute(findings: list[dict], coverage: dict) -> str:
    sev = {f["severity"] for f in findings}
    if "INTEGRITY" in sev:
        return "INTEGRITY_ALERT"
    if "CRITICAL" in sev:
        return "RED"
    if sev & {"HIGH", "MEDIUM"}:
        return "AMBER"
    if any(v != "COVERED" for v in coverage.values()):
        return "GREY"
    return "GREEN"
