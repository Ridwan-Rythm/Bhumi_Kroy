"""Latency of the verification pipeline over the ten samples.  Run from backend/:
    python scripts/bench.py [runs_per_sample]
Note: adapter latency is SIMULATED (120-250 ms, fanned out in parallel), so p50 is dominated by the slowest
adapter. This benchmarks run_check() directly; the HTTP variant is added once FastAPI is installed."""
import asyncio
import json
import os
import statistics
import sys
import tempfile
import time

sys.path.insert(0, ".")
from app.core import db  # noqa: E402
from app.engine.pipeline import run_check  # noqa: E402
from seed import load  # noqa: E402
from tests.helpers import fresh_key  # noqa: E402


def main(runs: int) -> None:
    fresh_key()
    conn = db.connect(os.path.join(tempfile.mkdtemp(), "bench.db"))
    load.load(conn)
    samples = json.load(open("seed/golden/samples.json", encoding="utf-8"))
    times = []
    for _ in range(runs):
        for s in samples:
            t = time.perf_counter()
            asyncio.run(run_check(conn, s["request"]))
            times.append((time.perf_counter() - t) * 1000)
    times.sort()
    q = lambda p: times[min(len(times) - 1, int(p * len(times)))]  # noqa: E731
    print(f"n={len(times)}  p50={q(.5):.0f} ms  p95={q(.95):.0f} ms  max={times[-1]:.0f} ms  mean={statistics.mean(times):.0f} ms")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
