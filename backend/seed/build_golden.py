"""Deterministic builder for the ten golden samples (contract section 9). Synthetic data only.

    python -m seed.build_golden     # (re)writes seed/golden/samples.json
"""
from __future__ import annotations

import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREFIX = {"land_records": "LND", "registry": "REG", "mutation": "MUT", "court": "CRT",
          "khas": "KHS", "bank": "BNK"}

# --- administrative units: real districts and upazilas, INVENTED mouzas and JL numbers ----------
DISTRICTS = [
    ("gazipur", "গাজীপুর", "Gazipur", [
        ("kaliakair", "কালিয়াকৈর", "Kaliakair", [("নয়াপাড়া", "Noyapara", "41"), ("দক্ষিণ চরপাড়া", "Dakshin Charpara", "57")]),
        ("sreepur", "শ্রীপুর", "Sreepur", [("বেলতলী", "Beltoli", "12"), ("উত্তর শিমুলিয়া", "Uttar Shimulia", "33"), ("কাঁঠালবাড়ী", "Kanthalbari", "64")]),
        ("kapasia", "কাপাসিয়া", "Kapasia", [("তারাপুর", "Tarapur", "8"), ("মাঝিপাড়া", "Majhipara", "26")])]),
    ("tangail", "টাঙ্গাইল", "Tangail", [
        ("mirzapur", "মির্জাপুর", "Mirzapur", [("ভবানীগাঁও", "Bhabanigaon", "19"), ("পশ্চিম হাটখোলা", "Paschim Hatkhola", "73")]),
        ("bhuapur", "ভূঞাপুর", "Bhuapur", [("সোনাতলা", "Sonatola", "5"), ("রামপুর কান্দি", "Rampur Kandi", "48"), ("চরবাড়ী", "Charbari", "90")]),
        ("ghatail", "ঘাটাইল", "Ghatail", [("মধুপুর কান্দা", "Madhupur Kanda", "22"), ("বিলপাড়া", "Bilpara", "37")])]),
    ("cumilla", "কুমিল্লা", "Cumilla", [
        ("debidwar", "দেবিদ্বার", "Debidwar", [("শালবন", "Shalban", "14"), ("পূর্ব নয়নপুর", "Purba Noyanpur", "51")]),
        ("burichang", "বুড়িচং", "Burichang", [("কামারগাঁও", "Kamargaon", "30"), ("দক্ষিণ ঘোষপাড়া", "Dakshin Ghoshpara", "68"), ("আমতলী", "Amtoli", "9"), ("নতুন বাজার", "Notun Bazar", "82")]),
        ("chandina", "চান্দিনা", "Chandina", [("বাগমারা", "Bagmara", "17"), ("কাশিনগর", "Kashinagar", "44")])]),
]
BANKS = ["পদ্মা পল্লী ঋণ ব্যাংক", "মেঘনা সমবায় ব্যাংক", "জনকল্যাণ ঋণ ব্যাংক"]


def admin_units() -> list[dict]:
    units, short = [], {"gazipur": "gzp", "tangail": "tng", "cumilla": "cml"}
    for did, dbn, den, upas in DISTRICTS:
        units.append({"id": did, "kind": "district", "parent_id": None, "name_bn": dbn, "name_en": den, "jl_no": None})
        for uid, ubn, uen, mouzas in upas:
            units.append({"id": uid, "kind": "upazila", "parent_id": did, "name_bn": ubn, "name_en": uen, "jl_no": None})
            for i, (mbn, men, jl) in enumerate(mouzas, 1):
                units.append({"id": f"m-{short[did]}-{uid[:3]}-{i:02d}", "kind": "mouza", "parent_id": uid,
                              "name_bn": mbn, "name_en": men, "jl_no": jl})
    return units


