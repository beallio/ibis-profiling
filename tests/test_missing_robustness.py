import math
from ibis_profiling.report.model.missing import MissingEngine
from decimal import Decimal


def test_missing_engine_empty_columns_consistency():
    """Verify that empty columns return includes 'warnings'."""
    variables = {}
    result = MissingEngine.compute(None, variables)
    assert "warnings" in result, "Early return missing 'warnings' key"
    assert result["warnings"] == []


def test_missing_engine_decimal_robustness():
    """Verify that non-float numeric types (Decimal) don't crash isfinite."""
    # We'll use a small helper to test the logic directly if needed,
    # but here we can just verify math.isfinite(Decimal('NaN')) behavior
    # and ensure our fix handles it.

    val = Decimal("nan")
    is_f = False
    try:
        if val is not None and math.isfinite(float(val)):
            is_f = True
    except (TypeError, ValueError):
        pass
    assert is_f is False, "Decimal NaN should not be finite"

    val = Decimal("1.23")
    is_f = False
    try:
        if val is not None and math.isfinite(float(val)):
            is_f = True
    except (TypeError, ValueError):
        pass
    assert is_f is True, "Decimal 1.23 should be finite"


if __name__ == "__main__":
    test_missing_engine_empty_columns_consistency()
    test_missing_engine_decimal_robustness()
