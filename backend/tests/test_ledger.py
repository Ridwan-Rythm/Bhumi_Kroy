"""Ledger tests. test_admin_rehash_is_still_detected answers: 'what stops an admin re-hashing?'"""
import json

from app.ledger import chain, checkpoint, signer
from tests.helpers import make_db

PLOT = "P-001"


def _edit_record(conn, record_id, field, value):
    row = conn.execute("SELECT data_json FROM records WHERE record_id=?", (record_id,)).fetchone()
    data = json.loads(row["data_json"])
    data[field] = value
    conn.execute("UPDATE records SET data_json=? WHERE record_id=?",
                 (signer.canonical(data).decode(), record_id))
    return data


def test_clean_chain_verifies():
    conn = make_db()
    for plot_id in ("P-001", "P-003", "P-009"):
        st = chain.verify(conn, plot_id)
        assert st.ok and st.reason is None and st.broken_at_seq is None
        assert st.height >= 4 and st.checkpoint["height"] == st.height


def test_edit_record_data_is_hash_mismatch():
    conn = make_db()
    e = chain.entries(conn, PLOT)[2]
    _edit_record(conn, e["record_id"], "area_decimal", 99.0)
    st = chain.verify(conn, PLOT)
    assert (st.ok, st.reason, st.broken_at_seq) == (False, "hash_mismatch", e["seq"])


def test_delete_entry_is_link_broken():
    conn = make_db()
    conn.execute("DELETE FROM ledger WHERE plot_id=? AND seq=2", (PLOT,))
    st = chain.verify(conn, PLOT)
    assert (st.ok, st.reason) == (False, "link_broken")


def test_reorder_two_entries_is_link_broken():
    conn = make_db()
    a, b = chain.entries(conn, PLOT)[1], chain.entries(conn, PLOT)[2]
    cols = ("ts", "source", "record_id", "record_hash", "prev_hash", "entry_hash")
    for src, dst_seq in ((a, b["seq"]), (b, a["seq"])):  # swap contents, keep seq numbers
        conn.execute("UPDATE ledger SET %s WHERE plot_id=? AND seq=?" % ",".join(c + "=?" for c in cols),
                     (*[src[c] for c in cols], PLOT, dst_seq))
    st = chain.verify(conn, PLOT)
    assert (st.ok, st.reason) == (False, "link_broken")


def test_swap_checkpoint_signature_is_signature_invalid():
    conn = make_db()
    other = chain.latest_checkpoint(conn, "P-003")["signature_b64"]
    conn.execute("UPDATE checkpoints SET signature_b64=? WHERE plot_id=?", (other, PLOT))
    st = chain.verify(conn, PLOT)
    assert (st.ok, st.reason) == (False, "signature_invalid")


def _rehash_from(conn, plot_id, start_seq):
    """Recompute record hashes and the whole chain, like an admin with DB access but no key."""
    prev = chain.GENESIS if start_seq == 1 else chain.entries(conn, plot_id)[start_seq - 2]["entry_hash"]
    for e in chain.entries(conn, plot_id):
        if e["seq"] < start_seq:
            continue
        data = json.loads(conn.execute("SELECT data_json FROM records WHERE record_id=?",
                                       (e["record_id"],)).fetchone()["data_json"])
        row = dict(e)
        row["record_hash"], row["prev_hash"] = chain.record_hash(data), prev
        row["entry_hash"] = chain.entry_hash(row)
        conn.execute("UPDATE ledger SET record_hash=?, prev_hash=?, entry_hash=? WHERE plot_id=? AND seq=?",
                     (row["record_hash"], row["prev_hash"], row["entry_hash"], plot_id, e["seq"]))
        prev = row["entry_hash"]


def test_admin_rehash_is_still_detected():
    conn = make_db()
    e = chain.entries(conn, PLOT)[1]
    _edit_record(conn, e["record_id"], "area_decimal", 99.0)
    _rehash_from(conn, PLOT, e["seq"])
    # The chain is now internally consistent...
    rows = chain.entries(conn, PLOT)
    assert rows[-1]["entry_hash"] != chain.latest_checkpoint(conn, PLOT)["head_hash"]
    # ...but the head no longer matches the signed checkpoint, and the key was not available to re-sign.
    st = chain.verify(conn, PLOT)
    assert (st.ok, st.reason) == (False, "checkpoint_mismatch")


def test_replayed_older_checkpoint_is_height_mismatch():
    conn = make_db()
    rec = {"record_id": "BNK-9001", "source": "bank", "type": "MORTGAGE", "date": "2026-10-10",
           "mortgagor": {"name": "x", "father": "y"}, "bank_name": "b", "amount_bdt": 1, "status": "ACTIVE"}
    chain.append_record(conn, PLOT, rec, "2026-10-10T00:00:00+06:00")
    new_cp = checkpoint.sign_checkpoint(conn, PLOT)
    assert chain.verify(conn, PLOT).ok
    # attacker removes the newest checkpoint so the older (validly signed) one is "latest" again
    conn.execute("DELETE FROM checkpoints WHERE plot_id=? AND height=?", (PLOT, new_cp["height"]))
    st = chain.verify(conn, PLOT)
    assert (st.ok, st.reason) == (False, "height_mismatch")


def test_legitimate_append_with_new_checkpoint_verifies():
    conn = make_db()
    before = chain.verify(conn, PLOT).height
    rec = {"record_id": "BNK-9002", "source": "bank", "type": "MORTGAGE", "date": "2026-10-10",
           "mortgagor": {"name": "x", "father": "y"}, "bank_name": "b", "amount_bdt": 1, "status": "ACTIVE"}
    e = chain.append_record(conn, PLOT, rec, "2026-10-10T00:00:00+06:00")
    assert e["seq"] == before + 1
    assert not chain.verify(conn, PLOT).ok  # appended but not yet checkpointed
    checkpoint.sign_checkpoint(conn, PLOT)
    st = chain.verify(conn, PLOT)
    assert st.ok and st.height == before + 1


def test_tamper_on_one_plot_does_not_break_another():
    conn = make_db()
    e = chain.entries(conn, PLOT)[0]
    _edit_record(conn, e["record_id"], "area_decimal", 1.0)
    assert not chain.verify(conn, PLOT).ok
    assert chain.verify(conn, "P-002").ok and chain.verify(conn, "P-003").ok


def test_deleting_the_last_entry_is_detected():
    conn = make_db()
    last = chain.entries(conn, PLOT)[-1]["seq"]
    conn.execute("DELETE FROM ledger WHERE plot_id=? AND seq=?", (PLOT, last))
    st = chain.verify(conn, PLOT)
    assert not st.ok and st.reason == "height_mismatch"
