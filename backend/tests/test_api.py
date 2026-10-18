"""HTTP-level tests (contract section 5): every endpoint, the error shape, rate limit, CORS, P-010."""
import contextlib
import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.ratelimit import limiter
from app.main import create_app
from app.models import DemoLedger, Locations, PubKey, Report, SamplePlot, VerifyResult
from tests.helpers import fresh_key, temp_dir

SAMPLES = {s["sample_id"]: s for s in json.loads(Path("seed/golden/samples.json").read_text(encoding="utf-8"))}
ENV = ("DB_PATH", "DEMO_MODE", "RATE_LIMIT_PER_MIN")


@contextlib.contextmanager
def api_client(demo=True, rate="1000"):
    saved = {k: os.environ.get(k) for k in ENV}
    fresh_key()
    os.environ["DB_PATH"] = os.path.join(temp_dir(), "api.db")
    os.environ["DEMO_MODE"] = "1" if demo else "0"
    os.environ["RATE_LIMIT_PER_MIN"] = rate
    limiter.reset()
    try:
        with TestClient(create_app(), raise_server_exceptions=False) as c:
            yield c
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        limiter.reset()


def err(r, status, code, field=None):
    assert r.status_code == status, (r.status_code, r.text)
    e = r.json()["error"]
    assert set(e) == {"code", "message", "field"}
    assert e["code"] == code, e
    if field is not None:
        assert e["field"] == field, e
    return e


def post_check(c, sid="P-001", **over):
    body = json.loads(json.dumps(SAMPLES[sid]["request"]))
    body.update(over)
    return c.post("/api/v1/check", json=body)


# ---- meta -----------------------------------------------------------------------------------------
def test_health_reports_demo_mode():
    with api_client(demo=True) as c:
        assert c.get("/api/v1/health").json() == {"ok": True, "demo_mode": True}
    with api_client(demo=False) as c:
        assert c.get("/api/v1/health").json() == {"ok": True, "demo_mode": False}


def test_meta_endpoints_have_the_contract_shape():
    with api_client() as c:
        loc = Locations.model_validate(c.get("/api/v1/meta/locations").json())
        assert any(m.jl_no for d in loc.districts for u in d.upazilas for m in u.mouzas)
        samples = c.get("/api/v1/meta/samples").json()
        assert [s["sample_id"] for s in samples] == list(SAMPLES)
        for s in samples:
            SamplePlot.model_validate(s)
        pk = PubKey.model_validate(c.get("/api/v1/meta/pubkey").json())
        assert pk.key_id == "demo-2026-01" and pk.alg == "Ed25519"


def test_every_sample_mouza_exists_in_locations():
    with api_client() as c:
        mouzas = {m["id"] for d in c.get("/api/v1/meta/locations").json()["districts"]
                  for u in d["upazilas"] for m in u["mouzas"]}
        assert {s["request"]["plot"]["mouza_id"] for s in SAMPLES.values()} <= mouzas


# ---- check ----------------------------------------------------------------------------------------
def test_check_returns_200_for_green_and_for_red():
    with api_client() as c:
        green = post_check(c, "P-001")
        assert green.status_code == 200 and green.json()["verdict"] == "GREEN"
        Report.model_validate(green.json())
        red = post_check(c, "P-003")
        assert red.status_code == 200 and red.json()["verdict"] == "RED"
        Report.model_validate(red.json())


def test_check_accepts_bangla_digits():
    with api_client() as c:
        body = json.loads(json.dumps(SAMPLES["P-001"]["request"]))
        body["plot"]["khatian_no"] = body["plot"]["khatian_no"].translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))
        r = c.post("/api/v1/check", json=body)
        assert r.status_code == 200 and r.json()["plot"]["khatian_no"] == SAMPLES["P-001"]["request"]["plot"]["khatian_no"]


