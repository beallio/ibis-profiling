from copy import deepcopy

from ibis_profiling import constants
from ibis_profiling.report import report


def test_derive_variable_metrics_calculates_numeric_fields_without_mutation():
    stats = {
        "type": "Numeric",
        "n_missing": 2,
        "n_distinct": 8,
        "n_unique": 3,
        "min": -2,
        "max": 8,
        "25%": 1,
        "75%": 7,
        "mean": 2,
        "std": 4,
        "n_zeros": 2,
        "n_infinite": 1,
        "n_negative": 3,
    }
    original = deepcopy(stats)

    result = report._derive_variable_metrics(stats, 10)

    assert result is not stats
    assert stats == original
    assert result["p_missing"] == 0.2
    assert result["p_distinct"] == 0.8
    assert result["count"] == 8
    assert result["is_unique"] is False
    assert result["range"] == 10
    assert result["iqr"] == 6
    assert result["cv"] == 2
    assert result["p_zeros"] == 0.2
    assert result["p_infinite"] == 0.1
    assert result["p_negative"] == 0.3
    assert result["p_unique"] == 0.3


def test_derive_variable_metrics_prunes_categorical_numeric_fields():
    stats = {
        "type": "Categorical",
        "n_missing": 1,
        "n_distinct": 4,
        "n_unique": 2,
        "n_empty": 3,
        **{metric: 99 for metric in constants.NUMERIC_ONLY_METRICS},
    }
    original = deepcopy(stats)

    result = report._derive_variable_metrics(stats, 10)

    assert stats == original
    assert result["p_empty"] == 0.3
    assert constants.NUMERIC_ONLY_METRICS.isdisjoint(result)


def test_derive_variable_metrics_preserves_skipped_distinct_value():
    stats = {
        "type": "Categorical",
        "n_missing": "Skipped",
        "n_distinct": "Skipped",
        "n_unique": "Skipped",
    }
    original = deepcopy(stats)

    result = report._derive_variable_metrics(stats, 10)

    assert stats == original
    assert result["p_missing"] == 0
    assert result["p_distinct"] == "Skipped"
    assert result["count"] == 10
    assert result["is_unique"] is False
    assert result["p_unique"] == "Skipped"


def test_compute_table_aggregates_calculates_counts_without_mutation():
    variables = {
        "constant": {"n_missing": 2, "n_distinct": 1, "n_empty": 0},
        "all_missing": {"n_missing": 10, "n_distinct": 2, "n_empty": 3},
        "skipped": {
            "n_missing": "Skipped",
            "n_distinct": "Skipped",
            "n_empty": "Skipped",
        },
    }
    original = deepcopy(variables)

    result = report._compute_table_aggregates(variables, 10)

    assert variables == original
    assert result == {
        "n_cells_missing": 12,
        "n_cells_empty": 3,
        "n_vars_constant": 1,
        "n_vars_with_missing": 2,
        "n_vars_all_missing": 1,
        "n_vars_with_empty": 1,
        "p_cells_missing": 0.4,
        "p_cells_empty": 0.1,
    }


def test_compute_table_aggregates_guards_empty_tables():
    assert report._compute_table_aggregates({}, 0) == {
        "n_cells_missing": 0,
        "n_cells_empty": 0,
        "n_vars_constant": 0,
        "n_vars_with_missing": 0,
        "n_vars_all_missing": 0,
        "n_vars_with_empty": 0,
        "p_cells_missing": 0,
        "p_cells_empty": 0,
    }
