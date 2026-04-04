<p align="center">
  <img src="https://raw.githubusercontent.com/beallio/ibis-profiling/main/src/ibis_profiling/assets/img/ibis-profiling-logo.png?cacheBuster=1" width="400" alt="Ibis Profiling Logo">
</p>

# Ibis Profiling

[![PyPI version](https://badge.fury.io/py/ibis-profiling.svg?cacheBuster=15)](https://badge.fury.io/py/ibis-profiling)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An ultra-high-performance data profiling system built natively for **Ibis**.

## Core Principle: Profiling as Query Compilation

Unlike traditional profiling tools (e.g., `ydata-profiling`) that load data into local memory (Pandas), **Ibis Profiling** treats profiling as a **query planning problem**. 

It compiles dozens of statistical metrics into a **minimal set of optimized SQL queries** that execute directly in your remote backend (DuckDB, BigQuery, Snowflake, ClickHouse, etc.). This ensures that computation happens where the data lives, enabling the profiling of multi-billion row datasets in seconds rather than hours.

---

## 🖼️ Preview

### Overview Dashboard
![Overview Screenshot](https://raw.githubusercontent.com/beallio/ibis-profiling/main/src/ibis_profiling/assets/img/report_overview.png?cacheBuster=1)

### Variable Detail View
![Variables Screenshot](https://raw.githubusercontent.com/beallio/ibis-profiling/main/src/ibis_profiling/assets/img/report_variables.png?cacheBuster=1)

### Missing Values Analysis
![Missing Screenshot](https://raw.githubusercontent.com/beallio/ibis-profiling/main/src/ibis_profiling/assets/img/report_missing.png?cacheBuster=1)


---

## 🎯 Use Cases

- **Financial Data Integrity Audit:** Quickly identify missing values, outliers, and distribution skew in multi-million row transaction logs without moving data to your local machine.
- **High-Volume ML Preprocessing:** Profile billion-row datasets directly in BigQuery or Snowflake to identify feature leakage (via correlations) and category imbalances before starting expensive training jobs.
- **Automated Data Quality Gates:** Integrate `to_dict()` output into CI/CD pipelines to automatically fail builds if data quality alerts (e.g., CONSTANT or HIGH_CARDINALITY) are triggered on new production batches.
- **Data Migration Validation:** Compare profile summaries of source and destination databases to ensure statistical parity after a large-scale migration.

---

## 🚀 Key Features

- **Backend Pushdown:** 100% of the heavy lifting is done by the database engine.
- **Multi-Pass Execution:** Intelligently splits computation into optimized passes to handle complex moments (Skewness, MAD) without backend "nested aggregation" errors.
- **JSON Schema Parity:** Achieves full structural and statistical parity with `ydata-profiling`, allowing drop-in replacement for downstream automated pipelines.
- **Logical Type Inference:** Built-in semantic detection for common data patterns (**Email**, **URL**, **IP Address**, **Phone Number**, **Credit Card**, **SSN**, **JSON**, **MAC Address**, **File Path**, **Country Code**, **Complex**, **Geometry (WKT)**, **Currency**, **IBAN**, **SWIFT/BIC**, **Tax ID (EIN)**, **ISIN**, **Stock Ticker**, **Age**, **Gender**, **Language Code**, **Passport**, **US State**, **US Territory**, **US Military Mail**, **US Zip Code**, **UUID**, **CUID**, **NanoID**, **Boolean**, **Ordinal**, **Count**) even when stored as strings.
- **Alert Engine:** Heuristic-based warnings for **Unique**, **Constant**, **Skewed**, **Zeros**, **Missing**, and **Empty** (empty string) values.
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

### Command Line Interface (CLI)

You can profile datasets directly from the terminal without writing any Python code.

#### Basic Usage
```bash
# If installed locally
uv run ProfileReport --file-path data.csv --output report.html

# One-off run (no installation required)
uv run --with ibis-profiling,ibis-framework[duckdb] ProfileReport --file-path data.parquet
```

#### CLI Options
| Option | Shortcut | Description |
| :--- | :--- | :--- |
| `--file-path` | `-f` | **(Required)** Path to input file (CSV, Parquet, Excel). |
| `--output` | `-o` | Path to output file (default: `report.html`). |
| `--title` | `-t` | Custom report title. |
| `--minimal` | | Generate a minimal report (faster). |
| `--theme` | | Report theme: `default` or `ydata-like`. |
| `--format` | | Force output format: `html` or `json`. |
| `--correlations` | | Explicitly enable or disable correlations (`--correlations` / `--no-correlations`). |
| `--monotonicity` | | Explicitly enable or disable monotonicity checks (`--monotonicity` / `--no-monotonicity`). |
| `--monotonicity-threshold` | | Row count threshold above which monotonicity is skipped (default: 100,000). |
| `--monotonicity-order-by` | | Column name to order by for deterministic monotonicity checks. Required to enable monotonicity. |
| `--n-unique-threshold` | | Row count threshold above which `n_unique` (singletons) calculation is skipped (default: 50,000,000). |
| `--duplicates` | | Explicitly enable or disable duplicate row checks (`--duplicates` / `--no-duplicates`). |
| `--offline` / `--online` | | Whether to bundle all JS/CSS assets in the HTML for offline viewing (default: `--offline`). |
| `--global-batch-size` | | Maximum number of metrics to compute in a single global aggregate query (default: 500). |

---

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

### ⚙️ Advanced Configuration

Fine-tune the profiler's performance and behavior using additional parameters in `ProfileReport()`:

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `minimal` | `False` | Enable faster profiling by skipping expensive metrics (correlations, interactions). |
| `parallel` | `False` | Execute independent backend queries in parallel using a thread pool. (Fallback to sequential if backend is not thread-safe). |
| `pool_size` | `4` | Number of concurrent worker threads for parallel execution. |
| `use_sketches` | `False` | Use hyperloglog/sketches for `approx_nunique` when supported by the backend (e.g., DuckDB). Greatly speeds up large cardinality checks. |
| `max_interaction_pairs` | `10` | Limit pairwise scatter plots to the Top N most interactive numeric variables. |
| `correlations_sampling_threshold` | `1,000,000` | Row count threshold above which Spearman correlation uses sampling. |
| `correlations_sample_size` | `1,000,000` | Number of rows used when correlation sampling is active. |
| `correlations` | `True` | Explicitly enable/disable all correlation matrices. |
| `monotonicity` | `True` | Explicitly enable/disable monotonicity checks. |
| `monotonicity_threshold` | `100,000` | Row count threshold above which monotonicity is skipped by default. |
| `duplicates_threshold` | `50,000,000` | Row count threshold above which duplicate check is skipped by default. |
| `n_unique_threshold` | `50,000,000` | Row count threshold above which exact `n_unique` (singleton) calculation is skipped. |
| `global_batch_size` | `500` | Maximum number of aggregate expressions per backend query. |
| `compute_duplicates` | `True` | Explicitly enable/disable duplicate row detection. |

#### 🔍 Interaction Pruning & "Interactivity"

To maintain high performance and keep HTML reports lightweight, `ibis-profiling` uses an automated pruning strategy for pairwise scatter plots:

- **Interactivity Definition**: "Interactivity" is defined as the **average absolute Pearson correlation** of a column with all other numeric variables.
- **Why are variables limited?**: We determine the number of columns to include ($N$) by the requested `max_interaction_pairs` (default 10). A limit of 10 variables results in up to 45 pairwise scatter plots ($10 \times 9 / 2 = 45$).
- **How are fields pruned?**:
    1.  **Scoring**: Every numeric column is assigned a score based on its average absolute correlation with others.
    2.  **Ranking**: Columns are ranked by this score. High scores indicate variables that likely have the most meaningful relationships.
    3.  **Selection**: Only the Top $N$ columns are kept. All other columns are pruned from the interactions pass to prevent massive HTML bloat and long compute times.

---

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

### Export Options
Both `to_file` and `to_html` support the following parameters:

| Parameter | Default | Description |
| :--- | :--- | :--- |
| `theme` | `"default"` | Report theme: `"default"` (React SPA) or `"ydata-like"`. |
| `minify` | `True` | Whether to minify the output HTML. |
| `offline` | `True` | If `True`, all JS/CSS assets are bundled directly in the HTML for offline viewing and enhanced security. If `False`, assets are loaded from public CDNs with SRI and CSP. |

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

Ibis Profiling uses a multi-pass execution engine to compute statistics efficiently across massive datasets while remaining compatible with SQL-based backends. Below is the comprehensive breakdown of every metric presented in the generated reports.

### 1. Dataset Statistics (Overview)

| Metric | Calculation / Derivation |
| :--- | :--- |
| **Number of variables** | `n_var` = Total columns in the dataset schema. |
| **Number of observations** | `n` = Total rows in the dataset. |
| **Missing cells** | `n_cells_missing` = Sum of all `NULL` or `NaN` values across all variables. |
| **Missing cells (%)** | `p_cells_missing` = `n_cells_missing / (n * n_var)` |
| **Duplicate rows** | `n_duplicates` = `n - count(distinct_rows)`. Evaluated dataset-wide. |
| **Duplicate rows (%)** | `p_duplicates` = `n_duplicates / n` |
| **Total size in memory** | Estimated payload footprint calculated via `DatasetInspector`, using conservative type heuristics (e.g., `Int64` = 8 bytes, `String` = 20 bytes) multiplied by `n`. |
| **Average record size** | `memory_size / n` |
| **Variable types** | Count of variables classified as `Numeric`, `Categorical`, `Boolean`, or `DateTime`. Low-cardinality numerics may be automatically reclassified as `Categorical`. |

### 2. Variable Statistics

#### Core Metrics & Properties

| Metric | Calculation | Type |
| :--- | :--- | :--- |
| **Distinct** | `n_distinct` = Count of unique values (excluding `NULL`). | All |
| **Distinct (%)** | `p_distinct` = `n_distinct / n` | All |
| **Missing** | `n_missing` = Count of `NULL` or `NaN` values. | All |
| **Missing (%)** | `p_missing` = `n_missing / n` | All |
| **Infinite** | `n_infinite` = Count of `inf` or `-inf` values. | Numeric |
| **Infinite (%)** | `p_infinite` = `n_infinite / n` | Numeric |
| **Mean** | `sum(x) / count(x)`. Safe-aggregation treats `NaN` as `NULL`. | Numeric |
| **Minimum / Maximum** | `min(x)` and `max(x)`. | Num, Date |
| **Zeros** | `n_zeros` = Count of values strictly equal to `0`. | Numeric |
| **Zeros (%)** | `p_zeros` = `n_zeros / n` | Numeric |
| **Negative** | `n_negative` = Count of values `< 0`. | Numeric |
| **Negative (%)** | `p_negative` = `n_negative / n` | Numeric |
| **Hashable** | `True` if the datatype supports hashing (excludes Arrays, Maps, Structs). | All |
| **Length (Max, Mean, Min)** | Character length aggregations: `max(length(x))`, `mean(length(x))`, `min(length(x))`. | Text, Cat |

#### Quantile & Descriptive Statistics (Numeric)
*(Note: Complex moments use values from Pass 1 (mean, std) as constants to avoid "Nested Aggregation" backend errors).*

| Metric | Calculation | Logic |
| :--- | :--- | :--- |
| **Standard Deviation** | `std(x)` | Sample standard deviation (Bessel's correction). |
| **Variance** | `var(x)` | Sample variance. |
| **Coefficient of Variation** | `cv` = `std / mean` | Standardized measure of dispersion. |
| **Kurtosis** | `kurtosis(x)` | Standardized 4th moment (tail heaviness). |
| **Skewness** | `mean( ((x - μ) / σ)^3 )` | Standardized 3rd moment (asymmetry). |
| **MAD** | `mean( abs(x - μ) )` | Mean Absolute Deviation. |
| **Sum** | `sum(x)` | Aggregate sum of all valid numeric values. |
| **Monotonicity** | Logical evaluation | Checks if column values strictly or non-strictly increase/decrease. |
| **Percentiles (5%, Q1, Median, Q3, 95%)** | Backend quantile approximation functions. | Provides dataset distribution shape without loading data. |
| **Range** | `max - min` | Total span of values. |
| **Interquartile Range (IQR)** | `Q3 - Q1` | Spread of the middle 50% of values. |

### 3. Visualizations & Advanced Matrices

- **Histograms:** 
  - *Numeric/DateTime:* Computed using equi-width binning pushed down to the query engine.
  - *Categorical:* Fetches the top distinct values via `value_counts()`.
- **Length Distribution:** Categorical charts mapping the character length distribution of text columns.
- **Nullity Matrix (Missing Data):** Dense SVG sparkline visualization representing data completeness. Evaluated over the sampled rows.
- **Nullity Heatmap:** Pearson correlation of `nullity` between all variables. Reveals structural dependencies (e.g., if Column A is missing, Column B is highly likely to also be missing).
- **Interactions (Scatter Plots):** Automated, high-performance HTML5 Canvas scatter plots. The engine scores numeric columns by their average absolute Pearson correlation and samples pairs of the highest-scoring (most interactive) columns.
- **Correlations:** Computes both **Pearson** (linear relationship) and **Spearman** (monotonic relationship) matrices. Uses intelligent sampling if datasets exceed `1,000,000` rows by default.

### 4. Alert Engine Logic

The report generates heuristic warnings (Alerts) to flag potential data quality issues immediately.

| Alert Type | Logic / Threshold | Severity |
| :--- | :--- | :--- |
| **CONSTANT** | `n_distinct == 1` | warning |
| **UNIQUE** | `n_distinct == n` | warning |
| **HIGH_CARDINALITY** | `p_distinct > 0.5` (Categorical only) | warning |
| **MISSING** | `p_missing > 0.05` | info |
| **ZEROS** | `p_zeros > 0.10` | info |
| **SKEWED** | `abs(skewness) > 10` | info |

---

## 📂 Project Structure & Examples

To see **Ibis Profiling** in action, you can explore the pre-generated reports in the `examples/` directory:

- **[Full Example Report](https://raw.githack.com/beallio/ibis-profiling/main/examples/html/full_report.html):** A comprehensive profile including all advanced metrics, correlations, and interactions.
- **[Minimal Example Report](https://raw.githack.com/beallio/ibis-profiling/main/examples/html/minimal_report.html):** A lightweight version optimized for speed and large-scale datasets.
- **[Raw JSON Output](https://github.com/beallio/ibis-profiling/tree/main/examples/json):** View the structured data used to drive the React-based frontend reports.

```text
ibis-profiling/
├── examples/             # Sample profiling reports (HTML/JSON)
├── scripts/              # Performance benchmarks and data generation
├── src/ibis_profiling/   # Core engine, metrics, and report templates
└── tests/                # Comprehensive test suite (TDD-driven)
```

---

## 📄 License
Ibis Profiling is licensed under the **MIT License**. See `LICENSE` for details.
