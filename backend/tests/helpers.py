"""Shared test helpers. Plain functions only, so tests run under pytest and the local runner."""
from __future__ import annotations

import atexit
import os
import shutil
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


_TEMP_DIRS: list[str] = []


@atexit.register
def _cleanup_temp_dirs() -> None:
    for d in _TEMP_DIRS:
        shutil.rmtree(d, ignore_errors=True)


def temp_dir(prefix: str = "landcheck_") -> str:
    """A temp folder that is deleted when the test run ends (no leftovers in /tmp)."""
    d = tempfile.mkdtemp(prefix=prefix)
    _TEMP_DIRS.append(d)
    return d


def make_db(seed: int = 42):
    """Seeded SQLite DB in a temp dir. Returns an open connection."""
    from app.core import db
    from seed import load
    fresh_key()
    path = os.path.join(temp_dir(), "t.db")
    conn = db.connect(path)
    load.load(conn, seed=seed)
    return conn
