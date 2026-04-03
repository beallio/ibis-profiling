import psutil
import logging
from typing import Any

logger = logging.getLogger(__name__)


class MemoryManager:
    """Heuristics for batch sizing and memory limits."""

    @staticmethod
    def get_available_memory_mb() -> float:
        """Returns available system memory in MB."""
        return psutil.virtual_memory().available / (1024 * 1024)

    @staticmethod
    def calculate_batch_size(n_rows: int, n_cols: int, available_mb: float | None = None) -> int:
        """
        Heuristic: batch_size = clamp(500 / (total_cells / 10M), 5, 500)
        Based on benchmarks, 500M cells at batch 500 uses ~3.6GB.
        If we have 10M rows and 50 cols, we should probably use batch ~50.
        """
        if available_mb is None:
            available_mb = MemoryManager.get_available_memory_mb()

        # Benchmarks show that at 10M rows x 50 cols (500M cells):
        # Batch 500: 3.6GB
        # Batch 50: 2.8GB
        # Batch 5: 2.6GB
        #
        # The penalty for small batches is low (~5-10% duration),
        # but the memory safety gain is significant on large datasets.

        total_cells = n_rows * n_cols

        if total_cells < 10_000_000:
            return 500  # Small dataset, go fast

        if total_cells < 100_000_000:
            return 100

        if total_cells < 500_000_000:
            return 50

        return 20  # Large dataset, be conservative

    @staticmethod
    def apply_duckdb_limits(con: Any, available_mb: float | None = None):
        """Sets DuckDB memory limit to 70% of available RAM."""
        try:
            if hasattr(con, "name") and con.name == "duckdb":
                if available_mb is None:
                    available_mb = MemoryManager.get_available_memory_mb()

                # Use 70% of available memory as a safety margin
                limit_mb = int(available_mb * 0.7)
                con.raw_sql(f"SET memory_limit='{limit_mb}MB'")
                logger.info(f"Set DuckDB memory_limit to {limit_mb}MB")
        except Exception as e:
            logger.debug(f"Failed to set DuckDB memory limits: {e}")

    @staticmethod
    def to_int(val: Any) -> int:
        """Safely converts an Ibis/DuckDB result to int."""
        if val is None:
            return 0
        if isinstance(val, int):
            return val
        if isinstance(val, str):
            try:
                return int(val)
            except ValueError:
                return 0
        if hasattr(val, "item") and callable(val.item):
            return int(val.item())
        # If it's a polars/pandas-like object with a first element
        try:
            if hasattr(val, "__getitem__") and not isinstance(val, (str, bytes)):
                return int(val[0])
        except Exception:
            pass
        try:
            return int(val)
        except Exception:
            return 0
