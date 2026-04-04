import ibis
import polars as pl
from ibis_profiling.logical_types import (
    IBAN,
    SWIFT,
    TaxID,
    ISIN,
    StockTicker,
    IbisLogicalTypeSystem,
)


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


def test_swift_detection():
    valid = [
        "ABCDEFGH",  # 8 chars
        "ABCDEFGH123",  # 11 chars
        "NWBKGB2L",
    ]
    invalid = [
        "ABCD",  # Too short
        "ABCDEFGHIJKLM",  # Too long
        "12345678",  # All numbers
    ]

    ts = IbisLogicalTypeSystem()
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"s": valid})))["s"] == SWIFT
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"s": invalid})))["s"] != SWIFT


def test_taxid_detection():
    valid = ["12-3456789", "98-7654321"]
    invalid = ["123-45-6789", "12-345678", "ABC-DEFG"]

    ts = IbisLogicalTypeSystem()
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"t": valid})))["t"] == TaxID
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"t": invalid})))["t"] != TaxID


def test_isin_detection():
    valid = ["US0378331005", "AU000000BHP4", "GB0002634946"]
    invalid = ["not-an-isin", "US037833100", "ABCDEFGHIJKL"]

    ts = IbisLogicalTypeSystem()
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"isin": valid})))["isin"] == ISIN
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"isin": invalid})))["isin"] != ISIN


def test_stock_ticker_detection():
    valid = ["AAPL", "TSLA", "BTC", "MSFT", "A"]
    invalid = ["aapl", "APPLE123", "THISISTOOLONG"]

    ts = IbisLogicalTypeSystem()
    assert (
        ts.infer_all_types(ibis.memtable(pl.DataFrame({"ticker": valid})))["ticker"] == StockTicker
    )
    assert (
        ts.infer_all_types(ibis.memtable(pl.DataFrame({"ticker": invalid})))["ticker"]
        != StockTicker
    )