def test_check_errors_use_the_contract_shape_and_never_500():
    with api_client() as c:
        err(c.post("/api/v1/check", content=b"{not json", headers={"Content-Type": "application/json"}),
            422, "VALIDATION_ERROR")
        err(c.post("/api/v1/check", json=[1, 2]), 422, "VALIDATION_ERROR")
        err(c.post("/api/v1/check", json={}), 422, "VALIDATION_ERROR", "plot")
        for bad in ([1], "yes", [], {"bank": "no"}):
            err(post_check(c, consents=bad), 422, "VALIDATION_ERROR")
        body = json.loads(json.dumps(SAMPLES["P-001"]["request"]))
        body["plot"]["dag_no"] = "99999"
        err(c.post("/api/v1/check", json=body), 404, "NOT_FOUND", "plot")


def test_integrity_alert_check_is_200_with_null_ids():
    with api_client() as c:
        assert c.post("/demo/tamper", json={"plot_id": "P-001", "kind": "edit_field"}).status_code == 200
        r = post_check(c)
        j = r.json()
        assert r.status_code == 200 and j["verdict"] == "INTEGRITY_ALERT"
        assert all(j[k] is None for k in ("report_id", "short_code", "valid_until", "signed_payload_b64", "signature_b64"))


# ---- reports and verify ---------------------------------------------------------------------------
def test_get_report_returns_the_issued_report_or_404():
    with api_client() as c:
        issued = post_check(c).json()
        got = c.get(f"/api/v1/reports/{issued['report_id']}")
        assert got.status_code == 200 and got.json() == issued
        err(c.get("/api/v1/reports/RPT-0000-000000"), 404, "NOT_FOUND")


def test_verify_by_short_code_and_by_payload():
    with api_client() as c:
        r = post_check(c).json()
        by_code = c.post("/api/v1/verify", json={"short_code": r["short_code"].lower()})
        assert by_code.status_code == 200
        assert VerifyResult.model_validate(by_code.json()).state == "GENUINE_CURRENT"
        by_payload = c.post("/api/v1/verify", json={"payload_b64": r["signed_payload_b64"],
                                                    "signature_b64": r["signature_b64"]}).json()
        assert by_payload["state"] == "GENUINE_CURRENT" and by_payload["signature_valid"] is True
        flipped = r["signed_payload_b64"][:-3] + ("AAA" if not r["signed_payload_b64"].endswith("AAA") else "BBB")
        bad = c.post("/api/v1/verify", json={"payload_b64": flipped, "signature_b64": r["signature_b64"]}).json()
        assert bad["state"] == "TAMPERED"
        assert c.post("/api/v1/verify", json={"short_code": "ZZZZ-ZZZZ"}).json()["state"] == "UNKNOWN"


def test_verify_bad_bodies_are_validation_errors():
    with api_client() as c:
        err(c.post("/api/v1/verify", json={}), 422, "VALIDATION_ERROR")
        err(c.post("/api/v1/verify", json={"short_code": 12}), 422, "VALIDATION_ERROR", "short_code")
        err(c.post("/api/v1/verify", json={"payload_b64": "abc"}), 422, "VALIDATION_ERROR", "signature_b64")


def test_p010_over_http():
    with api_client() as c:
        r1 = post_check(c).json()
        assert r1["verdict"] == "GREEN"
        led = c.post("/demo/tamper", json={"plot_id": "P-001", "kind": "edit_field"})
        DemoLedger.model_validate(led.json())
        assert led.json()["ok"] is False
        assert post_check(c).json()["verdict"] == "INTEGRITY_ALERT"
        assert c.post("/api/v1/verify", json={"short_code": r1["short_code"]}).json()["state"] == "INTEGRITY_ALERT"
        assert c.post("/demo/reset").json() == {"ok": True}
        added = c.post("/demo/add-event", json={"plot_id": "P-001", "kind": "new_mortgage"}).json()
        assert added["ok"] and added["added"]["kind"] == "MORTGAGE"
        v = c.post("/api/v1/verify", json={"short_code": r1["short_code"]}).json()
        assert v["state"] == "GENUINE_SUPERSEDED" and v["diff"][0]["kind"] == "MORTGAGE"
        r2 = post_check(c).json()
        assert r2["verdict"] == "RED" and "R-LIEN-01" in {f["rule_id"] for f in r2["findings"]}
        c.post("/demo/reset")
        c.post("/demo/tamper", json={"plot_id": "P-001", "kind": "edit_and_rehash"})
        assert c.get("/demo/ledger/P-001").json()["reason"] == "checkpoint_mismatch"