# --- names ---------------------------------------------------------------------------------------
def _load_names() -> tuple[list[str], list[str], list[str]]:
    g, s, p = [], [], []
    for line in (HERE / "names_bn.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("G: "):
            g.append(line[3:])
        elif line.startswith("S: "):
            s.append(line[3:])
        elif line.startswith("P: "):
            p.append(line[3:])
    return g, s, p


class NameFactory:
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.given, self.sur, self.pat = _load_names()
        self.used: set[str] = {"করিম", "আবদুল"}

    def person(self) -> dict:
        while True:
            name = f"{self.rng.choice(self.given)} {self.rng.choice(self.sur)}"
            if name not in self.used:
                self.used.add(name)
                break
        fname = f"{self.rng.choice(self.given)} {self.rng.choice(self.sur)}"
        return {"name": name, "father": self.rng.choice(self.pat).format(name=fname)}


class Ids:
    def __init__(self):
        self.n = {k: 0 for k in PREFIX}

    def next(self, source: str) -> str:
        self.n[source] += 1
        return f"{PREFIX[source]}-{self.n[source]:04d}"


def _p(person: dict) -> dict:
    return {"name": person["name"], "father": person["father"]}


class PlotBuilder:
    def __init__(self, plot_id: str, mouza_id: str, khatian_no: str, dag_no: str, ids: Ids):
        self.plot_id, self.mouza_id, self.khatian_no, self.dag_no = plot_id, mouza_id, khatian_no, dag_no
        self.ids, self.records, self.adapters = ids, [], {}

    def _add(self, source: str, rtype: str, date: str, **data) -> str:
        rid = self.ids.next(source)
        self.records.append({"record_id": rid, "source": source, "type": rtype, "date": date, **data})
        return rid

    # land records
    def survey_entry(self, date, survey, holders, area, land_class):
        return self._add("land_records", "SURVEY_ENTRY", date, survey=survey, area_decimal=area,
                         land_class=land_class,
                         holders=[{**_p(p), "share": s} for p, s in holders])

    # registry
    def sale(self, date, seller, buyer, share="1", area=None, mutated_on=None, rtype="SALE"):
        return self._add("registry", rtype, date, **{"from": _p(seller), "to": _p(buyer)}, share=share,
                         area_decimal=area, mutated_on=mutated_on, deed_no=f"D-{date[:4]}-{self.ids.n['registry'] + 1:04d}")

    def gift(self, date, donor, donee, share="1", area=None):
        return self.sale(date, donor, donee, share, area, rtype="GIFT")

    def partition(self, date, note="split of dag"):
        return self._add("registry", "PARTITION", date, note=note)

    def lt_notice(self, date, sale_ref):
        return self._add("registry", "LT_NOTICE", date, sale_ref=sale_ref)

    # mutation
    def inheritance(self, date, deceased, heirs):
        return self._add("mutation", "INHERITANCE", date, **{"from": _p(deceased)},
                         heirs=[{**_p(p), "share": s} for p, s in heirs])

    def mutation_pending(self, date, applicant):
        return self._add("mutation", "MUTATION_PENDING", date, applicant=_p(applicant),
                         case_no=f"M-{date[:4]}-{self.ids.n['mutation'] + 1:04d}")

    # court
    def court_case(self, date, case_ref, court, status="OPEN", linkage="TEXT_MATCH"):
        return self._add("court", "COURT_CASE", date, case_ref=case_ref, court=court, status=status, linkage=linkage)

    # khas / restrictions
    def restriction(self, date, rtype, list_name=None):
        return self._add("khas", rtype, date, list=list_name)

    # bank
    def mortgage(self, date, mortgagor, bank_name, amount_bdt=1500000):
        return self._add("bank", "MORTGAGE", date, mortgagor=_p(mortgagor), bank_name=bank_name,
                         amount_bdt=amount_bdt, status="ACTIVE")

    def mortgage_release(self, date, mortgage_ref):
        return self._add("bank", "MORTGAGE_RELEASE", date, mortgage_ref=mortgage_ref)

    def set_adapter(self, source, **cfg):
        self.adapters.setdefault(source, {}).update(cfg)

    def build(self) -> dict:
        snaps = sorted((r for r in self.records if r["type"] == "SURVEY_ENTRY"), key=lambda r: r["date"])
        cur = snaps[-1]
        return {"plot_id": self.plot_id, "mouza_id": self.mouza_id, "survey": cur["survey"],
                "khatian_no": self.khatian_no, "dag_no": self.dag_no, "area_decimal": cur["area_decimal"],
                "land_class": cur["land_class"], "adapter_config": self.adapters, "records": self.records}


def _chain(b, a, bb, c, area=33.0, cls="ধান", bs_area=None, bs_cls=None):
    """CS holder A -> (inheritance 1985) B -> RS -> (sale 2010) C -> BS."""
    b.survey_entry("1926-03-14", "CS", [(a, "1")], area, cls)
    b.inheritance("1985-07-02", a, [(bb, "1")])
    b.survey_entry("1993-11-20", "RS", [(bb, "1")], area, cls)
    b.sale("2010-05-18", bb, c, "1", area)
    b.survey_entry("2018-02-09", "BS", [(c, "1")], bs_area or area, bs_cls or cls)


# (plot_id, mouza_id, khatian, dag)
LOCATIONS = {
    "P-001": ("m-gzp-kal-01", "1203", "4521"), "P-002": ("m-gzp-sre-02", "877", "2310"),
    "P-003": ("m-gzp-kap-01", "1540", "6104"), "P-004": ("m-tng-mir-01", "322", "918"),
    "P-005": ("m-tng-bhu-02", "2045", "7733"), "P-006": ("m-tng-gha-01", "611", "1457"),
    "P-007": ("m-cml-deb-01", "1388", "5290"), "P-008": ("m-cml-bur-02", "954", "3366"),
    "P-009": ("m-cml-cha-02", "1710", "6841"),
}
DISTRICT_OF = {"gzp": ("gazipur", {"kal": "kaliakair", "sre": "sreepur", "kap": "kapasia"}),
               "tng": ("tangail", {"mir": "mirzapur", "bhu": "bhuapur", "gha": "ghatail"}),
               "cml": ("cumilla", {"deb": "debidwar", "bur": "burichang", "cha": "chandina"})}
DISTRICT_BN = {"gazipur": "গাজীপুর", "tangail": "টাঙ্গাইল", "cumilla": "কুমিল্লা"}

LABELS = {
    "P-001": ("কোনো লাল সংকেত নেই", "Nothing found", "GREEN", "Clean plot"),
    "P-002": ("বিক্রেতা রেকর্ডে মালিক নন", "Seller is not the record holder", "RED", "Seller is not the holder"),
    "P-003": ("বন্ধক ও অপেক্ষমাণ নামজারি", "Mortgage and pending mutation", "RED", "Mortgage + pending mutation"),
    "P-004": ("চলমান মালিকানা মামলা", "Open title suit", "RED", "Open title suit"),
    "P-005": ("খাস জমি", "Khas land", "RED", "Khas land"),
    "P-006": ("দ্বৈত বিক্রয়", "Double sale", "RED", "Double sale"),
    "P-007": ("আয়তন ও শ্রেণিতে অসংগতি", "Area drift and class change", "AMBER", "Area drift + class change"),
    "P-008": ("নামের বানান ভিন্ন, পিতার নাম নেই", "Name variant, no father's name", "AMBER", "Name variant, no father's name"),
    "P-008B": ("একই জমি, পিতার নামসহ", "Same plot, father's name given", "GREEN", "Same plot, father's name given"),
    "P-009": ("অজানা মানে নিশ্চিন্ত নয়", "Unknown is not a pass", "GREY", "Unknown is not safe"),
}


def _location(mouza_id: str) -> tuple[str, str]:
    short, up = mouza_id.split("-")[1], mouza_id.split("-")[2]
    did, upas = DISTRICT_OF[short]
    return did, upas[up]


def build_all(seed: int = 42) -> dict:
    """Deterministic: same seed -> identical output."""
    rng = random.Random(seed)
    names, ids = NameFactory(rng), Ids()
    plots: dict[str, dict] = {}
    seller_input: dict[str, dict] = {}

    def new(pid):
        m, k, d = LOCATIONS[pid]
        return PlotBuilder(pid, m, k, d, ids)

    def std(pid, **kw):
        b = new(pid)
        a, bb, c = names.person(), names.person(), names.person()
        _chain(b, a, bb, c, **kw)
        return b, c

    # P-001 clean
    b, c = std("P-001")
    plots["P-001"] = b
    seller_input["P-001"] = {"name": c["name"], "father_or_husband": c["father"]}
    # P-002 seller is not the holder
    b, c = std("P-002")
    plots["P-002"] = b
    seller_input["P-002"] = {"name": "আবু তাহের চৌধুরী", "father_or_husband": "মৃত সোলায়মান শেখ"}
    # P-003 mortgage + pending mutation by someone else
    b, c = std("P-003")
    b.mortgage("2023-08-15", c, BANKS[0])
    b.mutation_pending("2026-09-20", names.person())
    plots["P-003"] = b
    seller_input["P-003"] = {"name": c["name"], "father_or_husband": c["father"]}
    # P-004 open title suit (TEXT_MATCH)
    b, c = std("P-004")
    b.court_case("2026-06-02", "TS-118/2026", f"যুগ্ম জেলা জজ আদালত, {DISTRICT_BN['tangail']}")
    plots["P-004"] = b
    seller_input["P-004"] = {"name": c["name"], "father_or_husband": c["father"]}
    # P-005 khas
    b, c = std("P-005")
    b.restriction("2019-05-01", "KHAS")
    plots["P-005"] = b
    seller_input["P-005"] = {"name": c["name"], "father_or_husband": c["father"]}
    # P-006 double sale: same seller, same share, overlapping dates; LT notices present
    b, c = std("P-006")
    d1, d2 = names.person(), names.person()
    s1 = b.sale("2024-02-10", c, d1, "1", 33.0)
    s2 = b.sale("2024-03-05", c, d2, "1", 33.0)
    b.lt_notice("2024-02-12", s1)
    b.lt_notice("2024-03-07", s2)
    plots["P-006"] = b
    seller_input["P-006"] = {"name": c["name"], "father_or_husband": c["father"]}
    # P-007 area drift RS 20.0 -> BS 14.5 and class ধান -> বাড়ি, no split / conversion record
    b, c = std("P-007", area=20.0, bs_area=14.5, bs_cls="বাড়ি")
    plots["P-007"] = b
    seller_input["P-007"] = {"name": c["name"], "father_or_husband": c["father"]}
    # P-008 name variant: record holder spelled differently from the typed seller
    b = new("P-008")
    a, bb = names.person(), names.person()
    holder = {"name": "মোহাম্মদ আবদুল করিম", "father": "মৃত রহিম উদ্দিন"}
    _chain(b, a, bb, holder)
    plots["P-008"] = b
    seller_input["P-008"] = {"name": "মোঃ আব্দুল করিম", "father_or_husband": None}
    seller_input["P-008B"] = {"name": "মোঃ আব্দুল করিম", "father_or_husband": holder["father"]}
    # P-009 unknown is not safe: court PARTY_NAME_ONLY (NO_RECORD), bank outage
    b, c = std("P-009")
    b.set_adapter("court", linkage="PARTY_NAME_ONLY")
    b.set_adapter("bank", status="UNAVAILABLE", reason="outage")
    plots["P-009"] = b
    seller_input["P-009"] = {"name": c["name"], "father_or_husband": c["father"]}

    plot_dicts = [plots[k].build() for k in sorted(plots)]
    samples = []
    for sid in ["P-001", "P-002", "P-003", "P-004", "P-005", "P-006", "P-007", "P-008", "P-008B", "P-009"]:
        pid = sid.rstrip("B")
        plot = next(p for p in plot_dicts if p["plot_id"] == pid)
        did, uid = _location(plot["mouza_id"])
        bn, en, verdict, scenario = LABELS[sid]
        sel = {"name": seller_input[sid]["name"]}
        if seller_input[sid].get("father_or_husband"):
            sel["father_or_husband"] = seller_input[sid]["father_or_husband"]
        samples.append({"sample_id": sid, "plot_id": pid, "scenario": scenario, "label_bn": bn, "label_en": en,
                        "expected_verdict": verdict,
                        "request": {"plot": {"district_id": did, "upazila_id": uid, "mouza_id": plot["mouza_id"],
                                             "survey": plot["survey"], "khatian_no": plot["khatian_no"],
                                             "dag_no": plot["dag_no"]},
                                    "seller": sel, "consents": {"bank": True}}})
    return {"admin_units": admin_units(), "plots": plot_dicts, "samples": samples}


def main() -> None:
    out = HERE / "golden" / "samples.json"
    out.write_text(json.dumps(build_all(42)["samples"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
