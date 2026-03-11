from ibis_profiling.report.model.summary import SummaryEngine
import polars as pl


def test_summary_logic():
    assert SummaryEngine.process_variables(pl.DataFrame([]), {}) == {}
