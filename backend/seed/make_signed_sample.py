"""Writes contracts/fixtures/signed_sample*.json using a THROWAWAY key (not the real one).

Run from backend/:  python -m seed.make_signed_sample
"""
from __future__ import annotations

import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from app.ledger.signer import KEY_ID, b64u, canonical

FIXTURES = Path(__file__).resolve().parents[2] / "contracts" / "fixtures"
THROWAWAY_SEED = bytes(range(100, 132))  # fixed so the fixture is stable; NOT the real key


def build() -> tuple[dict, dict]:
    key = Ed25519PrivateKey.from_private_bytes(THROWAWAY_SEED)
    pub = b64u(key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw))
    payload = {
        "v": 1, "report_id": "RPT-2026-000123", "short_code": "K7M2-9QXA", "plot_id": "P-001",
        "verdict": "GREEN", "issued_at": "2026-10-17T10:15:00+06:00",
        "valid_until": "2026-10-24T10:15:00+06:00", "ledger_height": 5,
        "ledger_head": "sha256:" + "ab" * 32, "findings_hash": "sha256:" + "cd" * 32, "key_id": KEY_ID,
    }
    raw = canonical(payload)
    sig = b64u(key.sign(raw))
    good = {"note": "sample_only", "payload_json": payload, "payload_b64": b64u(raw),
            "signature_b64": sig, "public_key_b64": pub, "key_id": KEY_ID}
    bad_bytes = bytearray(raw)
    bad_bytes[-3] ^= 0x01  # flip one byte, keep the same signature
    bad = dict(good, payload_b64=b64u(bytes(bad_bytes)))
    bad.pop("payload_json")
    bad["note"] = "sample_only_tampered"
    return good, bad


def main() -> None:
    good, bad = build()
    FIXTURES.mkdir(parents=True, exist_ok=True)
    (FIXTURES / "signed_sample.json").write_text(json.dumps(good, indent=2, ensure_ascii=False) + "\n")
    (FIXTURES / "signed_sample_tampered.json").write_text(json.dumps(bad, indent=2, ensure_ascii=False) + "\n")
    print("wrote", FIXTURES)


if __name__ == "__main__":
    main()
