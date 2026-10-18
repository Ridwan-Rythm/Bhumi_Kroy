"""Regression tests for the review findings: rolled-back ledger, unchecked ledger_head, malformed
consents, loose short codes, report_id collisions, key-file mode and samples.json drift."""
import asyncio
import json
import os
import sqlite3
import stat
import sys
from pathlib import Path

from app.core import db
from app.core.errors import AppError
from app.engine import report_builder
from app.engine.pipeline import normalize_request, run_check
from app.ledger import signer
from app.services import demo_service as demo
from app.services import verify_service as vs
from seed import build_golden
from tests.helpers import make_db, raises, temp_dir

SAMPLES = {s["sample_id"]: s for s in json.loads(Path("seed/golden/samples.json").read_text(encoding="utf-8"))}
os.environ["DEMO_MODE"] = "1"


def check(conn, sid="P-001"):
    return asyncio.run(run_check(conn, SAMPLES[sid]["request"]))


# ---- 27: a rolled-back ledger must not verify as current ------------------------------------------
def test_rolled_back_ledger_is_an_integrity_alert():
    conn = make_db()
    demo.add_event(conn, "P-001", "new_mortgage")
    r2 = check(conn)  # pins the new, higher height
    height = r2["ledger"]["height"]
    # Roll back: drop the newest entry AND the checkpoints that pointed at it. chain.verify() is happy.
    conn.execute("DELETE FROM ledger WHERE plot_id='P-001' AND seq=?", (height,))
    conn.execute("DELETE FROM checkpoints WHERE plot_id='P-001' AND height>=?", (height,))
    conn.commit()
    from app.ledger import chain
    assert chain.verify(conn, "P-001").ok is True  # this is why the pinned height must be compared
    v = vs.verify(conn, short_code=r2["short_code"])
    assert v["state"] == "INTEGRITY_ALERT"
    assert v["ledger"] == {"ok": False, "broken_at_seq": None, "reason": "height_mismatch"}


def test_report_pinned_at_current_height_still_verifies():
    conn = make_db()
    r = check(conn)
    assert vs.verify(conn, short_code=r["short_code"])["state"] == "GENUINE_CURRENT"


# ---- 28: ledger_head in the signed payload is compared with the chain -----------------------------
def test_different_history_with_same_height_is_an_integrity_alert():
    conn = make_db(seed=42)
    r = check(conn)
    other = make_db(seed=7)  # same plots and heights, different history
    v = vs.verify(other, payload_b64=r["signed_payload_b64"], signature_b64=r["signature_b64"])
    assert v["state"] == "INTEGRITY_ALERT"
    assert v["ledger"]["reason"] == "checkpoint_mismatch"


def test_reset_with_the_same_seed_keeps_old_reports_valid():
    conn = make_db()
    r = check(conn)
    demo.reset(conn)
    assert vs.verify(conn, short_code=r["short_code"])["state"] == "GENUINE_CURRENT"


# ---- 29: malformed consents / father are validation errors, never a 500 ---------------------------
def _req(**over):
    base = {"plot": {"district_id": "d", "upazila_id": "u", "mouza_id": "m", "khatian_no": "1", "dag_no": "2"},
            "seller": {"name": "x"}}
    base.update(over)
    return base


def test_malformed_consents_are_validation_errors():
    for bad in ([1], "yes", [], 5, {"bank": "yes"}, {"bank": 1}):
        e = raises(AppError, normalize_request, _req(consents=bad))
        assert e.code == "VALIDATION_ERROR" and e.field.startswith("consents"), bad


def test_consents_default_to_bank_true_when_absent_or_null():
    assert normalize_request(_req())["consents"] == {"bank": True}
    assert normalize_request(_req(consents=None))["consents"] == {"bank": True}
    assert normalize_request(_req(consents={}))["consents"] == {"bank": True}
    assert normalize_request(_req(consents={"bank": False}))["consents"] == {"bank": False}


def test_non_string_father_is_rejected_not_dropped():
    r = _req()
    r["seller"]["father_or_husband"] = 42
    assert raises(AppError, normalize_request, r).field == "seller.father_or_husband"


def test_unhashable_survey_is_a_validation_error():
    r = _req()
    r["plot"]["survey"] = ["BS"]
    assert raises(AppError, normalize_request, r).field == "plot.survey"


