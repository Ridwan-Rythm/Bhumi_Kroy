"""The P-010 demo script (contract section 9), plus verify-state tests."""
import asyncio
import json
import os

from app.core import clock
from app.core.errors import AppError
from app.engine.pipeline import run_check
from app.ledger import signer
from app.services import demo_service as demo
from app.services import verify_service as vs
from tests.helpers import make_db, raises

SAMPLES = {s["sample_id"]: s for s in json.load(open("seed/golden/samples.json", encoding="utf-8"))}
os.environ["DEMO_MODE"] = "1"


def check(conn, sid="P-001"):
    return asyncio.run(run_check(conn, SAMPLES[sid]["request"]))


def test_p010_full_script():
    conn = make_db()
    r1 = check(conn)
    assert r1["verdict"] == "GREEN" and r1["report_id"]
    assert vs.verify(conn, short_code=r1["short_code"])["state"] == "GENUINE_CURRENT"

    led = demo.tamper(conn, "P-001", "edit_field")
    assert led["ok"] is False and led["reason"] == "hash_mismatch"
    assert [e["status"] for e in led["entries"]].count("broken") == 1
    alert = check(conn)
    assert alert["verdict"] == "INTEGRITY_ALERT"
    for k in ("report_id", "short_code", "valid_until", "signed_payload_b64", "signature_b64"):
        assert alert[k] is None
    assert alert["findings"][0]["rule_id"] == "R-INT-01" and alert["coverage"]["Q6"] == "NOT_COVERED"
    assert conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0] == 1  # nothing stored for the alert
    assert vs.verify(conn, short_code=r1["short_code"])["state"] == "INTEGRITY_ALERT"

    demo.reset(conn)
    assert vs.verify(conn, short_code=r1["short_code"])["state"] == "GENUINE_CURRENT"  # R1 survived the reset
    added = demo.add_event(conn, "P-001", "new_mortgage")
    assert added["ok"] and added["added"]["kind"] == "MORTGAGE"
    v = vs.verify(conn, short_code=r1["short_code"])
    assert v["state"] == "GENUINE_SUPERSEDED" and v["signature_valid"] is True
    assert [(d["change"], d["kind"], d["record_ref"]) for d in v["diff"]] == [
        ("ADDED", "MORTGAGE", added["added"]["record_ref"])]
    r2 = check(conn)
    assert r2["verdict"] == "RED" and "R-LIEN-01" in {f["rule_id"] for f in r2["findings"]}


def test_p010_bonus_admin_rehash_gives_checkpoint_mismatch():
    conn = make_db()
    r1 = check(conn)
    led = demo.tamper(conn, "P-001", "edit_and_rehash")
    assert led["reason"] == "checkpoint_mismatch" and led["checkpoint"]["valid"] is False
    assert check(conn)["verdict"] == "INTEGRITY_ALERT"
    v = vs.verify(conn, short_code=r1["short_code"])
    assert v["state"] == "INTEGRITY_ALERT" and v["ledger"]["reason"] == "checkpoint_mismatch"


def test_verify_by_payload_and_flipped_byte_is_tampered():
    conn = make_db()
    r = check(conn)
    ok = vs.verify(conn, payload_b64=r["signed_payload_b64"], signature_b64=r["signature_b64"])
    assert ok["state"] == "GENUINE_CURRENT" and ok["report"]["report_id"] == r["report_id"]
    raw = bytearray(signer.b64u_decode(r["signed_payload_b64"]))
    raw[-5] ^= 1
    bad = vs.verify(conn, payload_b64=signer.b64u(bytes(raw)), signature_b64=r["signature_b64"])
    assert bad["state"] == "TAMPERED" and bad["signature_valid"] is False and bad["report"] is None
    junk = vs.verify(conn, payload_b64="!!!", signature_b64="x")
    assert junk["state"] == "TAMPERED"


