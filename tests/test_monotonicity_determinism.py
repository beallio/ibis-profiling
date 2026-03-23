import ibis
import pandas as pd
from ibis_profiling import ProfileReport


def test_monotonicity_skips_without_order_by():
    """Test that monotonicity checks are skipped when no order_by column is provided."""
    data = {"val": [1, 2, 3, 4, 5], "id": [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data)
    table = ibis.memtable(df)

    # Run profile without order_by
    # We force monotonicity=True to bypass threshold skipping
    report = ProfileReport(
        table, monotonicity=True, monotonicity_order_by=None, cardinality_threshold=0
    )
    desc = report.get_description()

    # Should be "Skipped" for determinism
    assert desc["variables"]["val"]["monotonic_increasing"] == "Skipped"
    assert desc["variables"]["val"]["monotonic_decreasing"] == "Skipped"

    # Verify warning is present
    warnings = desc["analysis"].get("warnings", [])
    assert any("monotonicity_order_by" in w or "monotonicity order" in w.lower() for w in warnings)


def test_monotonicity_runs_with_order_by():
    """Test that monotonicity checks run when an order_by column is provided."""
    data = {"val": [1, 2, 3, 4, 5], "id": [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data)
    table = ibis.memtable(df)

    # Run profile WITH order_by
    report = ProfileReport(
        table, monotonicity=True, monotonicity_order_by="id", cardinality_threshold=0
    )
    desc = report.get_description()

    # Should NOT be "Skipped"
    assert desc["variables"]["val"]["monotonic_increasing"] is True
    assert desc["variables"]["val"]["monotonic_decreasing"] is False
