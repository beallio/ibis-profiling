from dataclasses import dataclass
from .memory import MemoryManager


@dataclass(frozen=True)
class ProfileConfig:
    minimal: bool
    title: str
    compute_correlations: bool
    compute_monotonicity: bool
    explicit_monotonicity: bool
    compute_duplicates: bool
    explicit_duplicates: bool
    cardinality_threshold: int
    max_interaction_pairs: int
    correlations_sampling_threshold: int
    correlations_sample_size: int
    sample_seed: int
    correlations_max_columns: int
    missing_heatmap_max_columns: int
    missing_matrix_max_columns: int
    monotonicity_threshold: int
    duplicates_threshold: int
    n_unique_threshold: int
    inference_sample_size: int | None
    monotonicity_order_by: str | None
    use_sketches: bool
    global_batch_size: int
    validation_warnings: tuple[str, ...]

    @classmethod
    def resolve(
        cls,
        *,
        n_rows: int,
        n_cols: int,
        minimal: bool = False,
        title: str = "Ibis Profiling Report",
        correlations: bool | None = None,
        monotonicity: bool | None = None,
        compute_duplicates: bool | None = None,
        cardinality_threshold: int = 20,
        max_interaction_pairs: int = 10,
        correlations_sampling_threshold: int = 1_000_000,
        correlations_sample_size: int = 1_000_000,
        sample_seed: int = 42,
        correlations_max_columns: int = 15,
        missing_heatmap_max_columns: int = 15,
        missing_matrix_max_columns: int = 50,
        monotonicity_threshold: int = 100_000,
        duplicates_threshold: int = 50_000_000,
        n_unique_threshold: int | None = None,
        inference_sample_size: int | None = 10_000,
        monotonicity_order_by: str | None = None,
        use_sketches: bool = False,
        global_batch_size: int | None = None,
    ) -> "ProfileConfig":

        compute_correlations_resolved = not minimal if correlations is None else correlations
        compute_monotonicity_resolved = not minimal if monotonicity is None else monotonicity
        explicit_monotonicity = monotonicity is True
        compute_duplicates_resolved = (
            not minimal if compute_duplicates is None else compute_duplicates
        )
        explicit_duplicates = compute_duplicates is True

        correlations_max_columns_resolved = max(2, correlations_max_columns)
        missing_heatmap_max_columns_resolved = max(2, missing_heatmap_max_columns)
        missing_matrix_max_columns_resolved = max(2, missing_matrix_max_columns)

        if n_unique_threshold is None:
            n_unique_threshold_resolved = max(1_000_000, int(0.1 * n_rows))
        else:
            n_unique_threshold_resolved = n_unique_threshold

        if global_batch_size is None:
            global_batch_size_resolved = MemoryManager.calculate_batch_size(n_rows, n_cols)
        else:
            global_batch_size_resolved = global_batch_size

        validation_warnings = []
        if correlations_sampling_threshold <= 0:
            correlations_sampling_threshold = 1_000_000
            validation_warnings.append(
                "Invalid correlations_sampling_threshold provided (must be > 0). "
                "Resetting to default (1,000,000)."
            )

        if correlations_sample_size <= 0:
            correlations_sample_size = 1_000_000
            validation_warnings.append(
                "Invalid correlations_sample_size provided (must be > 0). "
                "Resetting to default (1,000,000)."
            )

        return cls(
            minimal=minimal,
            title=title,
            compute_correlations=compute_correlations_resolved,
            compute_monotonicity=compute_monotonicity_resolved,
            explicit_monotonicity=explicit_monotonicity,
            compute_duplicates=compute_duplicates_resolved,
            explicit_duplicates=explicit_duplicates,
            cardinality_threshold=cardinality_threshold,
            max_interaction_pairs=max_interaction_pairs,
            correlations_sampling_threshold=correlations_sampling_threshold,
            correlations_sample_size=correlations_sample_size,
            sample_seed=sample_seed,
            correlations_max_columns=correlations_max_columns_resolved,
            missing_heatmap_max_columns=missing_heatmap_max_columns_resolved,
            missing_matrix_max_columns=missing_matrix_max_columns_resolved,
            monotonicity_threshold=monotonicity_threshold,
            duplicates_threshold=duplicates_threshold,
            n_unique_threshold=n_unique_threshold_resolved,
            inference_sample_size=inference_sample_size,
            monotonicity_order_by=monotonicity_order_by,
            use_sketches=use_sketches,
            global_batch_size=global_batch_size_resolved,
            validation_warnings=tuple(validation_warnings),
        )
