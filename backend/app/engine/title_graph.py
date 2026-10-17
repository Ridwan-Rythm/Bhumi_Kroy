"""Title graph: replay ownership events into a share table, plus invariants I1, I2, I4, I5, I7.

Works on the raw records the adapters returned. All share arithmetic uses fractions.Fraction.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from fractions import Fraction

TIMELINE_KINDS = {"SURVEY_ENTRY", "SALE", "GIFT", "INHERITANCE", "PARTITION", "COURT_DECREE", "ACQUISITION",
                  "MORTGAGE", "MORTGAGE_RELEASE", "LT_NOTICE", "MUTATION_PENDING", "MUTATION_APPLIED"}
DEED_TYPES = ("SALE", "GIFT")
OWNERSHIP_TYPES = ("SURVEY_ENTRY", "SALE", "GIFT", "INHERITANCE")


def frac(text) -> Fraction:
    return Fraction(str(text))


def frac_text(f: Fraction) -> str:
    return str(f)


def mask_name(name: str | None) -> str | None:
    """Keep the first letter of each token (with its combining marks); mask the rest."""
    if not name:
        return None
    out = []
    for token in name.split():
        i = 1
        while i < len(token) and unicodedata.category(token[i]).startswith("M"):
            i += 1
        rest = sum(1 for ch in token[i:] if not unicodedata.category(ch).startswith("M"))
        out.append(token[:i] + "*" * rest)
    return " ".join(out)


def key(person: dict) -> tuple:
    return (person["name"], person.get("father"))


@dataclass
class Anomaly:
    kind: str            # OVERSELL | SHARE_SUM | GENERATION_UNEXPLAINED
    record_ref: str
    detail: dict = field(default_factory=dict)


@dataclass
class DoubleSale:
    deed_a: str
    deed_b: str
    overlap: Fraction


class TitleGraph:
    def __init__(self, records: list[dict]):
        self.records = sorted(records, key=lambda r: (r.get("date", ""), r["record_id"]))
        self.snapshots = [r for r in self.records if r["type"] == "SURVEY_ENTRY"]
        self.current_holders: list[dict] = []
        if self.snapshots:
            last = self.snapshots[-1]
            self.current_holders = [{**h, "share": frac(h["share"])} for h in last["holders"]]
        self.anomalies: list[Anomaly] = []
        self.double_sales: list[DoubleSale] = []
        self.final_table: dict[tuple, Fraction] = {}
        self._replay()

    # -- replay -----------------------------------------------------------------------------------
    def _replay(self) -> None:
        events = [r for r in self.records if r["type"] in OWNERSHIP_TYPES]
        events.sort(key=lambda r: (r["date"], 1 if r["type"] == "SURVEY_ENTRY" else 0, r["record_id"]))
        table: dict[tuple, Fraction] = {}
        started = False
        sold_by: dict[tuple, list[dict]] = {}
        for ev in events:
            t = ev["type"]
            if t == "SURVEY_ENTRY":
                snap = {key(h): frac(h["share"]) for h in ev["holders"]}
                total = sum(snap.values(), Fraction(0))
                if total != 1:
                    self.anomalies.append(Anomaly("SHARE_SUM", ev["record_id"], {"share_sum": total}))
                if started and table != snap:
                    self.anomalies.append(Anomaly("GENERATION_UNEXPLAINED", ev["record_id"], {}))
                table, started = dict(snap), True
            elif not started:
                continue
            elif t in DEED_TYPES:
                k, s = key(ev["from"]), frac(ev["share"])
                held = table.get(k, Fraction(0))
                if t == "SALE":
                    for prior in sold_by.get(k, []):
                        window_open = prior["mutated_on"] is None or ev["date"] < prior["mutated_on"]
                        overlap = prior["share"] + s - prior["held"]
                        if window_open and overlap > 0:
                            self.double_sales.append(DoubleSale(prior["id"], ev["record_id"], min(overlap, s)))
                    sold_by.setdefault(k, []).append({"id": ev["record_id"], "share": s, "held": held,
                                                      "mutated_on": ev.get("mutated_on")})
                if s > held:
                    self.anomalies.append(Anomaly("OVERSELL", ev["record_id"], {
                        "seller_share": held, "selling_share": s, "date": ev["date"]}))
                _set(table, k, max(held - s, Fraction(0)))
                _set(table, key(ev["to"]), table.get(key(ev["to"]), Fraction(0)) + s)
            elif t == "INHERITANCE":
                k = key(ev["from"])
                held = table.get(k, Fraction(0))
                given = sum((frac(h["share"]) for h in ev["heirs"]), Fraction(0))
                _set(table, k, max(held - given, Fraction(0)))
                for h in ev["heirs"]:
                    _set(table, key(h), table.get(key(h), Fraction(0)) + frac(h["share"]))
        self.final_table = table

    # -- helpers used by rules --------------------------------------------------------------------
    def of_type(self, *types: str) -> list[dict]:
        return [r for r in self.records if r["type"] in types]

    @property
    def depth(self) -> int:
        return len(self.snapshots)

    def last_transfer_date(self) -> str:
        dates = [r["date"] for r in self.of_type("SALE", "GIFT", "INHERITANCE")]
        return max(dates) if dates else ""

    def explained_between(self, d1: str, d2: str) -> bool:
        """A recorded split (PARTITION) or ACQUISITION between two survey dates explains area changes."""
        return any(d1 <= r["date"] <= d2 for r in self.of_type("PARTITION", "ACQUISITION"))

    def area_drifts(self) -> list[dict]:
        out = []
        for a, b in zip(self.snapshots, self.snapshots[1:]):
            if not a.get("area_decimal"):
                continue
            pct = abs(b["area_decimal"] - a["area_decimal"]) / a["area_decimal"] * 100
            out.append({"from_survey": a["survey"], "to_survey": b["survey"], "from_area": a["area_decimal"],
                        "to_area": b["area_decimal"], "drift_pct": round(pct, 1), "record_ref": b["record_id"],
                        "explained": self.explained_between(a["date"], b["date"])})
        return out

    def class_changes(self) -> list[dict]:
        out = []
        for a, b in zip(self.snapshots, self.snapshots[1:]):
            if a["land_class"] != b["land_class"]:
                out.append({"from_class": a["land_class"], "to_class": b["land_class"], "record_ref": b["record_id"],
                            "explained": self.explained_between(a["date"], b["date"])})
        return out

    # -- contract timeline ------------------------------------------------------------------------
    def timeline(self) -> list[dict]:
        out = []
        for r in self.records:
            kind = r["type"]
            if kind not in TIMELINE_KINDS:
                continue
            frm = to = share = area = survey = None
            if kind == "SURVEY_ENTRY":
                to = ", ".join(mask_name(h["name"]) for h in r["holders"])
                area, survey = r.get("area_decimal"), r.get("survey")
            elif kind in DEED_TYPES:
                frm, to = mask_name(r["from"]["name"]), mask_name(r["to"]["name"])
                share, area = frac_text(frac(r["share"])), r.get("area_decimal")
            elif kind == "INHERITANCE":
                frm = mask_name(r["from"]["name"])
                to = ", ".join(mask_name(h["name"]) for h in r["heirs"])
            elif kind == "MORTGAGE":
                frm, to = mask_name(r["mortgagor"]["name"]), r["bank_name"]
            elif kind == "MUTATION_PENDING":
                to = mask_name(r["applicant"]["name"])
            out.append({"date": r["date"], "kind": kind, "survey": survey, "from_masked": frm, "to_masked": to,
                        "share": share, "area_decimal": area, "record_ref": r["record_id"],
                        "source": r["source"], "flagged_by": []})
        return out


def _set(table: dict, k: tuple, v: Fraction) -> None:
    if v == 0:
        table.pop(k, None)
    else:
        table[k] = v
