import ibis
import pandas as pd
from ibis_profiling import ProfileReport


def test_monotonicity_threshold_skipping():
    # 10 rows
    data = {"val": range(10)}
    table = ibis.memtable(pd.DataFrame(data))

    # Threshold < 10, should skip
    # Need to set cardinality_threshold=0 to ensure 'val' is treated as Numeric
    report = ProfileReport(table, monotonicity_threshold=5, cardinality_threshold=0)
    description = report.get_description()

    assert description["variables"]["val"]["monotonic_increasing"] == "Skipped"
    assert description["variables"]["val"]["monotonic_decreasing"] == "Skipped"

    # Verify warning is present
    warnings = description["analysis"].get("warnings", [])
    assert any("Skipped monotonicity checks" in w for w in warnings)


def test_monotonicity_threshold_forcing():
    # 10 rows
    data = {"val": range(10), "id": range(10)}
    table = ibis.memtable(pd.DataFrame(data))

    # Threshold < 10, but monotonicity=True AND order_by is provided, should NOT skip
    report = ProfileReport(
        table,
        monotonicity_threshold=5,
        monotonicity=True,
        monotonicity_order_by="id",
        cardinality_threshold=0,
    )
    description = report.get_description()

    assert description["variables"]["val"]["monotonic_increasing"] is True
    assert description["variables"]["val"]["monotonic_decreasing"] is False


def test_monotonicity_ordering():
    # Data that is monotonic only when ordered by 'id'
    data = [
        {"id": 1, "val": 10},
        {"id": 3, "val": 30},
        {"id": 2, "val": 20},
    ]
    table = ibis.memtable(pd.DataFrame(data))

    # Natural order is 10, 30, 20 -> Skipped if no order_by
    report_natural = ProfileReport(table, monotonicity_order_by=None, cardinality_threshold=0)
    desc_natural = report_natural.get_description()
    assert desc_natural["variables"]["val"]["monotonic_increasing"] == "Skipped"

    # Ordered by ID: 10, 20, 30 -> IS monotonic
    report_ordered = ProfileReport(table, monotonicity_order_by="id", cardinality_threshold=0)
    desc_ordered = report_ordered.get_description()
    assert desc_ordered["variables"]["val"]["monotonic_increasing"] is True


def test_monotonicity_html_skipped_rendering():
    data = {"val": range(10)}
    table = ibis.memtable(pd.DataFrame(data))

    report = ProfileReport(table, monotonicity_threshold=5, cardinality_threshold=0)
    html = report.to_html()

    # Verify "Skipped" is in the HTML
    assert "Skipped" in html
