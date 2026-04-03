import ibis
from typing import Callable
from .profiler import profile, profile_excel


class ProfileReport:
    """
    Compatibility wrapper to mimic ydata-profiling API.
    """

    def __init__(
        self,
        table: ibis.Table,
        minimal: bool = False,
        on_progress: Callable[[int, str | None], None] | None = None,
        correlations: bool | None = None,
        monotonicity: bool | None = None,
        compute_duplicates: bool | None = None,
        monotonicity_threshold: int = 100_000,
        duplicates_threshold: int = 50_000_000,
        n_unique_threshold: int = 50_000_000,
        correlations_max_columns: int = 15,
        missing_heatmap_max_columns: int = 15,
        missing_matrix_max_columns: int = 50,
        monotonicity_order_by: str | None = None,
        global_batch_size: int | None = None,
        **kwargs,
    ):
        self.table = table
        self.minimal = minimal
        self.on_progress = on_progress
        self.correlations = correlations
        self.monotonicity = monotonicity
        self.compute_duplicates = compute_duplicates
        self.monotonicity_threshold = monotonicity_threshold
        self.duplicates_threshold = duplicates_threshold
        self.n_unique_threshold = n_unique_threshold
        self.correlations_max_columns = correlations_max_columns
        self.missing_heatmap_max_columns = missing_heatmap_max_columns
        self.missing_matrix_max_columns = missing_matrix_max_columns
        self.monotonicity_order_by = monotonicity_order_by
        self.global_batch_size = global_batch_size
        self.kwargs = kwargs

        title = kwargs.get("title", "Ibis Profiling Report")
        self._report = profile(
            table,
            minimal=minimal,
            title=title,
            on_progress=on_progress,
            correlations=correlations,
            monotonicity=monotonicity,
            compute_duplicates=compute_duplicates,
            cardinality_threshold=kwargs.get("cardinality_threshold", 20),
            monotonicity_threshold=monotonicity_threshold,
            duplicates_threshold=duplicates_threshold,
            n_unique_threshold=n_unique_threshold,
            correlations_max_columns=correlations_max_columns,
            missing_heatmap_max_columns=missing_heatmap_max_columns,
            missing_matrix_max_columns=missing_matrix_max_columns,
            monotonicity_order_by=monotonicity_order_by,
            max_interaction_pairs=kwargs.get("max_interaction_pairs", 10),
            correlations_sampling_threshold=kwargs.get(
                "correlations_sampling_threshold", 1_000_000
            ),
            correlations_sample_size=kwargs.get("correlations_sample_size", 1_000_000),
            parallel=kwargs.get("parallel", False),
            pool_size=kwargs.get("pool_size", 4),
            use_sketches=kwargs.get("use_sketches", False),
            global_batch_size=global_batch_size,
        )

    @classmethod
    def from_excel(cls, path: str, **kwargs) -> "ProfileReport":
        """Compatibility method to mimic ydata-profiling from_excel."""
        instance = cls.__new__(cls)
        instance._report = profile_excel(path, **kwargs)
        return instance

    def to_file(
        self, output_file: str, theme: str = "default", minify: bool = True, offline: bool = True
    ):
        return self._report.to_file(output_file, theme=theme, minify=minify, offline=offline)

    def to_json(self) -> str:
        return self._report.to_json()

    def to_dict(self) -> dict:
        return self._report.to_dict()

    def get_description(self) -> dict:
        return self._report.get_description()

    def to_html(self, theme: str = "default", minify: bool = True, offline: bool = True) -> str:
        return self._report.to_html(theme=theme, minify=minify, offline=offline)

    @property
    def analysis(self) -> dict:
        return self._report.analysis
