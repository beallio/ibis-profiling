<p align="center">
  <img src="https://raw.githubusercontent.com/beallio/ibis-profiling/main/src/ibis_profiling/assets/img/ibis-profiling-logo.png" width="400" alt="Ibis Profiling Logo">
</p>

# Ibis Profiling

[![PyPI version](https://badge.fury.io/py/ibis-profiling.svg)](https://badge.fury.io/py/ibis-profiling)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An ultra-high-performance data profiling system built natively for **Ibis**.

## Core Principle: Profiling as Query Compilation

Unlike traditional profiling tools (e.g., `ydata-profiling`) that load data into local memory (Pandas), **Ibis Profiling** treats profiling as a **query planning problem**. 

It compiles dozens of statistical metrics into a **minimal set of optimized SQL queries** that execute directly in your remote backend (DuckDB, BigQuery, Snowflake, ClickHouse, etc.). This ensures that computation happens where the data lives, enabling the profiling of multi-billion row datasets in seconds rather than hours.

---

## 🖼️ Preview

### Overview Dashboard
![Overview Screenshot](https://raw.githubusercontent.com/beallio/ibis-profiling/main/src/ibis_profiling/assets/img/report_overview.png)

### Variable Detail View
![Variables Screenshot](https://raw.githubusercontent.com/beallio/ibis-profiling/main/src/ibis_profiling/assets/img/report_variables.png)

### Missing Values Analysis
![Missing Screenshot](https://raw.githubusercontent.com/beallio/ibis-profiling/main/src/ibis_profiling/assets/img/report_missing.png)


---

## 🚀 Key Features

- **Backend Pushdown:** 100% of the heavy lifting is done by the database engine.
- **Multi-Pass Execution:** Intelligently splits computation into optimized passes to handle complex moments (Skewness, MAD) without backend "nested aggregation" errors.
- **JSON Schema Parity:** Achieves full structural and statistical parity with `ydata-profiling`, allowing drop-in replacement for downstream automated pipelines.
- **Modern SPA Report:** Generates a lightweight Single Page Application (SPA) with a modern React-based UI.
- **Adjustable Themes:** Includes built-in support for **Dark**, **Light**, and **High Contrast** modes with persistent user settings.
- **Auto-Categorical Detection:** Intelligent heuristics automatically reclassify low-cardinality integers (e.g., status codes, term months) as categorical for better visualization.
- **DateTime Distribution:** Full support for temporal histograms and distribution analysis.
- **Excel Support:** Directly profile Excel files (.xlsx, .xls, .xlsb) using high-performance Rust-based parsing.
- **Scalability:** Profile **5 million rows in < 12 seconds** (Minimal mode) and **< 22 seconds** (Full mode).
- **Python Compatibility:** Fully tested on **Python 3.11 through 3.14.3** (Core functionality).

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
| **10k Rows** | 0.89s | 1.40s | 9.94s | 28.38s | ~2.4 MB | ~74 MB | ~4.5 MB | ~107 MB |
| **25k Rows** | 1.03s | 1.57s | 12.20s | 30.47s | ~2.1 MB | ~154 MB | ~4.4 MB | ~188 MB |
| **50k Rows** | 1.22s | 1.82s | 16.63s | 35.10s | ~2.0 MB | ~284 MB | ~4.4 MB | ~324 MB |
| **500k Rows** | 2.29s | 3.56s | 91.93s | ~3m (est) | ~2.0 MB | ~2.5 GB | ~4.4 MB | ~2.8 GB (est) |
| **1M Rows** | 3.14s | 5.44s | 166.31s | ~6m (est) | ~2.1 MB | ~4.9 GB | ~4.4 MB | ~5.3 GB (est) |
| **5M Rows** | 10.69s | 17.88s | ~14m (est) | ~45m (est) | ~2.0 MB | >20 GB (est) | ~4.4 MB | >25 GB (est) |
| **10M Rows** | 20.64s | 21.29s* | ~28m (est) | ~1.5h (est) | ~2.4 MB | >40 GB (est) | ~2.6 MB* | >50 GB (est) |
| **20M Rows** | 43.98s | 8.77s** | >1h (est) | >3h (est) | ~2.4 MB | >80 GB (est) | ~1.0 MB** | >100 GB (est) |

*Notes:
- 10M Full (21.29s) used 10 columns.
- 20M Full (8.77s) used 5 columns.
- All other benchmarks use 20 columns.
- Ibis memory usage is nearly constant and extremely low compared to ydata-profiling due to database-native pushdown.*

### 🔍 Estimation Methodology
Projections for `ydata-profiling` on larger datasets are derived from observed scaling trends:
- **Time (Minimal):** Scaled linearly based on the jump from 500k (92s) to 1M (166s) rows.
- **Time (Full):** Scaled with a factor of ~2.5x - 3x over Minimal mode, consistent with small-sample ratios.
- **Memory:** Scaled linearly based on observed peak usage (~2.5 GB at 500k, ~4.9 GB at 1M), reflecting the overhead of loading the full dataset into Pandas DataFrames.

---

## 🛠 Installation

Install **Ibis Profiling** directly from PyPI:

### Using [uv](https://github.com/astral-sh/uv) (Recommended)
```bash
uv add ibis-profiling
```

### Using pip
```bash
pip install ibis-profiling
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

# 2. Generate the report with custom title
report = ProfileReport(table, title="Loan Analysis Report")

# 3. Export results
report.to_file("report.html")
```

### Excel Ingestion

```python
from ibis_profiling import ProfileReport

# Directly profile Excel files with high-performance parsing
report = ProfileReport.from_excel("data.xlsx")
report.to_file("excel_report.html")
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
| **Table Metadata** | Estimated Memory/Record Size. | Same as Minimal. |
| **Advanced Moments** | Skipped. | Skewness, Kurtosis, MAD. |
| **Correlations** | Skipped. | Pearson and Spearman matrices. |
| **Advanced Analysis** | Skipped. | Extreme Values, Monotonicity, Text Lengths. |
| **Visualizations** | **Histograms (Numeric/DateTime)**, Summary only. | Nullity Matrix (SVG), Heatmap, **Scatter Plots**. |
| **Duplicates** | Skipped. | Dataset-wide duplicate row count. |
| **Performance** | **Ultra-Fast.** Recommended for datasets > 50M rows. | **Detailed.** Recommended for deep data quality audits. |

## 📦 Report Export & Layouts

By default, `ibis-profiling` minifies the generated HTML report to reduce file size (typically by 15-20%) without compromising functionality.

### Custom Themes & Themes
The `to_file` method supports a `theme` parameter to choose between different report layouts:

```python
# Modern React SPA (Default)
report.to_file("report.html", theme="default")

# Classic layout for ydata-profiling parity
report.to_file("report.html", theme="ydata-like")
```

### Minification
To generate a human-readable (non-minified) report, set `minify=False`:

```python
# Save as formatted HTML
report.to_file("report.html", minify=False)
```

## 🎨 Interactive React SPA

The default report is a fully interactive React Single Page Application (SPA) providing a modern user experience:

- **Instant Search:** Quickly filter variables by name or type.
- **Theme Toggle:** Switch between **Dark**, **Light**, and **High Contrast** modes with persistent settings.
- **Alert Filtering:** Interactive dashboard to filter data quality alerts by severity (Warning vs. Info).
- **Responsive Charts:** High-fidelity SVG and Canvas-based visualizations (Histograms, Heatmaps, Scatter Plots).

---

## 🏗 Architecture & Backend Support

The system is decoupled into five core modules designed for maximum backend compatibility:
1. **Dataset Inspector:** Zero-execution schema analysis.
2. **Metric Registry:** Declarative metric definitions as Ibis expressions.
3. **Query Planner:** The "compiler" that batches compatible expressions into minimal execution plans.
4. **Execution Engine:** Multi-pass dispatcher that handles simple vs. complex aggregations.
5. **Report Builder:** Aggregates and formats raw backend results into high-fidelity JSON/HTML.

**Supported Backends:** 100% compatibility with all **Ibis** backends including DuckDB, Snowflake, BigQuery, ClickHouse, Postgres, Polars, and more.

---

## 📊 Missing Values Analysis

Move beyond simple counts with advanced pattern detection and visualization:
- **Missing Matrix:** A vertical sparkline grid (SVG) visualizing the exact location of missing values across rows, allowing you to spot temporal or structural gaps.
- **Nullity Heatmap:** Pearson correlation of "nullity" between variables, revealing structural dependencies (e.g., when Column A is missing, Column B is also 90% likely to be missing).

---

## 🔍 Pairwise Interactions

Explore dependencies between numeric variables with high-performance scatter plots:
- **Automatic Selection:** Intelligently samples the dataset to maintain 60FPS interactivity even with millions of rows.
- **Correlation-Driven:** Highlights pairs with high statistical significance to surface hidden patterns.
- **Canvas-Optimized:** Uses HTML5 Canvas for smooth rendering of thousands of data points directly in the browser.

---

## 📏 Metrics & Calculation Reference

### 1. Variable Calculations

The profiler uses a multi-pass execution engine to compute statistics efficiently across massive datasets while remaining compatible with SQL-based backends.

#### Core Statistics (Pass 1)
| Metric | Calculation | Type |
| :--- | :--- | :--- |
| `n` | Total number of observations (rows) in the table. | All |
| `n_missing` | Count of `NULL` or `NaN` values. | All |
| `p_missing` | `n_missing / n` | All |
| `n_distinct` | Count of unique values (excluding `NULL`). | All |
| `mean` | `sum(x) / count` (NaNs treated as NULL) | Numeric |
| `std` | Sample standard deviation (Bessel's correction). | Numeric |
| `min` / `max` | Minimum and maximum values. | Numeric, DateTime |
| `histogram` | Binned distribution (Numeric/DateTime) or Top Values (Categorical). | All |

#### Advanced Statistics (Pass 2)
To avoid "Nested Aggregation" errors in SQL backends, these are computed using values from Pass 1 as constants.
| Metric | Calculation | Logic |
| :--- | :--- | :--- |
| `skewness` | `mean( ((x - μ) / σ)^3 )` | Standardized 3rd moment. |
| `mad` | `mean( abs(x - μ) )` | Mean Absolute Deviation. |
| `n_duplicates` | `n - count(distinct_rows)` | Dataset-wide duplicate row count. |

### 2. Alert Engine Logic

| Alert Type | Logic / Threshold | Severity |
| :--- | :--- | :--- |
| **CONSTANT** | `n_distinct == 1` | warning |
| **UNIQUE** | `n_distinct == n` | warning |
| **HIGH_CARDINALITY** | `p_distinct > 0.5` (Categorical only) | warning |
| **MISSING** | `p_missing > 0.05` | info |
| **ZEROS** | `p_zeros > 0.10` | info |
| **SKEWED** | `abs(skewness) > 10` | info |

---

## 📄 License
Ibis Profiling is licensed under the **MIT License**. See `LICENSE` for details.
