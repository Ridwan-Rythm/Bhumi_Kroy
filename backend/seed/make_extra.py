"""Writes the five small Tier-2 plots seed/golden/extra_*.json. They are NOT part of the ten samples.
Run once from backend/:  python -m seed.make_extra   (the JSON files are committed and then hand-editable)."""
from __future__ import annotations

import json
from pathlib import Path

from seed.build_golden import Ids, PlotBuilder

OUT = Path(__file__).parent / "golden"
P = lambda n, f: {"name": n, "father": f}  # noqa: E731
A, B, C, D, E = (P("আলম মিয়া", "মৃত করিম মিয়া"), P("জসিম উদ্দিন", "মৃত হাশেম উদ্দিন"),
                 P("সালাম খান", "মৃত বশির খান"), P("রফিক শেখ", "মৃত নজরুল শেখ"), P("হারুন মোল্লা", "মৃত আজিজ মোল্লা"))
SELLER = {"name": C["name"], "father_or_husband": C["father"]}


def plot(pid, mouza, kh, dag, fn, expected):
    ids = Ids()
    base = 9000 + int(pid[2:]) * 10  # own id range: record_ids are globally unique and the ten samples use 1..99
    ids.n = {k: base for k in ids.n}
    b = PlotBuilder(pid, mouza, kh, dag, ids)
    fn(b)
    doc = {"plot": b.build(), "seller": SELLER, "expected_rules": expected}
    (OUT / f"extra_{pid.lower().replace('-', '')}.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def x1(b):  # R-OWN-03: B held 1/2 in RS but the 2010 deed conveys the whole plot
    b.survey_entry("1993-11-20", "RS", [(B, "1/2"), (E, "1/2")], 33.0, "ধান")
    b.sale("2010-05-18", B, C, "1", 33.0)
    b.survey_entry("2018-02-09", "BS", [(C, "1")], 33.0, "ধান")


def x2(b):  # R-CHAIN-01: BS holder C appears with no event linking him to RS holder B
    b.survey_entry("1993-11-20", "RS", [(B, "1")], 33.0, "ধান")
    b.survey_entry("2018-02-09", "BS", [(C, "1")], 33.0, "ধান")


def x3(b):  # R-CHAIN-02: BS shares sum to 3/4
    b.survey_entry("1993-11-20", "RS", [(C, "1")], 33.0, "ধান")
    b.survey_entry("2018-02-09", "BS", [(C, "1/2"), (D, "1/4")], 33.0, "ধান")


def x4(b):  # R-RES-03: acquisition notice
    b.survey_entry("2018-02-09", "BS", [(C, "1")], 33.0, "ধান")
    b.restriction("2025-04-01", "ACQUISITION")


def x5(b):  # R-INT-04: registry shows a sale to D, land records still show C, no LT notice
    b.survey_entry("2018-02-09", "BS", [(C, "1")], 33.0, "ধান")
    b.sale("2025-06-10", C, D, "1", 33.0)


if __name__ == "__main__":
    plot("X-001", "m-gzp-kal-01", "9001", "9001", x1, ["R-OWN-03"])
    plot("X-002", "m-gzp-kal-01", "9002", "9002", x2, ["R-CHAIN-01"])
    plot("X-003", "m-gzp-kal-01", "9003", "9003", x3, ["R-CHAIN-02"])
    plot("X-004", "m-gzp-kal-01", "9004", "9004", x4, ["R-RES-03"])
    plot("X-005", "m-gzp-kal-01", "9005", "9005", x5, ["R-INT-04"])
    print("wrote extra plots")
