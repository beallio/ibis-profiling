import ibis
import polars as pl
from ibis_profiling.logical_types import Age, Gender, LanguageCode, Passport, IbisLogicalTypeSystem


def test_age_detection():
    valid = [25, 30, 0, 120]
    invalid = [-1, 150, 1000]

    ts = IbisLogicalTypeSystem()
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"a": valid})))["a"] == Age
    # Note: invalid ages will still be Integer or Count, not Age
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"a": invalid})))["a"] != Age


def test_gender_detection():
    valid = ["Male", "Female", "M", "F", "Non-binary", "Unknown"]
    invalid = ["just a string", "123", "not-gender"]

    ts = IbisLogicalTypeSystem()
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"g": valid})))["g"] == Gender
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"g": invalid})))["g"] != Gender


def test_language_code_detection():
    valid = ["en", "es", "fr", "de", "zh"]
    invalid = ["english", "USA", "12", "E"]

    ts = IbisLogicalTypeSystem()
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"l": valid})))["l"] == LanguageCode
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"l": invalid})))["l"] != LanguageCode


def test_passport_detection():
    valid = ["A1234567", "123456789", "ZE123456"]
    invalid = ["not-a-passport", "12345", "ABCDEFGHIJKL"]

    ts = IbisLogicalTypeSystem()
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"p": valid})))["p"] == Passport
    assert ts.infer_all_types(ibis.memtable(pl.DataFrame({"p": invalid})))["p"] != Passport
