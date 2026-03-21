# Plan: Add Progress Bar to CLI

Add a progress bar to the CLI to provide visual feedback during the profiling process.

## Problem Definition
The current CLI tool `ProfileReport` does not provide visual feedback while it's processing large datasets. This makes it difficult for users to know if the process is stuck or how much time is remaining.

## Architecture Overview
The progress tracking will be implemented as a callback mechanism.
- `profile()` function in `src/ibis_profiling/__init__.py` will accept an `on_progress` callback.
- `ProfileReport` class will expose this callback in its constructor.
- `cli.py` will use `click.progressbar` to create a callback that updates the terminal UI.

## Core Data Structures
- `on_progress`: A callable with signature `(increment: int, label: str | None = None) -> None`.

## Public Interfaces
- `ProfileReport.__init__(..., on_progress=None)`
- `profile(..., on_progress=None)`

## Dependency Requirements
- `click` (already a dependency)

## Implementation Plan

### 1. Update `src/ibis_profiling/__init__.py`
Update `profile()` to include progress tracking.

#### Weights for Progress (Total 100)

**If NOT minimal:**
- Initial & Global Agg: 15
- Metadata & Reclassification: 5
- Static Metadata: 5
- Duplicates: 5
- Second Pass: 5
- Histograms: 15 (distributed)
- Complex Metrics: 15 (distributed)
- Correlations: 10
- Monotonicity: 5
- Samples: 5
- Missing Values: 5
- Interactions: 10

**If minimal:**
- Initial & Global Agg: 25
- Metadata & Reclassification: 10
- Static Metadata: 10
- Second Pass: 10
- Histograms: 20 (distributed)
- Complex Metrics: 15 (distributed)
- Samples: 10

### 2. Update `src/ibis_profiling/cli.py`
Use `click.progressbar` in the `main` function.

### 3. Testing Strategy
- **Unit Test:** `tests/test_progress.py` will verify that the callback is called with increments that sum to 100.
- **Manual Verification:** Run the CLI on a dataset and observe the progress bar.
- **Regression Testing:** Run `uv run pytest` to ensure all existing tests pass.

## Verification
- `ruff check . --fix`
- `ruff format .`
- `uv run ty check src/`
- `uv run pytest`
