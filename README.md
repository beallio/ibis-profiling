<p align="center">
  <img src="src/ibis_profiling/assets/img/ibis-profiling-logo.png" width="400" alt="Ibis Profiling Logo">
</p>

# Ibis Profiling

An ultra-high-performance data profiling system built natively for **Ibis**.

## Core Principle: Profiling as Query Compilation

Unlike traditional profiling tools (e.g., `ydata-profiling`) that iterate over columns or load data into local memory (Pandas), **Ibis Profiling** treats profiling as a **query planning problem**. 

It compiles dozens of statistical metrics into a **minimal set of optimized SQL queries** that execute directly in your remote backend (DuckDB, BigQuery, Snowflake, ClickHouse, etc.). This ensures that computation happens where the data lives, enabling the profiling of multi-billion row datasets in seconds rather than hours.

---

## 🚀 Key Features

- **Backend Pushdown:** 100% of the heavy lifting is done by the database engine.
- **Multi-Pass Execution:** Intelligently splits computation into optimized passes to handle complex moments (Skewness, MAD) without backend "nested aggregation" errors.
- **JSON Schema Parity:** Achieves full structural and statistical parity with `ydata-profiling`, allowing drop-in replacement for downstream automated pipelines.
- **High-Fidelity SPA:** Generates a modern Single Page Application (SPA) report with interactive Plotly charts, SVG-based nullity matrices, and alert badges.
- **Scalability:** Profile **10 million rows in < 25 seconds** (Full mode) and **20 million rows in < 50 seconds** (Minimal mode).

---

## 🛡️ Backend Stability & NaN Handling

A critical challenge in database-native profiling is the handling of `NaN` (Not-a-Number) values in floating-point columns. Traditional database aggregations (like `STDDEV_SAMP` in DuckDB) often throw `OutOfRange` errors when encountering `NaN`s.

**Ibis Profiling** implements a **Safe-Aggregation** layer that automatically treats `NaN` values as `NULL` during statistical computation. This ensures:
1. **Zero Crash Policy:** Profiles complete successfully even on messy synthetic or sensor data.
2. **Mathematical Consistency:** Statistics (mean, std, variance) are computed on the subset of valid numeric values, matching the behavior of high-level tools like Pandas while staying within the database.

---

## 📈 Performance Benchmarks

Benchmarks were conducted using a synthetic dataset with 20 columns (mix of numeric, categorical, text, and boolean) on a standard Linux environment using the **DuckDB** backend.

| Dataset Size | Ibis (Min) | Ibis (Full) | ydata (Min) | ydata (Full) | Mem Ibis (Min) | Mem ydata (Min) | Mem Ibis (Full) | Mem ydata (Full) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **10k Rows** | 0.90s | 0.88s | 9.92s | 28.00s | ~3.6 MB | ~74 MB | ~3.2 MB | ~107 MB |
| **50k Rows** | 1.16s | 1.15s | 17.53s | 38.23s | ~3.6 MB | ~293 MB | ~3.2 MB | ~329 MB |
| **500k Rows** | 2.16s | 2.50s | 85.92s | ~2.5m (est) | ~3.6 MB | ~2.5 GB | ~3.6 MB | ~2.8 GB (est) |
| **1M Rows** | 3.15s | 3.52s | 147.24s | ~5m (est) | ~3.2 MB | ~4.8 GB | ~3.2 MB | ~5.2 GB (est) |
| **5M Rows** | 12.23s | 12.38s | ~15m (est) | ~40m (est) | ~3.2 MB | >20 GB (est) | ~3.2 MB | >25 GB (est) |
| **10M Rows** | 27.27s | 24.53s | ~35m (est) | ~1.5h (est) | ~3.6 MB | >40 GB (est) | ~3.2 MB | >50 GB (est) |
| **20M Rows** | 49.17s | 32.15s* | >1h (est) | >3h (est) | ~3.6 MB | >80 GB (est) | ~1.8 MB* | >100 GB (est) |

*Note: 20M Full result (32.15s) was run with 10 columns to avoid OOM. All other benchmarks use 20 columns. ydata-profiling was run in "minimal" mode for larger datasets to avoid OOM errors. Ibis memory usage is nearly constant (< 1MB difference) between Minimal and Full modes.*

### 🔍 Estimation Methodology
Projections for `ydata-profiling` on larger datasets are derived from observed scaling trends:
- **Time (Minimal):** Scaled linearly based on the jump from 500k (85s) to 1M (147s) rows.
- **Time (Full):** Scaled with a factor of ~2.5x - 3x over Minimal mode, consistent with small-sample ratios.
- **Memory:** Scaled linearly based on observed peak usage (~2.5 GB at 500k, ~4.8 GB at 1M), reflecting the overhead of loading the full dataset into Pandas DataFrames.

---

## 🛠 Installation

```bash
uv add ibis-profiling
```

---

## 💻 Usage


### Quick Start (ydata-style API)

```python
import ibis
from ibis_profiling import ProfileReport

# 1. Connect to any Ibis-supported backend
con = ibis.duckdb.connect()
table = con.read_parquet("large_dataset.parquet")

# 2. Generate the profile (Zero-memory overhead)
report = ProfileReport(table)

# 3. Export results
report.to_file("report.html")
report.to_file("report.json")
```

