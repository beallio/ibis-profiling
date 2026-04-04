import ibis
import polars as pl
from ibis_profiling.logical_types import IBAN, IbisLogicalTypeSystem


def test_iban_detection():
    valid = [
        "GB29NWBK60161331926819",  # UK
        "DE89370400440532013000",  # Germany
        "FR7630006000011234567890123",  # France
    ]
    invalid = [
        "not-an-iban",
        "GB29NWBK",  # Too short
        "12345678901234567890",  # No country code
    ]

    ts = IbisLogicalTypeSystem()
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"i": valid})))["i"] == IBAN
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"i": invalid})))["i"] != IBAN
