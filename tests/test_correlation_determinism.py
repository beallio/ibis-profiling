import ibis

from ibis_profiling import profile


def _profile_sampled_data(sample_seed: int) -> dict:
    row_numbers = list(range(5_000))
    table = ibis.memtable(
        {
            "x": row_numbers,
            "y": [i * 0.5 + ((i * 37) % 101) for i in row_numbers],
            "z": [((i * 7919) % 5003) + (i % 17) for i in row_numbers],
        }
    )

    return profile(
        table,
        correlations_sampling_threshold=10,
        correlations_sample_size=200,
        sample_seed=sample_seed,
    ).to_dict()


def test_correlation_and_interaction_sampling_is_seeded():
    first = _profile_sampled_data(sample_seed=7)
    second = _profile_sampled_data(sample_seed=7)
    different_seed = _profile_sampled_data(sample_seed=11)

    first_matrices = (
        first["correlations"]["pearson"]["matrix"],
        first["correlations"]["spearman"]["matrix"],
    )
    second_matrices = (
        second["correlations"]["pearson"]["matrix"],
        second["correlations"]["spearman"]["matrix"],
    )
    different_seed_matrices = (
        different_seed["correlations"]["pearson"]["matrix"],
        different_seed["correlations"]["spearman"]["matrix"],
    )

    assert first_matrices == second_matrices
    assert first["interactions"] == second["interactions"]
    assert first_matrices != different_seed_matrices
