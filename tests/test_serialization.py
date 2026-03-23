import json
import polars as pl
import pytest
import ibis.expr.datatypes as dt
from ibis_profiling.report import ProfileReport


def test_json_serialization_handles_complex_types():
    # Test all problematic types together
    from datetime import datetime

    raw_results = pl.DataFrame(
        [
            {
                "a__min": datetime(2023, 1, 1),
                "b__mean": 10.5,
                "_dataset__row_count": 20000000,
            }
        ]
    )
    schema = {"a": dt.Timestamp(), "b": dt.Float64()}

    report = ProfileReport(raw_results, schema)
    result = report.to_dict()

    # This should now PASS
    json_str = json.dumps(result)
    assert isinstance(json_str, str)

    # Check values
    assert result["table"]["n"] == 20000000
    assert result["variables"]["a"]["min"] == "2023-01-01T00:00:00"
    assert result["variables"]["b"]["mean"] == 10.5


def test_missing_matrix_serialization_structure():
    """Verify that the missing matrix is correctly serialized into a list of dicts for the frontend."""
    import ibis
    import ibis.expr.datatypes as dt
    from ibis_profiling.report.model.missing import MissingEngine

    raw_results = pl.DataFrame([{"_dataset__row_count": 10}])
    schema = {"a": dt.Int64(), "b": dt.String()}

    table = ibis.memtable({"a": [1, None, 3], "b": ["x", "y", None]})
    variables = {
        "a": {"type": "Numeric", "n_missing": 1, "n": 3},
        "b": {"type": "Categorical", "n_missing": 1, "n": 3},
    }

    report = ProfileReport(raw_results, schema)
    report.missing = MissingEngine.compute(table, variables)

    d = report.to_dict()

    # Check structure
    assert "missing" in d
    assert "matrix" in d["missing"]

    matrix_section = d["missing"]["matrix"]
    assert "name" in matrix_section
    assert "caption" in matrix_section
    assert "matrix" in matrix_section

    # The crucial part: matrix_section['matrix'] must contain the list of dicts
    matrix_obj = matrix_section["matrix"]
    assert isinstance(matrix_obj, dict)
    matrix_data = matrix_obj["matrix"]
    assert isinstance(matrix_data, list), (
        f"Expected matrix data to be a list, got {type(matrix_data)}"
    )
    assert len(matrix_data) > 0
    assert isinstance(matrix_data[0], dict), (
        f"Expected matrix row to be a dict, got {type(matrix_data[0])}"
    )
    assert "a" in matrix_data[0]
    assert "b" in matrix_data[0]


if __name__ == "__main__":
    pytest.main([__file__])
