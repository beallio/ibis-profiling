from ibis_profiling.report import models


def test_numeric_variable_stats_are_typed_and_round_trip():
    source = {
        "logical_type": "Decimal",
        "count": 99,
        "95%": 95.1,
        "25%": 26.5,
        "p_zeros": 0.0,
        "histogram": {"bins": ["[1, 2]"], "counts": [99]},
        "n_negative": 0,
        "n_zeros": 0,
        "n_unique": 99,
        "5%": 5.9,
        "cv": 0.56,
        "n": 100,
        "std": 28.8,
        "skewness": -0.01,
        "n_distinct": 99,
        "p_negative": 0.0,
        "iqr": 49.0,
        "range": 99.0,
        "type": "Numeric",
        "n_missing": 1,
        "max": 100.0,
        "n_infinite": 0,
        "p_unique": 0.99,
        "mean": 50.9,
        "extreme_values_largest": [100.0, 99.0],
        "min": 1.0,
        "monotonic_increasing": True,
        "monotonic_decreasing": False,
        "variance": 833.3,
        "mad": 24.8,
        "extreme_values_smallest": [1.0, 2.0],
        "sum": 5040.0,
        "75%": 75.5,
        "is_unique": False,
        "p_distinct": 0.99,
        "hashable": True,
        "p_missing": 0.01,
        "50%": 51.0,
        "p_infinite": 0.0,
        "kurtosis": -1.18,
    }

    variable = models.VariableProfile.from_dict(source)

    assert isinstance(variable.stats, models.NumericStats)
    assert variable.stats.mean == 50.9
    assert variable.stats.p50 == 51.0
    assert variable.stats.n_zeros == 0
    assert "mean" not in variable.extra
    assert variable.extra["logical_type"] == "Decimal"
    assert variable.to_dict() == source


def test_text_variable_stats_are_typed_and_round_trip():
    source = {
        "p_empty": 0.25,
        "count": 100,
        "n_empty": 25,
        "histogram": {"bins": ["alpha", "(Empty)"], "counts": [75, 25]},
        "n_unique": 0,
        "logical_type": "Categorical",
        "n": 100,
        "n_distinct": 2,
        "min_length": 0,
        "max_length": 5,
        "type": "Categorical",
        "n_missing": 0,
        "length_histogram": {"bins": ["0", "5"], "counts": [25, 75]},
        "p_unique": 0.0,
        "extreme_values_largest": ["alpha", ""],
        "extreme_values_smallest": ["", "alpha"],
        "is_unique": False,
        "mean_length": 3.75,
        "p_distinct": 0.02,
        "hashable": True,
        "p_missing": 0.0,
    }

    variable = models.VariableProfile.from_dict(source)

    assert isinstance(variable.stats, models.TextStats)
    assert variable.stats.mean_length == 3.75
    assert variable.stats.n_empty == 25
    assert "mean_length" not in variable.extra
    assert variable.extra["logical_type"] == "Categorical"
    assert variable.to_dict() == source


def test_non_numeric_or_text_variable_has_no_typed_stats():
    source = {
        "type": "Boolean",
        "count": 2,
        "n_missing": 0,
        "p_missing": 0.0,
        "n_distinct": 2,
    }

    variable = models.VariableProfile.from_dict(source)

    assert variable.stats is None
    assert variable.extra == {"n_distinct": 2}
    assert variable.to_dict() == source