### Advanced Usage

```python
from ibis_profiling import profile

# Get the raw description dictionary
report = profile(table)
stats = report.to_dict()

print(f"Dataset Skewness: {stats['variables']['income']['skewness']}")
```

### Minimal vs. Full Profiling

The `ProfileReport` supports a `minimal` flag (default `False`) to toggle between fast exploratory profiling and deep statistical analysis.

| Feature | Minimal Mode (`minimal=True`) | Full Mode (`minimal=False`) |
| :--- | :--- | :--- |
| **Core Stats** | Count, Mean, Std, Min/Max, Zeros, Nullity. | All Minimal stats. |
| **Advanced Moments** | Skipped. | Skewness, Kurtosis, MAD. |
| **Correlations** | Skipped. | Full Pearson pairwise matrix. |
| **Missing Values** | Count and percentage only. | Nullity Matrix (SVG) and Heatmap. |
| **Duplicates** | Skipped. | Dataset-wide duplicate row count. |
| **Performance** | **Ultra-Fast.** Recommended for datasets > 50M rows. | **Detailed.** Recommended for deep data quality audits. |

---

## 🏗 Architecture

The system is decoupled into five core modules:
1. **Dataset Inspector:** Zero-execution schema analysis.
2. **Metric Registry:** Declarative metric definitions as Ibis expressions.
3. **Query Planner:** The "compiler" that batches compatible expressions into minimal execution plans.
4. **Execution Engine:** Multi-pass dispatcher that handles simple vs. complex aggregations.
5. **Report Builder:** Aggregates and formats raw backend results into high-fidelity JSON/HTML following the canonical YData schema.

---

## 📊 Missing Values Analysis

Move beyond simple counts with advanced pattern detection:
- **Matrix:** A vertical sparkline grid (SVG) visualizing the location of missing values across rows.
- **Heatmap:** Pearson correlation of "nullity" between variables, revealing structural dependencies.

---

## 📏 Metrics & Calculation Reference

This section provides a detailed breakdown of how metrics are calculated and how the alert engine identifies potential data quality issues.

### 1. Variable Calculations

The profiler uses a multi-pass execution engine to compute statistics efficiently across massive datasets while remaining compatible with SQL-based backends (like DuckDB).

#### Core Statistics (Pass 1)
These are computed in a single global aggregation pass using Ibis primitives.

| Metric | Calculation | Type |
| :--- | :--- | :--- |
| `n` | Total number of observations (rows) in the table. | All |
| `n_missing` | Count of `NULL` or `NaN` values. | All |
| `p_missing` | `n_missing / n` | All |
| `n_distinct` | Count of unique values (excluding `NULL`). | All |
| `p_distinct` | `n_distinct / n` | All |
| `count` | `n - n_missing` (Total non-missing values) | All |
| `mean` | `sum(x) / count` (NaNs treated as NULL) | Numeric |
| `std` | Sample standard deviation (Bessel's correction). | Numeric |
| `variance` | `std^2` | Numeric |
| `min` / `max` | Minimum and maximum values. | Numeric, DateTime |
| `zeros` | Count of values exactly equal to `0`. | Numeric |
| `n_negative` | Count of values `< 0`. | Numeric |
| `infinite` | Count of `+/- inf` values (Float only). | Numeric |

#### Advanced Statistics (Pass 2)
To avoid "Nested Aggregation" errors in SQL backends, these are computed using values from Pass 1 as constants.

| Metric | Calculation | Logic |
| :--- | :--- | :--- |
| `skewness` | `mean( ((x - μ) / σ)^3 )` | Standardized 3rd moment. |
| `mad` | `mean( abs(x - μ) )` | Mean Absolute Deviation. |
| `duplicates` | `n - count(distinct_rows)` | Dataset-wide duplicate row count. |

#### Quantiles
Calculated via `col.quantile(p)`.
- `5%`, `25%` (Q1), `50%` (Median), `75%` (Q3), `95%`.

---

### 2. Alert Engine Logic

The built-in alert engine scans the calculated metrics and triggers warnings based on industry-standard thresholds (aligned with `ydata-profiling`).

| Alert Type | Logic / Threshold | Severity |
| :--- | :--- | :--- |
| **CONSTANT** | `n_distinct == 1` | warning |
| **UNIQUE** | `n_distinct == n` | warning |
| **HIGH_CARDINALITY** | `p_distinct > 0.5` (and not `UNIQUE`, Categorical only) | warning |
| **MISSING** | `p_missing > 0.05` | info |
| **ZEROS** | `p_zeros > 0.10` | info |
| **SKEWED** | `abs(skewness) > 20` | info |

**Suppression Rules:**
1. If a column is **CONSTANT**, all other alerts for that column are suppressed.
2. If a column is **UNIQUE**, the **HIGH_CARDINALITY** alert is suppressed.

---

## 🤝 Contributing

Contributions are welcome! Please ensure all pull requests pass the `uv run pytest` suite and adhere to the TDD principles defined in our `.protocol`.
