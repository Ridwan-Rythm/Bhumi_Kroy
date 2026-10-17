from tests.rule_helpers import A, B, C, deed, findings, make_ctx, survey


def restr(rtype, lst=None, rid="KHS-1"):
    return {"record_id": rid, "source": "khas", "type": rtype, "date": "2019-05-01", "list": lst}


def test_res_01_fires_on_khas():
    f = findings(make_ctx({"khas": [restr("KHAS")]}), "R-RES-01")
    assert len(f) == 1 and f[0]["severity"] == "CRITICAL" and f[0]["params"] == {"record_ref": "KHS-1"}


def test_res_01_does_not_fire_without_record():
    assert findings(make_ctx({}), "R-RES-01") == []


def test_res_01_edge_vested_is_not_khas():
    ctx = make_ctx({"khas": [restr("VESTED", "KA")]})
    assert findings(ctx, "R-RES-01") == [] and len(findings(ctx, "R-RES-02")) == 1


def test_res_02_fires_for_ka_kha_and_abandoned():
    for rtype, lst in (("VESTED", "KA"), ("VESTED", "KHA"), ("ABANDONED", "ABANDONED")):
        f = findings(make_ctx({"khas": [restr(rtype, lst)]}), "R-RES-02")
        assert len(f) == 1 and f[0]["params"] == {"list": lst, "record_ref": "KHS-1"}


def test_res_02_does_not_fire_without_record():
    assert findings(make_ctx({}), "R-RES-02") == []


def test_res_02_edge_khas_record_is_not_vested():
    assert findings(make_ctx({"khas": [restr("KHAS")]}), "R-RES-02") == []


def bank(rid="BNK-1", status="ACTIVE"):
    return {"record_id": rid, "source": "bank", "type": "MORTGAGE", "date": "2023-08-15", "mortgagor": C,
            "bank_name": "পদ্মা পল্লী ঋণ ব্যাংক", "amount_bdt": 1, "status": status}


def release(ref):
    return {"record_id": "BNK-9", "source": "bank", "type": "MORTGAGE_RELEASE", "date": "2024-01-01",
            "mortgage_ref": ref}


def test_lien_01_fires_on_active_mortgage():
    f = findings(make_ctx({"bank": [bank()]}), "R-LIEN-01")
    assert len(f) == 1 and f[0]["severity"] == "CRITICAL"
    assert f[0]["params"] == {"lien_ref": "BNK-1", "bank_name": "পদ্মা পল্লী ঋণ ব্যাংক"} and f[0]["evidence"] == ["BNK-1"]


def test_lien_01_does_not_fire_when_released():
    assert findings(make_ctx({"bank": [bank(), release("BNK-1")]}), "R-LIEN-01") == []


def test_lien_01_edge_two_liens_one_released():
    f = findings(make_ctx({"bank": [bank("BNK-1"), bank("BNK-2"), release("BNK-1")]}), "R-LIEN-01")
    assert [x["params"]["lien_ref"] for x in f] == ["BNK-2"]


BASE = [survey("LND-1", "2018-01-01", "BS", [(A, "1")])]


def test_sale_01_fires_on_same_seller_same_share_overlapping_dates():
    reg = [deed("REG-1", "2024-02-10", A, B), deed("REG-2", "2024-03-05", A, C)]
    f = findings(make_ctx({"land_records": BASE, "registry": reg}), "R-SALE-01")
    assert len(f) == 1 and f[0]["severity"] == "CRITICAL"
    assert f[0]["params"] == {"deed_a": "REG-1", "deed_b": "REG-2", "overlap": "1"}


def test_sale_01_does_not_fire_on_a_to_b_to_c():
    reg = [deed("REG-1", "2024-02-10", A, B), deed("REG-2", "2024-03-05", B, C)]
    assert findings(make_ctx({"land_records": BASE, "registry": reg}), "R-SALE-01") == []


def test_sale_01_edge_two_half_shares_are_not_overlapping():
    reg = [deed("REG-1", "2024-02-10", A, B, "1/2"), deed("REG-2", "2024-03-05", A, C, "1/2")]
    assert findings(make_ctx({"land_records": BASE, "registry": reg}), "R-SALE-01") == []


def test_sale_01_edge_second_sale_after_first_was_mutated_is_not_a_double_sale():
    reg = [deed("REG-1", "2024-02-10", A, B, mutated_on="2024-02-20"), deed("REG-2", "2024-03-05", A, C)]
    assert findings(make_ctx({"land_records": BASE, "registry": reg}), "R-SALE-01") == []
