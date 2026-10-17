from app.adapters.base import SOURCES
from app.engine.rules.base import finding, rule


@rule("R-INT-01", 1, "INTEGRITY", "Q6")
def r_int_01(ctx):
    """Ledger or checkpoint verification failed."""
    if ctx.ledger.ok:
        return []
    return [finding("R-INT-01", "INTEGRITY", "Q6", [], {"reason": ctx.ledger.reason,
                                                       "broken_at_seq": ctx.ledger.broken_at_seq})]


@rule("R-INT-02", 1, "COVERAGE", "Q6")
def r_int_02(ctx):
    """A source is STALE."""
    return [finding("R-INT-02", "COVERAGE", "Q6", [], {"source": s, "as_of": ctx.sources[s].as_of})
            for s in SOURCES if ctx.sources[s].status == "STALE"]


@rule("R-INT-03", 1, "COVERAGE", "Q6")
def r_int_03(ctx):
    """A source is UNAVAILABLE or ERROR."""
    return [finding("R-INT-03", "COVERAGE", "Q6", [],
                    {"source": s, "reason": ctx.sources[s].reason or ctx.sources[s].status.lower()})
            for s in SOURCES if ctx.sources[s].status in ("UNAVAILABLE", "ERROR")]
