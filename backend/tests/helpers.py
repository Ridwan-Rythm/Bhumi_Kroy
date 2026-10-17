"""Shared test helpers. Plain functions only, so tests run under pytest and the local runner."""
from __future__ import annotations

import os
import tempfile


class SkipTest(Exception):
    pass


def skip(reason: str):
    try:
        import pytest
    except ImportError:
        raise SkipTest(reason)
    pytest.skip(reason)


def raises(exc_type, fn, *args, **kwargs):
    """Return the raised exception, or fail if nothing (or the wrong thing) was raised."""
    try:
        fn(*args, **kwargs)
    except exc_type as e:
        return e
    raise AssertionError(f"expected {exc_type.__name__} to be raised")


def fresh_key():
    """Deterministic throwaway key for tests (never the real one)."""
    from app.ledger import signer
    os.environ["SIGNING_KEY_B64"] = signer.b64u(bytes(range(32)))
    signer.reset_key_cache()


def make_db(seed: int = 42):
    """Seeded SQLite DB in a temp dir. Returns an open connection."""
    from app.core import db
    from seed import load
    fresh_key()
    path = os.path.join(tempfile.mkdtemp(prefix="landcheck_"), "t.db")
    conn = db.connect(path)
    load.load(conn, seed=seed)
    return conn
