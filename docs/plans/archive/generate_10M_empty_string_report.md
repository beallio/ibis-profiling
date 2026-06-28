# Plan: Generate 10M x 20 Test Report with Empty String Column

## Objective
Generate a large-scale test report (10 million rows by 20 columns) to verify the profiler's behavior and performance on datasets with specific characteristics, specifically an entirely empty string column.

## Key Files & Context
- **Script:** `scripts/generate_10M_empty_string_report.py` (to be created)
- **Output:** `/tmp/ibis-profiling/report_10M_empty.html`
- **Output:** `/tmp/ibis-profiling/data_10M_empty.parquet`

## Implementation Steps

### 1. Create Generation and Profiling Script
Create `scripts/generate_10M_empty_string_report.py` based on `scripts/profile_5M_20cols.py`.
- Configure it to generate 10,000,000 rows and 20 columns.
- One column `empty_strings` will be populated exclusively with `""`.
- Use `ibis` with the DuckDB backend for efficient processing of the Parquet file.
- Generate both minimal and full reports for comparison, but focus on the full report for the user's request.

### 2. Execute the Script
Run the script using `uv run` with the required environment variables:
```bash
export UV_PROJECT_ENVIRONMENT=/tmp/ibis-profiling/.venv
export XDG_CACHE_HOME=/tmp/ibis-profiling/.cache
export PYTHONPYCACHEPREFIX=/tmp/ibis-profiling/__pycache__
uv run scripts/generate_10M_empty_string_report.py
```

### 3. Verify Results
- Confirm `report_10M_empty.html` exists in `/tmp/ibis-profiling/`.
- Verify the dataset size in the report (10,000,000 rows, 20 columns).
- Inspect the `empty_strings` column metadata in the JSON output (if generated) or by visually checking the HTML.

## Verification & Testing
- **Red (Test Case):** Create a small test `tests/test_empty_strings_large.py` to verify that a dataset with an empty string column can be profiled without error and that the column is correctly summarized.
- **Green:** Run the generation script and ensure it completes successfully.
- **Validate:** Check the output HTML for correctness.
