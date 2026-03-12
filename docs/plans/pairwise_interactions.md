# Plan: Pairwise Interactions for Scatter Plots

## Status: Completed (2026-03-12)

## Objective
Implement pairwise interactions to provide data for scatter plots in the profiling report. This allows users to visualize relationships between numeric variables.

## Background & Motivation
Currently, `ibis-profiling` computes correlation matrices (Pearson/Spearman), but does not provide the underlying raw data for scatter plots. `ydata-profiling` includes an "Interactions" section where users can select pairs of variables to see their scatter plot. We need to efficiently sample and package this data.

## Scope & Impact
- **Sampling**: Extract a subset (e.g., 500-1000 points) of numeric variable pairs.
- **Data Structure**: Store pairwise data in the `interactions` dictionary in the report model.
- **UI**: Update the HTML template to render scatter plots.

## Proposed Solution

### 1. New Interaction Engine
Create `src/ibis_profiling/report/model/interactions.py`:
- `InteractionEngine.compute(table, variables, sample_size=1000)`:
  - Identify numeric columns.
  - Sample the table for efficiency.
  - For each pair of numeric columns (col1, col2), extract (x, y) coordinates.
  - Return a nested dictionary: `{col1: {col2: [{"x": v1, "y": v2}, ...]}}`.

### 2. Update `ProfileReport`
In `src/ibis_profiling/report/report.py`:
- Ensure `interactions` dictionary is correctly populated and serialized.

### 3. Update `profile()`
In `src/ibis_profiling/__init__.py`:
- Invoke `InteractionEngine.compute()` when `minimal=False`.
- Pass results to the `report` object.

### 4. UI Template
In `src/ibis_profiling/templates/default.html`:
- Add an "Interactions" tab/section.
- Implement a selector for X and Y axes (numeric columns only).
- Render a scatter plot.

## Implementation Plan

### Phase 1: Engine & Model (TDD)
1.  Create `tests/test_interactions.py` with a failing test.
2.  Create `src/ibis_profiling/report/model/interactions.py`.
3.  Update `src/ibis_profiling/__init__.py` to integrate the engine.
4.  Verify tests pass.

### Phase 2: UI Integration
1.  Update `src/ibis_profiling/templates/default.html` to display the "Interactions" section.
2.  Implement the scatter plot visualization.

## Verification
- Run `uv run pytest tests/test_interactions.py`.
- Manually inspect generated HTML reports.
