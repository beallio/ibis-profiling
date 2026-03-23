import ibis
import pandas as pd
from ibis_profiling import profile
import ibis.expr.types as ir


def is_ibis_expr(obj):
    """Recursively check if any value in a nested structure is an Ibis expression."""
    if isinstance(obj, ir.Expr):
        return True
    if isinstance(obj, dict):
        return any(is_ibis_expr(v) for v in obj.values())
    if isinstance(obj, list):
        return any(is_ibis_expr(v) for v in obj)
    return False


def test_no_unexecuted_expressions():
    """
    Verify that the final report dictionary contains NO unexecuted Ibis expressions.
    This prevents the 'blank report' issue where the frontend receives raw Ibis objects.
    """
    df = pd.DataFrame({"a": [1, 2, None, 4], "b": [4, 3, 2, 1], "c": [1, 1, 1, 1]})
    table = ibis.memtable(df)

    # We want to check ALL components: summary, correlations, missing, interactions
    report = profile(table, minimal=False)
    data = report.to_dict()

    # Check for Ibis expressions
    assert not is_ibis_expr(data), "Found unexecuted Ibis expressions in report data!"


def test_missing_matrix_structure():
    """Verify that the Missingness Matrix has the correct structure for the frontend."""
    df = pd.DataFrame({"a": [1, None], "b": [None, 2]})
    table = ibis.memtable(df)
    report = profile(table)
    data = report.to_dict()

    missing = data.get("missing", {})
    assert "matrix" in missing
    # The frontend now expects a list of dicts under missing.matrix.matrix.matrix
    # missing.matrix is the section, missing.matrix.matrix is the matrix wrapper, missing.matrix.matrix.matrix is the list
    inner_matrix_obj = missing["matrix"].get("matrix", {})
    assert isinstance(inner_matrix_obj, dict)
    inner_matrix = inner_matrix_obj.get("matrix", [])
    assert isinstance(inner_matrix, list)
    assert len(inner_matrix) == 2
    assert "a" in inner_matrix[0]
    assert "b" in inner_matrix[0]


def test_correlation_matrix_values():
    """Verify that correlation matrices contain actual numbers, not expression strings."""
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [1, 2, 3, 4]})
    table = ibis.memtable(df)
    report = profile(table)
    data = report.to_dict()

    # In our JSON output, correlations are now dicts with a 'matrix' key
    pearson = data["correlations"]["pearson"]
    assert isinstance(pearson, dict)
    assert "matrix" in pearson
    matrix = pearson["matrix"]
    assert isinstance(matrix, list)
    assert "a" in matrix[0]
    assert isinstance(matrix[0]["a"], float)
    assert matrix[0]["a"] == 1.0
