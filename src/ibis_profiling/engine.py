import ibis
import ibis.expr.types as ir
import polars as pl
import logging
from typing import cast, Protocol
from ibis.common.exceptions import IbisError

logger = logging.getLogger(__name__)


class BackendAdapter(Protocol):
    def get_storage_size(self, table: ibis.Table) -> int | None: ...


class DuckDBAdapter:
    def get_storage_size(self, table: ibis.Table) -> int | None:
        """
        Attempts to get the storage size for DuckDB tables.
        Currently returns None as reliable cross-version byte size is not straightforward.
        """
        try:
            # Structure for future optimizations:
            # 1. Identify table name
            # 2. Whitelist check
            # 3. Execute backend-specific size lookup
            return None
        except (AttributeError, ValueError, TypeError, IbisError) as exc:
            logger.debug("DuckDB storage size lookup failed: %s", exc)
            return None
        except Exception as exc:
            logger.debug("DuckDB storage size lookup backend error: %s", exc)
            return None


class DefaultAdapter:
    def get_storage_size(self, table: ibis.Table) -> int | None:
        return None


class ExecutionEngine:
    def __init__(self):
        self._adapters = {
            "duckdb": DuckDBAdapter(),
        }

    def _get_adapter(self, table: ibis.Table) -> BackendAdapter:
        try:
            con = table._find_backend()
            return self._adapters.get(con.name, DefaultAdapter())
        except (AttributeError, ValueError, TypeError, IbisError) as exc:
            logger.debug("Failed to get backend adapter: %s", exc)
            return DefaultAdapter()
        except Exception as exc:
            logger.debug("Failed to get backend adapter with unknown error: %s", exc)
            return DefaultAdapter()

    def execute(self, plan: ir.Table) -> pl.DataFrame:
        """
        Executes the optimized Ibis expression graph.
        Returns a Polars DataFrame.
        """
        return cast(pl.DataFrame, pl.from_arrow(plan.to_pyarrow()))

    def get_storage_size(self, table: ibis.Table) -> int | None:
        """
        Attempts to get the actual storage size from the backend.
        """
        adapter = self._get_adapter(table)
        return adapter.get_storage_size(table)
