# Implementation Plan - Address Code Review Findings

## Objective
Address the 7 findings from the code review `docs/review/review_20260321.md` to improve security, reliability, and performance of the `ibis-profiling` tool.

## Key Files & Context
- `src/ibis_profiling/report/report.py`: `ProfileReport.to_html` (XSS vulnerability).
- `src/ibis_profiling/engine.py`: `ExecutionEngine.get_storage_size` (SQL injection risk).
- `scripts/run_benchmarks.py`: `main` (Command injection risk).
- `src/ibis_profiling/metrics.py`: `n_unique` metric (Logic bug with column naming).
- `src/ibis_profiling/report/model/missing.py`: `MissingEngine.compute` (Logic bug with `IndexError`).
- `src/ibis_profiling/report/model/interactions.py`: `InteractionEngine.compute` (Performance bottleneck).
- `src/ibis_profiling/__init__.py`: `profile` (Swallowing exceptions).

## Implementation Steps

### 1. Security Fixes
#### XSS in `ProfileReport.to_html`
- Modify `to_html` to escape `<` in the JSON string before injection into the HTML template.

#### SQL Injection in `ExecutionEngine.get_storage_size`
- Implement a whitelist regex for table names and use parameterized queries for `pragma_storage_info`.

#### Command Injection in `scripts/run_benchmarks.py`
- Replace `os.system` calls with `subprocess.run` using argument lists.

### 2. Logic Fixes
#### `n_unique` metric column naming
- Update the `n_unique` metric definition to robustly identify the count column from `value_counts()`.

#### `IndexError` in `MissingEngine.compute`
- Add a guard to return early with an empty model if no variables are provided.

### 3. Performance & Best Practices
#### Pairwise interactions optimization
- Use `itertools.combinations` to ensure each pair of numeric columns is only computed once, then populate both `(col1, col2)` and `(col2, col1)` in the results.

#### Histogram error reporting
- Instead of `pass`, append warning messages to the report's analysis section when histogram computation fails.

## Verification & Testing
- Create `tests/test_security_fixes.py` to verify:
    - XSS prevention in generated HTML.
    - SQL injection protection in `get_storage_size`.
- Update `tests/test_missing.py` with an empty table test case.
- Update `tests/test_interactions.py` to verify pairwise data completeness and efficiency.
- Add a test case to `tests/test_metrics.py` for `n_unique` backend consistency.
- Verify histogram warnings in `tests/test_profiler.py`.
- Run the full test suite and quality checks:
    ```bash
    ruff check . --fix
    ruff format .
    uv run ty check src/
    uv run pytest
    ```
