# Investigation: Unique Count Discrepancy

## Problem
In the initial parity report for the 1 million row loan dataset, a discrepancy was noted in the unique count for the `loan_amount` column:
- **Ibis-Native Profiler:** 962,611
- **ydata-profiling:** 934,133

## Findings
The investigation revealed that the two systems use different definitions for "unique":

1. **Ibis-Native Profiler (and DuckDB/Pandas/Polars default):**
   - The `unique` metric refers to **Distinct Values**.
   - It counts how many different values exist in the column, regardless of their frequency.
   - Calculation: `SELECT COUNT(DISTINCT loan_amount) FROM table`
   - Result: **962,611**

2. **ydata-profiling:**
   - It distinguishes between `n_distinct` and `n_unique`.
   - `n_distinct`: Number of distinct values (**962,611** - matches Ibis).
   - `n_unique`: Number of values that appear **exactly once** in the dataset.
   - Calculation: Values with frequency == 1.
   - Result: **934,133**

## Conclusion
There is no error in the statistical computation of either system. The difference is purely semantic. 

To maintain parity with traditional expectations of "Unique Count" in database contexts, the Ibis-Native Profiler will continue to report **Distinct Values**. However, for users coming from `ydata-profiling`, it is important to note that our `unique` corresponds to their `n_distinct`.

## Verification Script
The following check was performed using Polars on the 1M row sample:
```python
import polars as pl
df = pl.read_parquet('loan_data_1M.parquet')
distinct_count = df['loan_amount'].n_unique() # 962,611
exactly_once = df['loan_amount'].value_counts().filter(pl.col('count') == 1).height # 934,133
```
This confirms the `ydata-profiling` result of 934,133 refers specifically to single-occurrence values.
