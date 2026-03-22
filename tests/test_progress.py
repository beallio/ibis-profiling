import pytest
import ibis
from ibis_profiling import ProfileReport


@pytest.fixture
def table():
    return ibis.memtable({"id": [1, 2, 3], "val": [1.0, 2.0, 3.0]})


def test_profile_progress_callback(table):
    progress_updates = []

    def on_progress(inc, label=None):
        progress_updates.append((inc, label))

    # We need to update ProfileReport and profile to accept on_progress
    ProfileReport(table, on_progress=on_progress)

    assert len(progress_updates) > 0
    # Total sum should be close to 100
    total_inc = sum(u[0] for u in progress_updates)
    assert 98 <= total_inc <= 102


def test_profile_minimal_progress_callback(table):
    progress_updates = []

    def on_progress(inc, label=None):
        progress_updates.append((inc, label))

    report = ProfileReport(table, minimal=True, on_progress=on_progress)
    del report

    assert len(progress_updates) > 0
    total_inc = sum(u[0] for u in progress_updates)
    assert 98 <= total_inc <= 102
