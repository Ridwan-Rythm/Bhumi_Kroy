from tests.rule_helpers import A, C, findings, make_ctx, survey


def two(a1, a2, c1="ধান", c2="ধান"):
    return {"land_records": [survey("LND-1", "1993-01-01", "RS", [(A, "1")], a1, c1),
                             survey("LND-2", "2018-01-01", "BS", [(C, "1")], a2, c2)]}


def test_chain_03_high_above_10_percent():
    f = findings(make_ctx(two(20.0, 14.5)), "R-CHAIN-03")
    assert len(f) == 1 and f[0]["severity"] == "HIGH" and f[0]["evidence"] == ["LND-2"]
    assert f[0]["params"] == {"from_survey": "RS", "to_survey": "BS", "from_area": 20.0, "to_area": 14.5,
                              "drift_pct": 27.5}


def test_chain_03_ignored_up_to_3_percent():
    assert findings(make_ctx(two(100.0, 97.0)), "R-CHAIN-03") == []
    assert findings(make_ctx(two(33.0, 33.0)), "R-CHAIN-03") == []


def test_chain_03_edge_medium_between_3_and_10_percent_and_10_is_medium():
    assert findings(make_ctx(two(100.0, 95.0)), "R-CHAIN-03")[0]["severity"] == "MEDIUM"
    assert findings(make_ctx(two(100.0, 90.0)), "R-CHAIN-03")[0]["severity"] == "MEDIUM"
    assert findings(make_ctx(two(100.0, 89.0)), "R-CHAIN-03")[0]["severity"] == "HIGH"


def test_chain_03_edge_recorded_partition_or_acquisition_explains_the_drift():
    part = {"record_id": "REG-1", "source": "registry", "type": "PARTITION", "date": "2005-01-01", "note": "split"}
    acq = {"record_id": "KHS-1", "source": "khas", "type": "ACQUISITION", "date": "2005-01-01", "list": None}
    for key, rec in (("registry", part), ("khas", acq)):
        recs = {**two(20.0, 14.5), key: [rec]}
        assert findings(make_ctx(recs), "R-CHAIN-03") == []


def test_chain_04_fires_on_class_change():
    f = findings(make_ctx(two(33.0, 33.0, "ধান", "বাড়ি")), "R-CHAIN-04")
    assert len(f) == 1 and f[0]["severity"] == "MEDIUM" and f[0]["params"] == {"from_class": "ধান", "to_class": "বাড়ি"}


def test_chain_04_does_not_fire_when_class_is_unchanged():
    assert findings(make_ctx(two(33.0, 33.0)), "R-CHAIN-04") == []


def test_chain_04_edge_single_survey_has_nothing_to_compare():
    assert findings(make_ctx({"land_records": [survey("LND-1", "2018-01-01", "BS", [(C, "1")])]}), "R-CHAIN-04") == []


def test_info_02_depth_and_info_03_last_transfer_date():
    recs = {**two(33.0, 33.0), "registry": [{"record_id": "REG-1", "source": "registry", "type": "SALE",
            "date": "2010-05-18", "from": A, "to": C, "share": "1", "area_decimal": None, "mutated_on": None}]}
    ctx = make_ctx(recs)
    assert findings(ctx, "R-INFO-02")[0]["params"] == {"depth": 2}
    assert findings(ctx, "R-INFO-03")[0]["params"] == {"last_transfer_date": "2010-05-18"}


def test_info_02_03_edge_no_survey_no_info_and_no_transfer_gives_empty_date():
    assert findings(make_ctx({}), "R-INFO-02") == [] and findings(make_ctx({}), "R-INFO-03") == []
    one = make_ctx({"land_records": [survey("LND-1", "2018-01-01", "BS", [(C, "1")])]})
    assert findings(one, "R-INFO-03")[0]["params"] == {"last_transfer_date": ""}
