"""Regenerates frontend/src/mocks/*.json from the REAL API, so mock mode and real mode cannot drift.

    cd backend && python -m scripts.export_mocks

Everything is produced in-process with a throwaway signing key (the same one as
contracts/fixtures/signed_sample*.json), a frozen clock and a seeded short-code generator, so the output
is reproducible and contains no secret. One honest exception: app/namematch is still Nazifa's stub, so
for P-008 and P-008B ONLY the name matcher is replaced by a two-line stand-in that returns what the contract
expects (PROBABLE without a father's name, STRONG with one). The engine, rules, signing and ledger are real.
"""
from __future__ import annotations

import json
import os
import random
import tempfile
from datetime import datetime
from pathlib import Path

from app.ledger import signer

OUT = Path(__file__).resolve().parents[2] / "frontend" / "src" / "mocks"
THROWAWAY_SEED = bytes(range(100, 132))  # same key as contracts/fixtures/signed_sample*.json
FROZEN_NOW = "2026-10-17T10:15:00+06:00"


def _setup_env() -> str:
    tmp = tempfile.mkdtemp(prefix="landcheck_mocks_")
    os.environ.update({"DB_PATH": os.path.join(tmp, "mocks.db"), "DEMO_MODE": "1", "RATE_LIMIT_PER_MIN": "100000",
                       "SIGNING_KEY_B64": signer.b64u(THROWAWAY_SEED)})
    signer.reset_key_cache()
    return tmp


def _write(name: str, data) -> None:
    (OUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    tmp = _setup_env()
    from fastapi.testclient import TestClient

    from app import namematch
    from app.core import clock
    from app.engine import report_builder
    from app.main import create_app

    frozen = datetime.fromisoformat(FROZEN_NOW)
    clock.now = lambda: frozen + __import__("datetime").timedelta(days=clock.get_offset_days())
    rnd = random.Random(7)

    class _Secrets:
        @staticmethod
        def choice(seq):
            return rnd.choice(seq)

    report_builder.secrets = _Secrets

    real_match = namematch.match_name

    def stand_in(seller_name, seller_father, record_name, record_father):
        if seller_name == "মোঃ আব্দুল করিম" and record_name == "মোহাম্মদ আবদুল করিম":
            tier, score = ("STRONG", 0.97) if seller_father else ("PROBABLE", 0.88)
            return {"tier": tier, "score": score, "name_score": score, "father_score": 1.0 if seller_father else None}
        return real_match(seller_name, seller_father, record_name, record_father)

    namematch.match_name = stand_in

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    with TestClient(create_app()) as c:
        _write("locations", c.get("/api/v1/meta/locations").json())
        samples = c.get("/api/v1/meta/samples").json()
        _write("samples", samples)
        _write("pubkey", c.get("/api/v1/meta/pubkey").json())

        reports = {}
        for s in samples:
            r = c.post("/api/v1/check", json=s["request"]).json()
            assert r["verdict"] == s["expected_verdict"], (s["sample_id"], r["verdict"])
            reports[s["sample_id"]] = r
            _write("report_" + s["sample_id"].replace("-", ""), r)
        r1 = reports["P-001"]

        def verify(**body):
            return c.post("/api/v1/verify", json=body).json()

        _write("verify_genuine_current", verify(short_code=r1["short_code"]))
        _write("verify_unknown", verify(short_code="ZZZZ-ZZZZ"))
        flipped = r1["signed_payload_b64"][:-4] + ("AAAA" if not r1["signed_payload_b64"].endswith("AAAA") else "BBBB")
        _write("verify_tampered", verify(payload_b64=flipped, signature_b64=r1["signature_b64"]))
        # superseded: a legitimate new mortgage appears after R1 was issued
        c.post("/demo/add-event", json={"plot_id": "P-001", "kind": "new_mortgage"})
        _write("verify_genuine_superseded", verify(short_code=r1["short_code"]))
        c.post("/demo/reset")
        # expired: 8 days later
        c.post("/demo/clock", json={"offset_days": 8})
        _write("verify_genuine_expired", verify(short_code=r1["short_code"]))
        c.post("/demo/reset")
        _write("demo_ledger", c.get("/demo/ledger/P-001").json())
        # integrity alert: someone edits a record behind the ledger's back
        _write("demo_ledger_tampered", c.post("/demo/tamper", json={"plot_id": "P-001", "kind": "edit_field"}).json())
        _write("verify_integrity_alert", verify(short_code=r1["short_code"]))
        _write("report_integrity", c.post("/api/v1/check", json=samples[0]["request"]).json())
    print(f"wrote {len(list(OUT.glob('*.json')))} fixtures to {OUT} (work dir {tmp})")


if __name__ == "__main__":
    main()
