import polars as pl
import ibis.expr.datatypes as dt
from ibis_profiling.report.report import ProfileReport


def test_correlation_and_missing_model():
    # Setup a small dataset with correlations and missing values
    raw_results = pl.DataFrame([{"a__mean": 10.0, "b__mean": 20.0, "_dataset__row_count": 10}])
    schema = {"a": dt.Int64(), "b": dt.Int64()}

    report = ProfileReport(raw_results, schema)

    # Manually add some metrics to simulate engine output
    report.variables["a"]["n_missing"] = 2
    report.variables["b"]["n_missing"] = 5

    # Re-run missing processing
    from ibis_profiling.report.model.missing import MissingEngine

    report.missing = MissingEngine.process(report.variables)

    # Check missing model
    assert "bar" in report.missing
    assert report.missing["bar"]["matrix"]["counts"] == [2, 5]

    # Add correlations
    report.correlations["pearson"] = {"columns": ["a", "b"], "matrix": [[1.0, 0.5], [0.5, 1.0]]}

    result = report.to_dict()
    assert len(result["correlations"]["pearson"]["matrix"]) == 2
    assert result["missing"]["bar"]["matrix"]["counts"] == [2, 5]


def test_categorical_histogram_mapping():
    raw_results = pl.DataFrame([{"_dataset__row_count": 100}])
    schema = {"cat": dt.String()}
    report = ProfileReport(raw_results, schema)

    # Simulate top_values for categorical
    top_vals = {"cat": ["A", "B"], "cat_count": [60, 40]}
    report.add_metric("cat", "top_values", top_vals)

    assert "histogram" in report.variables["cat"]
    assert report.variables["cat"]["histogram"]["bins"] == ["A", "B"]
    assert report.variables["cat"]["histogram"]["counts"] == [60, 40]
