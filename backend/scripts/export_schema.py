"""Writes contracts/report.schema.json from app.models.Report (contract S0 deliverable).

    cd backend && python -m scripts.export_schema          # write
    cd backend && python -m scripts.export_schema --check  # exit 1 if the committed file is stale
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from app.models import Report

OUT = Path(__file__).resolve().parents[2] / "contracts" / "report.schema.json"


def build() -> str:
    schema = Report.model_json_schema()
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema",
              "$id": "https://landcheck.example/contracts/report.schema.json",
              "title": "Bhumi_Kroy Report (contract section 6)", **schema}
    return json.dumps(schema, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    text = build()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print(f"{OUT} is stale: run `cd backend && python -m scripts.export_schema`")
            return 1
        print("report.schema.json is up to date")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
