import ibis
import polars as pl
from ibis_profiling.logical_types import USState, USTerritory, USMilitaryMail, IbisLogicalTypeSystem


def test_us_state_detection():
    valid = ["CA", "NY", "TX", "FL", "DC"]
    invalid = ["not-a-state", "California", "12", "ZZ"]

    ts = IbisLogicalTypeSystem()
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"s": valid})))["s"] == USState
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"s": invalid})))["s"] != USState


def test_us_territory_detection():
    valid = ["PR", "VI", "GU", "AS", "MP"]
    invalid = ["US", "CA", "ZZ", "Puerto Rico"]

    ts = IbisLogicalTypeSystem()
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"t": valid})))["t"] == USTerritory
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"t": invalid})))["t"] != USTerritory


def test_us_military_mail_detection():
    valid = ["AA", "AE", "AP"]
    invalid = ["CA", "PR", "ZZ", "APO"]

    ts = IbisLogicalTypeSystem()
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"m": valid})))["m"] == USMilitaryMail
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"m": invalid})))["m"] != USMilitaryMail
