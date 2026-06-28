import warnings

import pytest

import ibis_profiling.wrapper as wrapper_module

ProfileReport = wrapper_module.ProfileReport


def test_profile_report_forwards_profile_options(monkeypatch):
    captured = {}

    def spy_profile(table, **kwargs):
        captured["table"] = table
        captured.update(kwargs)
        return object()

    monkeypatch.setattr(wrapper_module, "profile", spy_profile)

    table = object()
    on_progress = object()
    options = {
        "minimal": True,
        "title": "Forwarding Test",
        "on_progress": on_progress,
        "correlations": False,
        "monotonicity": True,
        "compute_duplicates": False,
        "cardinality_threshold": 3,
        "max_interaction_pairs": 4,
        "correlations_sampling_threshold": 5,
        "correlations_sample_size": 6,
        "sample_seed": 7,
        "correlations_max_columns": 8,
        "missing_heatmap_max_columns": 9,
        "missing_matrix_max_columns": 10,
        "monotonicity_threshold": 11,
        "duplicates_threshold": 12,
        "n_unique_threshold": 13,
        "inference_sample_size": 14,
        "monotonicity_order_by": "ordered_col",
        "use_sketches": True,
        "global_batch_size": 15,
    }

    ProfileReport(table, **options)

    assert captured["table"] is table
    for name, expected in options.items():
        if expected is on_progress:
            assert captured[name] is expected
        else:
            assert captured[name] == expected


def test_profile_report_warns_for_unknown_kwargs(monkeypatch):
    monkeypatch.setattr(wrapper_module, "profile", lambda table, **kwargs: object())

    with pytest.warns(UserWarning, match="definitely_not_an_option"):
        ProfileReport(object(), definitely_not_an_option=1)


def test_profile_report_accepts_title_without_unknown_kwarg_warning(monkeypatch):
    monkeypatch.setattr(wrapper_module, "profile", lambda table, **kwargs: object())

    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always")
        ProfileReport(object(), title="Legitimate Title")

    assert not records
