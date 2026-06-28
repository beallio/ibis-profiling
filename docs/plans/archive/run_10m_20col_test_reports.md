# Plan: 10M x 20 Col Customer Report Comparison

## Problem Definition
Run test reports in both `default` and `ydata-like` themes using 10M rows and 20 columns of varied customer data in BOTH minimal and FULL modes to verify performance and visual consistency at scale.

## Architecture Overview
1.  **Data Generation**: Use a Python script with `Polars` and `Faker` to generate 10M rows of synthetic customer data with 20 columns.
2.  **Profiling**: Use `ibis-profiling` CLI to generate HTML reports.
3.  **Output**: Store reports in `/tmp/ibis-profiling/`.

## Core Data Structures
-   **Input**: `10M_20col_customer_data.parquet`
-   **Outputs**: `report_default_10M.html`, `report_ydata_10M.html`

## Public Interfaces
-   `scripts/generate_10m_20col_customer_data.py`
-   `ibis_profiling.cli`

## Dependency Requirements
-   `polars`
-   `faker`
-   `ibis-profiling` (local installation)

## Testing Strategy
1.  Verify data generation script runs successfully.
2.  Verify `ProfileReport` CLI runs for both themes.
3.  Verify output files exist and are non-empty.
