"""Canonical JSON and Ed25519 signing (contract section 7). Library crypto only."""
from __future__ import annotations

import base64
import contextlib
import json
import os
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

KEY_ID = "demo-2026-01"
_DEFAULT_KEY_PATH = Path(__file__).resolve().parents[2] / ".keys" / "ed25519.key"
_cached: Ed25519PrivateKey | None = None


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64u_decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _raw(key: Ed25519PrivateKey) -> bytes:
    return key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                             serialization.NoEncryption())


def load_or_create_key() -> Ed25519PrivateKey:
    """Env SIGNING_KEY_B64 (32-byte seed, base64url) wins; else persist a generated key."""
    global _cached
    if _cached is not None:
        return _cached
    env = os.environ.get("SIGNING_KEY_B64")
    if env:
        _cached = Ed25519PrivateKey.from_private_bytes(b64u_decode(env.strip()))
        return _cached
    path = Path(os.environ.get("SIGNING_KEY_PATH", _DEFAULT_KEY_PATH))
    if path.exists():
        _restrict(path)
        _cached = Ed25519PrivateKey.from_private_bytes(b64u_decode(path.read_text().strip()))
    else:
        _cached = Ed25519PrivateKey.generate()
        _write_private(path, b64u(_raw(_cached)))
    return _cached


def _write_private(path: Path, text: str) -> None:
    """Create the key file readable and writable by the owner only (0600, folder 0700)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.suppress(OSError):  # not our folder (shared path): the 0600 file mode still protects it
        path.parent.chmod(0o700)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(text)


def _restrict(path: Path) -> None:
    """Tighten a key file that an older version created world-readable (best effort; no-op on Windows)."""
    try:
        if path.stat().st_mode & 0o077:
            path.chmod(0o600)
    except OSError:
        pass


def reset_key_cache() -> None:
    global _cached
    _cached = None


def sign(data: bytes) -> str:
    return b64u(load_or_create_key().sign(data))


def public_key_b64() -> str:
    pub = load_or_create_key().public_key()
    return b64u(pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw))


def verify(data: bytes, signature_b64: str, public_key: str | None = None) -> bool:
    try:
        pub = Ed25519PublicKey.from_public_bytes(b64u_decode(public_key or public_key_b64()))
        pub.verify(b64u_decode(signature_b64), data)
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False
