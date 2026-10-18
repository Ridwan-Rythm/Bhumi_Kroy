"""contracts/report.schema.json is current, and real reports validate against it."""
import asyncio
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from app.engine.pipeline import run_check
from scripts import export_schema
from tests.helpers import make_db

SAMPLES = json.loads(Path("seed/golden/samples.json").read_text(encoding="utf-8"))
SCHEMA_PATH = Path("..") / "contracts" / "report.schema.json"


def test_committed_schema_matches_the_models():
    assert SCHEMA_PATH.read_text(encoding="utf-8") == export_schema.build(), \
        "contracts/report.schema.json is stale: run `cd backend && python -m scripts.export_schema`"


def test_every_sample_report_validates_against_the_schema():
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    conn = make_db()
    for s in SAMPLES:
        report = asyncio.run(run_check(conn, s["request"]))
        errors = sorted(validator.iter_errors(report), key=lambda e: list(e.path))
        assert not errors, (s["sample_id"], [f"{list(e.path)}: {e.message}" for e in errors[:3]])


def test_schema_rejects_a_report_with_an_extra_or_missing_field():
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    report = asyncio.run(run_check(make_db(), SAMPLES[0]["request"]))
    assert validator.is_valid(report)
    assert not validator.is_valid({**report, "surprise": 1})
    assert not validator.is_valid({k: v for k, v in report.items() if k != "verdict"})
    assert not validator.is_valid({**report, "verdict": "SAFE"})
