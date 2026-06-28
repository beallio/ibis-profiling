# Plan: Implement Proper Numeric Histograms

## Objective
Replace the current `value_counts()` hack for numeric histograms with a true statistical binning approach. This will ensure that continuous data (like normal distributions) is correctly visualized as a bell curve rather than a flat line of top values.

## Proposed Solution
Instead of just taking the top 20 most frequent values, we will divide the data range into 20 equal-width bins.

### Logic
1. **Pass 1 (Existing)**: We already calculate `min` and `max` for all numeric columns.
2. **Histograms Calculation (New)**:
   - For each numeric column:
     - Use `min` and `max` from Pass 1.
     - Calculate bin index: `bin_idx = ((col - min) / (max - min) * 20).floor()`.
     - Clip `bin_idx` to `[0, 19]`.
     - Perform `value_counts()` on the `bin_idx` to get counts per bucket.
     - Map bucket indices back to range labels (e.g., "[10.0, 12.5]").

## Key Files
- `src/ibis_profiling/__init__.py`: Orchestrate the histogram calculation after Pass 1.
- `src/ibis_profiling/planner.py`: Clean up the old pseudo-histogram logic.
- `src/ibis_profiling/report/report.py`: (Optional) Update to handle the new histogram format if needed.

## Implementation Steps

### 1. Update Planner
- Modify `QueryPlanner.build_complex_metrics` to only use `value_counts()` for Categorical/Boolean types.
- Remove the rounding hack for numeric types.

### 2. Update Profile Entry Point
- In `src/ibis_profiling/__init__.py`:
    - After the first pass aggregates are collected:
    - Identify numeric columns.
    - Build a new set of expressions for binned histograms using the known `min`/`max`.
    - Execute and pass to `report.add_metric`.

### 3. Update Report Model
- Ensure `add_metric` can handle the binned data and format the labels nicely as ranges.

## Verification
- Run the "Normal Distribution Test" script.
- Verify the `report_variables.png` shows a bell curve.
