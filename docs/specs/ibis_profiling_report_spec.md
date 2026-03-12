# Product & Technical Specifications: Ibis Profiling Dashboard

## 1. Overview & Architecture

The Ibis Profiling Dashboard is a modern, interactive, and self-contained web application designed to visualize structured data profiling reports.

- **Delivery Format:** Single-file HTML (`index.html`). Zero build steps or local development environment required. It runs entirely in the browser.
- **Framework:** React 18, loaded asynchronously via `esm.sh` and Import Maps.
- **Compilation:** In-browser JSX transpilation using Babel Standalone.
- **Styling:** Tailwind CSS (loaded via CDN).
- **Icons:** Lucide React.
- **State Management:** Native React Hooks (`useState`, `useMemo`).
- **Data Ingestion:** Driven by a strictly typed JSON payload (`REPORT_DATA`). The UI is highly polymorphic, automatically collapsing or hiding sections if the corresponding data is absent or `NaN`.

## 2. Design System & UI/UX

The application utilizes a multi-theme design system, allowing users to toggle between different visual modes.

- **Adjustable Themes:**
    - **Dark (Default):** Tailwind's slate scale (`slate-950` background, `slate-900` cards).
    - **Light:** Clean, high-contrast light mode (`slate-50` background, `white` cards).
    - **High Contrast:** Strictly black and zinc palette for maximum accessibility.
- **Persistence:** User theme selection is stored in `localStorage` and persists across sessions.
- **Typography:** Sans-serif for general UI and reading text; strictly `font-mono` for all statistical values, table data, and labels to ensure vertical alignment of digits.
- **Semantic Colors:**
    - **Blue:** Primary interactions, positive correlations, standard distributions.
    - **Red:** Missing data warnings, negative correlations.
    - **Green:** 100% data completeness, memory size metrics.
    - **Purple/Yellow:** Unique constraints, high cardinality alerts.
- **Responsiveness:**
    - **Desktop:** Fixed left sidebar with full navigation.
    - **Mobile/Tablet:** Bottom fixed navigation bar with icon-first design.
- **Custom Scrollbars:** Styled scrollbars matched to the slate theme for a cohesive, premium feel.
- **Asset Fallbacks:** Image elements (like the sidebar logo) include `onError` event handlers to gracefully degrade to inline SVG icons if local assets are missing.

## 3. Polymorphic Navigation & Features

The application dynamically builds its navigation based on the presence of keys in the JSON payload.

### A. Overview Tab (Always Active)
- **KPI Banner:** Displays 4 top-level metrics: Total Rows, Total Variables, Missing Cells (%), and Memory Size.
- **System Alerts:** A grid of alert badges (Unique, Constant, High Cardinality, Missing) conditionally styled based on severity.
- **Variable Quick View:** Grid of mini-cards for every variable in the dataset.
    - Shows Variable Name, Data Type, Missingness percentage.
    - Renders a miniature inline sparkline/histogram of the variable's distribution.
    - Clicking a card dynamically searches for that variable and routes the user to the Variables tab.

### B. Variables Tab
- **Global Search:** A sticky search bar filters the variable list by name in real-time.
- **Dynamic Visualizations:**
    - **Numeric Data:** Renders vertical `NumericHistogram` charts.
    - **Categorical/Boolean Data:** Renders horizontal `CategoricalChart` progress bars.
- **Data Cleaning:** Bins labeled "None", "Null", or "NaN" are programmatically filtered out of charts to prevent skewing visual distributions.
- **Statistical Sections:** Renders distinct panels based on available data:
    - **Core Metrics:** Mean, Min, Max, Std Dev, Lengths.
    - **Data Properties:** Zeros, Negatives, Infinites, Monotonicity.
    - **Shape & Scale:** Range, IQR, Coefficient of Variation (CV), MAD.
    - **Advanced Stats:** Skewness, Kurtosis, Variance.
    - **Extreme Values:** Lists the Top 5 smallest and Top 5 largest values if provided.

