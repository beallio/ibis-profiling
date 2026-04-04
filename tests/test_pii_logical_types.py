import ibis
import polars as pl
from ibis_profiling.logical_types import CreditCard, SSN, IbisLogicalTypeSystem


def test_credit_card_detection():
    # Valid formats for various brands
    valid_cards = [
        "4111111111111111",  # Visa
        "5105105105105105",  # Mastercard
        "341234567890123",  # Amex
        "6011123456789012",  # Discover
        "4111 1111 1111 1111",  # Visa with spaces
        "5105-1051-0510-5105",  # Mastercard with dashes
    ]

    invalid_cards = [
        "1234567890",  # Too short
        "ABCDEFGHIJKLMN",  # Not numeric
        "41111111111111111",  # Too long
        "9999999999999999",  # Invalid prefix
    ]

    ts = IbisLogicalTypeSystem()

    # Test valid
    df = pl.DataFrame({"cc": valid_cards})
    table = ibis.memtable(df)
    results = ts.infer_all_types(table)
    assert results["cc"] == CreditCard

    # Test invalid (should fall back to Categorical or String)
    df_invalid = pl.DataFrame({"cc": invalid_cards})
    table_invalid = ibis.memtable(df_invalid)
    results_invalid = ts.infer_all_types(table_invalid)
    assert results_invalid["cc"] != CreditCard


def test_ssn_detection():
    valid_ssns = [
        "123-45-6789",
        "123 45 6789",
        "123456789",
        "899-99-9999",
    ]

    invalid_ssns = [
        "000-45-6789",  # Invalid area starts with 0
        "900-45-6789",  # Invalid area starts with 9
        "123-45-678",  # Too short
        "AAA-BB-CCCC",  # Not numeric
    ]

    ts = IbisLogicalTypeSystem()

    # Test valid
    df = pl.DataFrame({"ssn": valid_ssns})
    table = ibis.memtable(df)
    results = ts.infer_all_types(table)
    assert results["ssn"] == SSN

    # Test invalid
    df_invalid = pl.DataFrame({"ssn": invalid_ssns})
    table_invalid = ibis.memtable(df_invalid)
    results_invalid = ts.infer_all_types(table_invalid)
    assert results_invalid["ssn"] != SSN