# ---- demo gating ----------------------------------------------------------------------------------
def test_demo_endpoints_are_disabled_without_demo_mode():
    with api_client(demo=False) as c:
        for method, path, body in (("post", "/demo/tamper", {"plot_id": "P-001", "kind": "edit_field"}),
                                   ("post", "/demo/add-event", {"plot_id": "P-001", "kind": "new_mortgage"}),
                                   ("post", "/demo/reset", None), ("get", "/demo/ledger/P-001", None),
                                   ("post", "/demo/clock", {"offset_days": 1})):
            err(getattr(c, method)(path, **({"json": body} if body is not None else {})), 404, "DEMO_DISABLED")
        # even before the body is parsed
        err(c.post("/demo/tamper", content=b"nope"), 404, "DEMO_DISABLED")


def test_demo_not_implemented_and_validation_codes():
    with api_client() as c:
        for kind in ("replace_entry", "replay_checkpoint"):
            err(c.post("/demo/tamper", json={"plot_id": "P-001", "kind": kind}), 501, "NOT_IMPLEMENTED")
        err(c.post("/demo/tamper", json={"plot_id": "P-001", "kind": "explode"}), 422, "VALIDATION_ERROR", "kind")
        err(c.post("/demo/tamper", json={"plot_id": "P-999", "kind": "edit_field"}), 404, "NOT_FOUND")
        err(c.post("/demo/clock", json={"offset_days": "x"}), 422, "VALIDATION_ERROR", "offset_days")
        assert c.post("/demo/clock", json={"offset_days": 8}).json()["ok"] is True
        c.post("/demo/reset")


# ---- cross-cutting --------------------------------------------------------------------------------
def test_rate_limit_is_30_per_minute_by_default_and_shared_by_check_and_verify():
    with api_client(rate="30") as c:
        for _ in range(15):
            assert c.post("/api/v1/verify", json={"short_code": "ZZZZ-ZZZZ"}).status_code == 200
        for _ in range(15):
            assert post_check(c, "P-002").status_code == 200
        r = post_check(c, "P-002")
        err(r, 429, "RATE_LIMITED")
        assert r.headers["Retry-After"] == "60"
        err(c.post("/api/v1/verify", json={"short_code": "ZZZZ-ZZZZ"}), 429, "RATE_LIMITED")
        assert c.get("/api/v1/health").status_code == 200  # other endpoints are not limited


def test_cors_allows_the_vite_dev_origin_only():
    with api_client() as c:
        ok = c.options("/api/v1/check", headers={"Origin": "http://localhost:5173",
                                                  "Access-Control-Request-Method": "POST",
                                                  "Access-Control-Request-Headers": "content-type"})
        assert ok.status_code == 200 and ok.headers["access-control-allow-origin"] == "http://localhost:5173"
        other = c.get("/api/v1/health", headers={"Origin": "https://evil.example"})
        assert "access-control-allow-origin" not in other.headers


def test_unknown_route_and_wrong_method_use_the_error_shape():
    with api_client() as c:
        err(c.get("/api/v1/nope"), 404, "NOT_FOUND")
        err(c.get("/api/v1/check"), 404, "NOT_FOUND")


def test_unexpected_crash_is_a_generic_internal_error():
    import app.api.routes as routes
    real = routes.run_check

    async def boom(*a, **k):
        raise RuntimeError("secret database path /srv/x")

    routes.run_check = boom
    try:
        with api_client() as c:
            e = err(post_check(c), 500, "INTERNAL")
            assert "secret" not in e["message"]
    finally:
        routes.run_check = real