### C. Missing Tab (Conditional)
- **Zero-Missing State:** Displays a success banner if data is 100% complete.
- **Missing Counts:** Horizontal bar chart visualizing the raw count of missing values per column.
- **Nullity Matrix (Missingno-style):**
    - A high-performance, inline SVG visualization mapping data presence (dark blocks) vs missing data (gaps) for the first 250 rows.
    - **Auto-Transposition:** Automatically detects if matrix data is supplied in column-oriented format (`[columns][rows]`) and transposes it to `[rows][columns]` for vertical rendering.
    - **Completeness Sparkline:** Calculates row-by-row density and draws a continuous sparkline on the right axis to show overall data health.
- **Nullity Heatmap:** A correlation matrix specifically showing the Pearson correlation of nullity between variables.

### D. Correlations Tab (Conditional)
- **Matrix Toggle:** Allows users to switch between different correlation algorithms (e.g., Pearson, Spearman, Auto) if multiple are provided.
- **Visualization:**
    - Renders a tabular grid.
    - Values are shaded based on correlation strength and direction (Red = Negative, Blue = Positive).
    - Opacity scales with the absolute value of the correlation (closer to 0 is transparent, closer to 1/-1 is solid).
    - `NaN` values are handled gracefully and rendered as blank/transparent cells.

### E. Duplicates Tab (Conditional)
- Dedicated space to visualize rows that are exact duplicates across all variables (UI structure built, awaits full data population).

### F. Sample Data Tab (Conditional)
- **Tabular Preview:** Transposes column-oriented JSON sample data (`{ "col1": [val1, val2], "col2": [val1, val2] }`) into a standard HTML table row format.
- Null/NaN values are italicized and highlighted in red for easy spotting.
- Long text strings are truncated with ellipsis to prevent table blowout.

## 4. Custom Visualization Components

To avoid the bloat of external charting libraries (like Chart.js or D3), all visualizations are built using DOM elements and inline SVGs.

- **NumericHistogram:** Utilizes CSS flexbox. Bar heights are calculated as a percentage of the maximum count in the dataset. Includes hover tooltips mapping bins to exact counts.
- **CategoricalChart:** Uses layered div elements to create horizontal progress bars. Limited to displaying the top 10 categories to maintain UI cleanliness.
- **CorrelationMatrixComponent:** Utilizes standard HTML `<table>` elements with inline background color opacity calculations. Features rotated table headers and custom hover crosshairs.
- **NullityMatrix:** Uses native `<svg>`, `<rect>`, `<polygon>`, and `<polyline>` elements for extreme rendering performance of dense datasets (e.g., 250 rows × 15 columns).

## 5. Expected JSON Schema

To render without errors, the `REPORT_DATA` object must adhere to the following core structure:

```json
{
  "analysis": { "title": "string", "date_start": "iso-date", "date_end": "iso-date" },
  "table": { "n": "number", "n_var": "number", "memory_size": "number", "p_cells_missing": "number" },
  "alerts": [
    { "alert_type": "UNIQUE | MISSING | CONSTANT", "fields": ["string"], "message": "string (optional)" }
  ],
  "variables": {
    "column_name": {
      "type": "Numeric | Categorical | Boolean",
      "p_missing": "number",
      "histogram": { "bins": [], "counts": [] },
      "...stats": "number | boolean"
    }
  },
  "missing": {
    "bar": { "matrix": { "columns": [], "counts": [] } },
    "matrix": { "columns": [], "values": [[boolean]] },
    "heatmap": { "matrix": [ { "col1": "number" } ] }
  },
  "correlations": {
    "pearson": [ { "col1": "number", "col2": "number" } ]
  },
  "sample": {
    "head": {
      "column_name": ["val1", "val2"]
    }
  }
}
```

> **Note:** Matrices inside `missing` and `correlations` are processed through a `parseMatrixData` helper, allowing them to be either arrays of objects or standard 2D arrays (`[[]]`).
