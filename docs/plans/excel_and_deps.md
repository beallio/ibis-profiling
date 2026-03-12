# Plan: Excel Support and Dependency Optimization

## Objective
1. Enable profiling of Excel files (.xlsx, .xls, .xlsb) using `ibis-profiling` with high performance.
2. Optimize project dependencies by moving benchmarking tools to development groups and adding `fastexcel`.

## Proposed Solution: Excel Support
Add `ProfileReport.from_excel()` and a top-level `profile_excel()` function.

### Engine Strategy
- **Use Polars (`calamine`)**: 
  - **Performance**: Rust-based engine for extremely fast parsing.
  - **Dependency**: Add `fastexcel` to project dependencies.
  - **Logic**: Use `polars.read_excel(path, engine="calamine", **kwargs)`.
  - **Fallback**: Not required as we will explicitly include the `fastexcel` dependency.

## Proposed Solution: Dependency Optimization
- **fastexcel**: Add to `dependencies` for fast Excel support.
- **ydata-profiling**: Move from `dependencies` to `dev-dependencies`.
- **pandas**: While `ibis` needs it, we will keep it for now as a transitive dependency of Ibis, but not use it directly in our core.

## Key Files
- `src/ibis_profiling/__init__.py`: Add `profile_excel` and update `ProfileReport` wrapper.
- `src/ibis_profiling/report/report.py`: Add `ProfileReport.from_excel` static method.
- `pyproject.toml`: Add `fastexcel` and reorganize dependencies.

## Implementation Steps

### 1. Update Project Dependencies
- Modify `pyproject.toml`:
    - Add `fastexcel>=0.11.5` to `dependencies`.
    - Move `ydata-profiling` to `[dependency-groups].dev`.
- Run `uv sync` to update environment.

### 2. Update Internal Report Model
- In `src/ibis_profiling/report/report.py`:
    - Add `@staticmethod from_excel(path, **kwargs)`.
    - Implementation:
        - Import `polars` and `ibis`.
        - Read file with `pl.read_excel(path, engine="calamine", **kwargs)`.
        - Load into Ibis via `memtable`.
        - Return `profile(table)`.

### 3. Update Entry Point
- In `src/ibis_profiling/__init__.py`:
    - Add `profile_excel(path, **kwargs)` function.
    - Update `ProfileReport` wrapper to include `from_excel`.

## Verification & Testing
- Create a test script that generates an Excel file and profiles it.
- Verify that `ibis-profiling` uses the Polars engine.
