import pytest
from ibis_profiling.config import ProfileConfig


def test_profile_config_immutability():
    config = ProfileConfig.resolve(
        n_rows=1000,
        n_cols=10,
        minimal=False,
    )
    with pytest.raises(Exception):  # dataclass FrozenInstanceError
        config.minimal = True


def test_profile_config_resolutions():
    # n_unique_threshold None -> max(1_000_000, int(0.1*n_rows))
    config1 = ProfileConfig.resolve(
        n_rows=20_000_000, n_cols=10, minimal=False, n_unique_threshold=None
    )
    assert config1.n_unique_threshold == 2_000_000

    config2 = ProfileConfig.resolve(n_rows=100, n_cols=10, minimal=False, n_unique_threshold=None)
    assert config2.n_unique_threshold == 1_000_000

    config3 = ProfileConfig.resolve(
        n_rows=100, n_cols=10, minimal=False, n_unique_threshold=50_000_000
    )
    assert config3.n_unique_threshold == 50_000_000

    # global_batch_size None -> MemoryManager.calculate_batch_size(n_rows, n_cols)
    config4 = ProfileConfig.resolve(n_rows=100, n_cols=10, minimal=False, global_batch_size=None)
    assert config4.global_batch_size > 0

    config5 = ProfileConfig.resolve(n_rows=100, n_cols=10, minimal=False, global_batch_size=42)
    assert config5.global_batch_size == 42


def test_profile_config_clamps():
    config = ProfileConfig.resolve(
        n_rows=100,
        n_cols=10,
        minimal=False,
        correlations_max_columns=0,
        missing_heatmap_max_columns=1,
        missing_matrix_max_columns=-5,
    )
    assert config.correlations_max_columns == 2
    assert config.missing_heatmap_max_columns == 2
    assert config.missing_matrix_max_columns == 2


def test_profile_config_validation_warnings():
    config = ProfileConfig.resolve(
        n_rows=100,
        n_cols=10,
        minimal=False,
        correlations_sampling_threshold=0,
        correlations_sample_size=-10,
    )
    assert config.correlations_sampling_threshold == 1_000_000
    assert config.correlations_sample_size == 1_000_000
    assert len(config.validation_warnings) == 2
    assert "correlations_sampling_threshold" in config.validation_warnings[0]
    assert "correlations_sample_size" in config.validation_warnings[1]


def test_profile_config_flag_derivation():
    config_minimal = ProfileConfig.resolve(n_rows=100, n_cols=10, minimal=True)
    assert config_minimal.compute_correlations is False
    assert config_minimal.compute_monotonicity is False
    assert config_minimal.compute_duplicates is False

    config_override = ProfileConfig.resolve(n_rows=100, n_cols=10, minimal=True, correlations=True)
    assert config_override.compute_correlations is True

    config_explicit = ProfileConfig.resolve(
        n_rows=100, n_cols=10, minimal=False, monotonicity=True, compute_duplicates=True
    )
    assert config_explicit.explicit_monotonicity is True
    assert config_explicit.explicit_duplicates is True