# ---- 30: short codes are matched strictly ---------------------------------------------------------
def test_short_code_normalisation_is_strict():
    n = report_builder.normalize_short_code
    assert n("k7m2-9qxa") == "K7M29QXA"
    assert n(" K7M2 9QXA ") == "K7M29QXA"
    assert n("K7M29QXA") == "K7M29QXA"
    for bad in ("K7M2-9QXA0000", "K7M2 9 Q XA", "K7M2-9QXI", "K7M2-9QX", "", "K7M2--9QXA", "K7M2_9QXA", None, 12):
        assert n(bad) is None, bad


def test_padded_or_noisy_short_code_does_not_resolve():
    conn = make_db()
    r = check(conn)
    raw = r["short_code"].replace("-", "")
    assert vs.verify(conn, short_code=raw)["state"] == "GENUINE_CURRENT"
    assert vs.verify(conn, short_code=raw + "0000")["state"] == "UNKNOWN"
    noisy = raw[:4] + " i o " + raw[4:]
    assert vs.verify(conn, short_code=noisy)["state"] == "UNKNOWN"


# ---- 31: report_id never collides -----------------------------------------------------------------
def test_two_connections_never_issue_the_same_report_id():
    path = os.path.join(temp_dir(), "c.db")
    from seed import load
    from tests.helpers import fresh_key
    fresh_key()
    c1, c2 = db.connect(path), db.connect(path)
    load.load(c1)
    ids = set()
    for _ in range(3):
        for c in (c1, c2):
            ids.add(check(c)["report_id"])
    assert len(ids) == 6


def test_report_id_survives_a_gap_in_the_table():
    conn = make_db()
    for _ in range(3):
        check(conn)
    conn.execute("DELETE FROM reports WHERE report_id LIKE '%000002'")
    conn.commit()
    ids = [row[0] for row in conn.execute("SELECT report_id FROM reports")]
    new = check(conn)["report_id"]
    assert new not in ids and new.endswith("000004")


def test_issue_retries_when_another_writer_takes_the_id():
    conn = make_db()
    real = report_builder.new_report_id
    calls = []

    def racing(c, now, skip=0):
        rid = real(c, now, skip)
        if not calls:  # first attempt: another writer grabs this id just before our INSERT
            calls.append(rid)
            c.execute("INSERT INTO reports VALUES (?,?,?,?,?)", (rid, "ZZZZ-ZZZZ", "P-001", "{}", "x"))
        return rid

    report_builder.new_report_id = racing
    try:
        r = check(conn)
    finally:
        report_builder.new_report_id = real
    assert r["report_id"] != calls[0]


# ---- 32: the private key is not world-readable ----------------------------------------------------
def test_new_signing_key_file_is_owner_only():
    if sys.platform.startswith("win"):
        return
    folder = temp_dir()
    path = os.path.join(folder, "sub", "ed25519.key")
    saved = {k: os.environ.pop(k, None) for k in ("SIGNING_KEY_B64", "SIGNING_KEY_PATH")}
    os.environ["SIGNING_KEY_PATH"] = path
    signer.reset_key_cache()
    try:
        signer.load_or_create_key()
        assert stat.S_IMODE(os.stat(path).st_mode) == 0o600
        assert stat.S_IMODE(os.stat(os.path.dirname(path)).st_mode) == 0o700
        os.chmod(path, 0o644)  # an older version left it like this
        signer.reset_key_cache()
        signer.load_or_create_key()
        assert stat.S_IMODE(os.stat(path).st_mode) == 0o600
    finally:
        os.environ.pop("SIGNING_KEY_PATH", None)
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v
        signer.reset_key_cache()


# ---- 33: samples.json is exactly what the builder produces ----------------------------------------
def test_samples_json_matches_the_builder():
    built = build_golden.build_all(42)["samples"]
    assert built == json.loads(Path("seed/golden/samples.json").read_text(encoding="utf-8")), \
        "seed/golden/samples.json is stale: run `cd backend && python -m seed.build_golden`"


def test_sqlite_integrity_error_is_what_the_retry_relies_on():
    conn = make_db()
    conn.execute("INSERT INTO reports VALUES ('A','S-1','P-001','{}','x')")
    try:
        conn.execute("INSERT INTO reports VALUES ('A','S-2','P-001','{}','x')")
    except sqlite3.IntegrityError:
        return
    raise AssertionError("reports.report_id must be a PRIMARY KEY")
