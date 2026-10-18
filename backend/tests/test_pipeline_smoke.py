import asyncio
import json
from pathlib import Path

from app.engine.pipeline import run_check
from tests.contract_shape import check_report
from tests.helpers import make_db

SAMPLES = json.loads(Path("seed/golden/samples.json").read_text(encoding="utf-8"))


def check(conn, sample_id):
    s = next(x for x in SAMPLES if x["sample_id"] == sample_id)
    return asyncio.run(run_check(conn, s["request"]))


def test_p001_green_and_p003_red_slice():
    conn = make_db()
    r1, r3 = check(conn, "P-001"), check(conn, "P-003")
    check_report(r1)
    check_report(r3)
    print("P-001", r1["verdict"], [f["rule_id"] for f in r1["findings"]])
    print("P-003", r3["verdict"], [(f["rule_id"], f["severity"]) for f in r3["findings"]])
    assert r1["verdict"] == "GREEN" and r3["verdict"] == "RED"
