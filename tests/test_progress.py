import ibis
import pandas as pd
from ibis_profiling import ProfileReport


def test_on_progress_callback():
    df = pd.DataFrame({"a": range(100), "b": range(100)})
    table = ibis.memtable(df)

    progress_updates = []

    def on_progress(inc, label=None):
        progress_updates.append((inc, label))

    ProfileReport(table, on_progress=on_progress)

    # Verify that total increments sum to 100
    total_inc = sum(inc for inc, label in progress_updates)
    assert total_inc == 100

    # Verify some key labels are present
    labels = [label for inc, label in progress_updates if label]
    assert any("Executing global aggregates" in label for label in labels)
    assert any("Report complete" in label for label in labels)


def test_performance_metadata():
    df = pd.DataFrame({"a": range(100), "b": range(100)})
    table = ibis.memtable(df)

    report = ProfileReport(table)
    data = report.to_dict()

    perf = data["analysis"].get("performance")
    assert perf is not None
    assert "Global Aggregates" in perf
    assert "Metadata Analysis" in perf
    assert isinstance(perf["Global Aggregates"], float)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
