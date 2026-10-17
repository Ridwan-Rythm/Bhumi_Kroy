from app.ledger import signer
from tests.helpers import fresh_key


def test_sign_verify_roundtrip():
    fresh_key()
    data = signer.canonical({"a": 1, "b": "x"})
    sig = signer.sign(data)
    assert "=" not in sig
    assert signer.verify(data, sig)
    assert not signer.verify(data + b" ", sig)


def test_canonical_stable_regardless_of_key_order():
    assert signer.canonical({"b": 1, "a": 2}) == signer.canonical({"a": 2, "b": 1})
    assert signer.canonical({"a": [1, 2]}) == b'{"a":[1,2]}'


def test_canonical_keeps_bangla_unescaped():
    out = signer.canonical({"name": "রহিম"})
    assert "রহিম".encode("utf-8") in out
    assert b"\\u" not in out


def test_public_key_is_base64url_without_padding():
    fresh_key()
    pk = signer.public_key_b64()
    assert "=" not in pk and len(signer.b64u_decode(pk)) == 32


def test_garbage_signature_does_not_raise():
    fresh_key()
    assert signer.verify(b"x", "not-a-signature!!") is False


def test_signed_sample_fixtures_verify_and_tampered_fails():
    from seed.make_signed_sample import build
    good, bad = build()
    assert signer.verify(signer.b64u_decode(good["payload_b64"]), good["signature_b64"], good["public_key_b64"])
    assert not signer.verify(signer.b64u_decode(bad["payload_b64"]), bad["signature_b64"], bad["public_key_b64"])
