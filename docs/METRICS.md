# Ibis Profiler: Technical Reference & Calculations

This document provides a detailed breakdown of how metrics are calculated and how the alert engine identifies potential data quality issues.

---

## 1. Variable Calculations

The profiler uses a multi-pass execution engine to compute statistics efficiently across massive datasets while remaining compatible with SQL-based backends (like DuckDB).

### Core Statistics (Pass 1)
These are computed in a single global aggregation pass using Ibis primitives.

| Metric | Calculation | Type |
| :--- | :--- | :--- |
| `n` | Total number of observations (rows) in the table. | All |
| `n_missing` | Count of `NULL` or `NaN` values. | All |
| `p_missing` | `n_missing / n` | All |
| `n_distinct` | Count of unique values (including `NULL` if applicable). | All |
| `p_distinct` | `n_distinct / n` | All |
| `count` | `n - n_missing` (Total non-missing values) | All |
| `mean` | `sum(x) / count` | Numeric |
| `std` | Standard deviation (Bessel's correction applied). | Numeric |
| `variance` | `std^2` | Numeric |
| `min` / `max` | Minimum and maximum values. | Numeric, DateTime |
| `n_zeros` | Count of values exactly equal to `0`. | Numeric |
| `n_negative` | Count of values `< 0`. | Numeric |
| `n_infinite` | Count of `+/- inf` values (Float only). | Numeric |

### Advanced Statistics (Pass 2)
To avoid "Nested Aggregation" errors in SQL backends (where a metric depends on a previously calculated mean), these are computed using values from Pass 1 as constants.

| Metric | Calculation | Logic |
| :--- | :--- | :--- |
| `skewness` | `mean( ((x - μ) / σ)^3 )` | Standardized 3rd moment. |
| `mad` | `mean( abs(x - μ) )` | Mean Absolute Deviation. |
| `duplicates` | `n - count(distinct_rows)` | Dataset-wide duplicate row count. |

### Quantiles
Calculated via `col.quantile(p)`.
- `5%`, `25%` (Q1), `50%` (Median), `75%` (Q3), `95%`.

### Derived Metrics
| Metric | Calculation | Description |
| :--- | :--- | :--- |
| `range` | `max - min` | Full spread of data. |
| `iqr` | `p75 - p25` | Interquartile range (middle 50%). |
| `cv` | `std / mean` | Coefficient of Variation (relative variability). |
| `is_unique` | `n_distinct == n` | Boolean flag for primary key candidates. |

---

## 2. Alert Engine Logic

The alert engine scans the calculated metrics and triggers warnings based on industry-standard thresholds (aligned with `ydata-profiling`).

### Alert Rules & Thresholds

| Alert Type | Logic / Threshold | Severity |
| :--- | :--- | :--- |
| **CONSTANT** | `n_distinct == 1` | Warning |
| **UNIQUE** | `n_distinct == n` | Info |
| **HIGH_CARDINALITY** | `p_distinct > 0.5` (and not `UNIQUE`) | Warning |
| **MISSING** | `p_missing > 0.05` (More than 5% missing) | Warning |
| **ZEROS** | `p_zeros > 0.05` (More than 5% zeros) | Info |
| **SKEWED** | `abs(skewness) > 20` | Warning |

### Suppression Rules
To reduce noise, the engine applies hierarchical suppression:
1. If a column is **CONSTANT**, all other alerts for that column are suppressed.
2. If a column is **UNIQUE**, the **HIGH_CARDINALITY** alert is suppressed.

---

## 3. Missing Values Visualizations

### Nullity Correlation (Heatmap)
- **Calculation**: For each column, a "nullity mask" is created ($1$ if missing, $0$ if present). We then compute the **Pearson Correlation Coefficient** between these masks.
- **Interpretation**: A correlation of $1.0$ means if Column A is missing, Column B is always missing. This reveals structural dependencies in data collection.

### Nullity Matrix (Sparkline)
- **Calculation**: Samples the first 250 rows.
- **Rendering**: A vertical grid where each column is a variable. Dark marks represent data presence; light gaps represent missingness. This allows users to see if missing data is clustered in specific row ranges (horizontal bands) or specific variables (vertical stripes).

---

## 4. Interaction Engine (Scatter Plots)
- **Calculation**: Samples 1,000 rows.
- **Rendering**: Pairwise scatter plots for all Numeric variables. This helps identify non-linear relationships and clusters that correlation coefficients might miss.
