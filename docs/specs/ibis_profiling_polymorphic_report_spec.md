# Ibis Profiling: Polymorphic Report Specification

This document defines the behavioral and visual rules for `ibis-profiling` reports. It ensures the UI maximizes the utility of the "Full" JSON payload while gracefully degrading to a functional "Minimal" view when data is absent.

---

## 1. Core Principle: Graceful Degradation

The report is **data-driven** and **polymorphic**. No section or component should throw an error if its data is missing. Instead, it must follow these rules:
1.  **Hide if Empty:** If a top-level key (e.g., `correlations`, `missing`, `alerts`) is empty or null, the corresponding navigation item and section are hidden.
2.  **Collapse if Optional:** Secondary details within a section (e.g., `extreme_values`, `kurtosis`) are omitted if not present in the payload.
3.  **Null-Safety:** All statistical values are processed through a formatter that converts `null` or `NaN` to a user-friendly string (e.g., `"Null"` or `"-"`).

---

## 2. Section-Level Logic

### 2.1. Dataset Overview (`table`)
| Component | Data Requirement | Minimal Fallback |
| :--- | :--- | :--- |
| KPI Banner | `n`, `n_var`, `memory_size`, `p_cells_missing` | Always rendered. Values show `0` or `N/A` if missing. |
| Duplicates KPI | `p_duplicates` | Hidden if `p_duplicates` is not provided. |
| Variable Types | `types` (Object) | Shows "No type data" if `types` is empty. |

### 2.2. Alerts (`alerts`)
- **Presence:** Render the "System Alerts" section only if `alerts.length > 0`.
- **Filtering:** Users can filter by column name; if no alerts match the search, the alert section displays "No alerts for selected criteria."

### 2.3. Variables (`variables`)
The `VariableCard` is the most polymorphic component. It adapts to the inferred `type` and available metrics.

#### Visualizations
- **Histogram:** Rendered if `histogram` object exists and has data.
    - *Numerical:* Vertical bars with tooltips.
    - *Categorical:* Horizontal progress bars.
- **Length Distribution:** Rendered only for `Categorical` types if `length_histogram` is present.

#### Metric Groups (Toggleable or Inlined)
| Group | Mode | Trigger Keys |
| :--- | :--- | :--- |
| **Common** | Both | `n_distinct`, `n_missing`, `p_missing` |
| **Quantiles** | Both | `min`, `max`, `5%`, `25%`, `50%`, `75%`, `95%` |
| **Moments** | Both | `mean`, `std`, `variance`, `kurtosis` |
| **Shape** | **Full** | `skewness`, `mad`, `iqr`, `cv`, `range` |
| **Extreme Values**| Both | `extreme_values_smallest`, `extreme_values_largest` |

### 2.4. Missing Values (`missing`)
- **Navigation:** Link hidden if `missing` is null or empty.
- **Section Rendering:**
    - **Count Bar Chart:** Uses `missing.bar`.
    - **Matrix (Sample):** Uses `missing.matrix`. If missing, this specific sub-component is hidden.
    - **Heatmap:** Uses `missing.heatmap`. If missing (e.g., < 2 columns with nulls), this sub-component is hidden.

### 2.5. Correlations (`correlations`)
- **Navigation:** Link hidden if `correlations` is null or empty.
- **Algorithm Switcher:** Render a tab/button list for each key in `correlations` (e.g., `pearson`, `spearman`). If only one exists, the switcher is hidden.
- **Matrix View:** Renders the heatmap grid. `Null` values in the matrix are rendered as blank cells.

### 2.6. Sample Data (`sample`)
- **Navigation:** Link hidden if `sample` is null or empty.
- **Table:** Renders `sample.head`. If `sample.tail` is also present (Future), it appends it with a separator.

---

## 3. Formatting Rules

To maintain visual parity across "Full" and "Minimal" reports, the following formatting rules are mandatory:

1.  **Null Representation:** `NaN`, `Inf`, and `null` values must be rendered as `"Null"` (italicized in tables) or `"-"` (in metric lists).
2.  **Number Precision:**
    *   **Percentages:** 1 decimal place (`95.4%`).
    *   **Floats:** 3-4 decimal places (`0.1234`).
    *   **Integers:** Locale-aware formatting (`1,234,567`).
3.  **Memory:** Formatted to human-readable units (`B`, `KiB`, `MiB`, `GiB`).

---

## 4. Mode-Switching (Implementation Detail)

The UI does not need a "mode" flag. It should use **Feature Detection**:

```javascript
// Example React logic for polymorphism
const hasShapeMetrics = variable.skewness !== undefined;
const hasMissingHeatmap = data.missing?.heatmap?.matrix?.length > 0;

return (
  <>
    {hasShapeMetrics && <ShapeMetricsPanel data={variable} />}
    {hasMissingHeatmap && <MissingHeatmap data={data.missing.heatmap} />}
  </>
);
```

By following this spec, the report automatically scales its depth based on whether the Python engine ran in `minimal=True` or `minimal=False` mode.
