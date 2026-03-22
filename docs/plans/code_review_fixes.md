# Code Review Remediation Plan

**Background & Motivation:**
A recent code review identified several medium and low severity issues related to logic, performance, and best practices. These issues include bugs parsing metric keys with `__`, unhashable types breaking value counts, an expensive full-table distinct count causing OOMs, redundant counting in the interaction engine, schema dict mutations, and broad exception swallowing. Addressing these issues will make the profiler more robust and performant.

**Scope & Impact:**
This plan covers fixes in `src/ibis_profiling` and tests. The distinct count will be parameterized to allow users to disable it on massive datasets while remaining on by default.

**Phased Implementation Plan:**

### Stage 1: Logic Fixes (Metric Keys & Hashability)
**Changes:**
1.  **`src/ibis_profiling/report/model/summary.py`**: Update `process_variables` to use `.rsplit("__", 1)` instead of `.split("__", 1)` to handle column names that contain `__`.
2.  **`src/ibis_profiling/__init__.py`**: Update `_run_advanced_pass` and `_run_monotonicity` (or anywhere metric parsing happens) to use `.rsplit("__", 1)`.
3.  **`src/ibis_profiling/planner.py`**: Update `QueryPlanner.build_complex_metrics` to enforce an `is_hashable` check before calling `value_counts()` on discrete types.
**Verification:**
-   Add a test with a column named `user__id__column` to ensure it parses correctly and retains metrics.
-   Add a test with an `Array` or `Struct` column to ensure it skips `value_counts` without erroring.

### Stage 2: Core Performance (Parameterize Expensive Distinct Count)
**Changes:**
1.  **`src/ibis_profiling/cli.py`** and **`src/ibis_profiling/__init__.py`**: Add a new parameter `compute_duplicates` (boolean, default `True`) to the `profile()` entrypoint and `Profiler` class.
2.  **`src/ibis_profiling/__init__.py`**: Update the `Profiler.run` duplicate section (step 4). If `compute_duplicates` is `False`, skip `n_distinct_rows` and append a warning to `report.analysis["warnings"]` like "Skipped duplicate check as requested."
**Verification:**
-   Add tests to verify `n_duplicates` is computed when `compute_duplicates=True`.
-   Add tests to verify the distinct query is skipped and a warning is present when `compute_duplicates=False`.

### Stage 3: Interaction Engine Performance
**Changes:**
1.  **`src/ibis_profiling/report/model/interactions.py`**: Update `InteractionEngine.compute` to avoid `table.count().to_pyarrow().as_py()`. Accept `row_count` as an argument from the `Profiler` or calculate it safely via `sampled_table = table.limit(sample_size)`.
2.  **`src/ibis_profiling/__init__.py`**: Pass the already computed `row_count` to the interaction engine if applicable.
**Verification:**
-   Verify interactions still compute correctly.
-   Ensure no full table scan is triggered by the interaction engine during execution (mock or inspect queries if possible).

### Stage 4: Best Practices (Schema Mutation & Exceptions)
**Changes:**
1.  **`src/ibis_profiling/report/report.py`**: In `ProfileReport._build`, update the schema mutation line from `dataset_meta = self.schema.pop("_dataset", {})` to `schema_copy = dict(self.schema); dataset_meta = schema_copy.pop("_dataset", {})` and pass `schema_copy`.
2.  **`src/ibis_profiling/engine.py`**: In `DuckDBAdapter.get_storage_size` and `ExecutionEngine._get_adapter`, replace `except Exception:` with specific exceptions (e.g., `(AttributeError, ValueError, TypeError)`) and add a `logging.getLogger(__name__)` to log the failure in debug mode.
**Verification:**
-   Run the full test suite (`uv run pytest`) to ensure no regressions.
-   Add a test to ensure `self.schema` retains the `_dataset` key after report generation.
-   Add a test for exception handling in adapters (mock backend failure).

**Migration & Rollback:**
-   Changes are non-breaking except for adding a new optional parameter.
-   If any stage fails, rollback the specific stage using `git revert` or `git reset` and fix before proceeding.

**Final Approval:**
Run `uv run pytest` and `ruff check .` to ensure the entire suite passes cleanly.