def test_verify_unknown_short_code_and_normalisation():
    conn = make_db()
    assert vs.verify(conn, short_code="ZZZZ-ZZZZ")["state"] == "UNKNOWN"
    r = check(conn)
    assert vs.verify(conn, short_code=r["short_code"].lower().replace("-", " "))["state"] == "GENUINE_CURRENT"
    assert raises(AppError, vs.verify, conn).code == "VALIDATION_ERROR"


def test_verify_expired_after_clock_shift():
    conn = make_db()
    r = check(conn)
    later = clock.now().replace(microsecond=0) + __import__("datetime").timedelta(days=8)
    assert vs.verify(conn, short_code=r["short_code"], now=later)["state"] == "GENUINE_EXPIRED"


def test_verify_precedence_tampered_beats_integrity_alert():
    conn = make_db()
    r = check(conn)
    demo.tamper(conn, "P-001", "edit_field")
    raw = bytearray(signer.b64u_decode(r["signed_payload_b64"]))
    raw[-5] ^= 1
    v = vs.verify(conn, payload_b64=signer.b64u(bytes(raw)), signature_b64=r["signature_b64"])
    assert v["state"] == "TAMPERED"


def test_each_required_tamper_kind_is_detected_with_its_reason():
    expect = {"edit_field": "hash_mismatch", "edit_and_rehash": "checkpoint_mismatch",
              "delete_entry": "link_broken", "swap_signature": "signature_invalid", "reorder": "link_broken"}
    for kind, reason in expect.items():
        conn = make_db()
        led = demo.tamper(conn, "P-001", kind)
        assert (led["ok"], led["reason"]) == (False, reason), kind
        assert check(conn)["verdict"] == "INTEGRITY_ALERT"
        assert check(conn, "P-002")["verdict"] != "INTEGRITY_ALERT"  # other plots are unaffected


def test_optional_tamper_kinds_return_not_implemented_and_unknown_is_validation():
    conn = make_db()
    for kind in ("replace_entry", "replay_checkpoint"):
        assert raises(AppError, demo.tamper, conn, "P-001", kind).code == "NOT_IMPLEMENTED"
    assert raises(AppError, demo.tamper, conn, "P-001", "explode").code == "VALIDATION_ERROR"
    assert raises(AppError, demo.tamper, conn, "P-999", "edit_field").code == "NOT_FOUND"


def test_demo_routes_disabled_without_demo_mode():
    conn = make_db()
    os.environ["DEMO_MODE"] = "0"
    try:
        for fn, args in ((demo.tamper, ("P-001", "edit_field")), (demo.reset, ()), (demo.ledger_view, ("P-001",)),
                         (demo.add_event, ("P-001", "new_mortgage")), (demo.set_clock, (1,))):
            e = raises(AppError, fn, *((conn,) + args if fn is not demo.set_clock else args))
            assert e.code == "DEMO_DISABLED" and e.http_status == 404
    finally:
        os.environ["DEMO_MODE"] = "1"


def test_add_event_refuses_to_sign_over_a_tampered_chain():
    conn = make_db()
    demo.tamper(conn, "P-001", "edit_field")
    assert raises(AppError, demo.add_event, conn, "P-001", "new_mortgage").code == "VALIDATION_ERROR"


def test_add_mutation_pending_makes_p001_amber_or_worse():
    conn = make_db()
    demo.add_event(conn, "P-001", "new_mutation_pending")
    r = check(conn)
    assert r["verdict"] == "AMBER" and {f["rule_id"] for f in r["findings"]} >= {"R-DISP-03"}


def test_reset_keeps_reports_and_restores_seeded_state():
    conn = make_db()
    r = check(conn)
    demo.add_event(conn, "P-001", "new_mortgage")
    demo.reset(conn)
    assert conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0] == 1
    assert check(conn)["verdict"] == "GREEN" and r["report_id"]


def test_clock_shift_makes_report_expire():
    conn = make_db()
    r = check(conn)
    try:
        out = demo.set_clock(8)
        assert out["ok"]
        assert vs.verify(conn, short_code=r["short_code"])["state"] == "GENUINE_EXPIRED"
    finally:
        demo.reset(conn)
    assert clock.get_offset_days() == 0
