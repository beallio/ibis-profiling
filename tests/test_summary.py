from ibis_profiling.report.model.summary import SummaryEngine
from ibis_profiling.logical_types import IPAddress, SWIFT
import ibis.expr.datatypes as dt
import polars as pl


def test_summary_logic():
    assert SummaryEngine.process_variables(pl.DataFrame([]), {}) == {}


def test_summary_uses_registry_display_labels():
    variables = SummaryEngine.process_variables(
        pl.DataFrame([]),
        {"ip": dt.string, "swift": dt.string},
        logical_types={"ip": IPAddress, "swift": SWIFT},
    )

    assert variables["ip"]["logical_type"] == "IP Address"
    assert variables["swift"]["logical_type"] == "SWIFT/BIC"
