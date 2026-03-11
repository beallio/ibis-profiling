import ibis
from ibis_profiling.report.model.missing import MissingEngine


def test_missing_logic():
    table = ibis.memtable({"a": [1, None, 3], "b": [None, 2, 3]})
    variables = {"a": {"n_missing": 1, "n": 3}, "b": {"n_missing": 1, "n": 3}}
    result = MissingEngine.compute(table, variables)
    assert "bar" in result
    assert result["bar"]["matrix"]["counts"] == [1, 1]
    assert "matrix" in result
    assert "heatmap" in result
