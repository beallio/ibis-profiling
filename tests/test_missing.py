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


def test_missing_engine_empty_variables():
    """Verify that MissingEngine doesn't crash on empty variables."""
    table = ibis.memtable({"a": [1, 2, 3]})
    variables = {}

    # Should not raise IndexError: list index out of range
    result = MissingEngine.compute(table, variables)

    assert result["bar"]["matrix"]["columns"] == []
    assert result["matrix"]["matrix"]["columns"] == []
    assert result["heatmap"]["matrix"]["columns"] == []


def test_missing_matrix_pyarrow_backend():
    """Verify that MissingEngine handles backends returning PyArrow tables."""
    import pyarrow as pa
    from unittest.mock import MagicMock

    variables = {
        "a": {"n_missing": 1, "n": 3, "type": "Numeric"},
        "b": {"n_missing": 1, "n": 3, "type": "Numeric"},
    }

    # Mock the Ibis table and its projection/limit chain
    mock_table = MagicMock()
    mock_proj = MagicMock()
    mock_limit = MagicMock()

    mock_table.projection.return_value = mock_proj
    mock_proj.limit.return_value = mock_limit

    # Simulate PyArrow return
    mock_arrow_table = pa.table({"a": [True, False, False], "b": [False, True, False]})
    mock_limit.to_pyarrow.return_value = mock_arrow_table

    # Also need to mock heatmap part if it gets executed
    # We'll just ensure it doesn't crash
    mock_table.aggregate.return_value.to_pyarrow.return_value.to_pydict.return_value = {}

    result = MissingEngine.compute(mock_table, variables)

    assert "matrix" in result
    assert result["matrix"]["matrix"]["matrix"] == [[True, False], [False, True], [False, False]]
