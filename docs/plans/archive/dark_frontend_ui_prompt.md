# Prompt: High-Fidelity Dark Mode Profiling Dashboard

Use this prompt with an LLM (Gemini, Claude, GPT-4) to generate a modern, dark-themed frontend for the data profiling reports.

---

**Role:** Senior Frontend & Data Visualization Engineer.
**Task:** Create a high-fidelity, dark-themed Single Page Application (SPA) for a Data Profiling Report using the provided JSON data.

**Design Requirements:**
1. **Theme:** Modern "Midnight" dark theme using a Slate/Zinc palette (e.g., Background: `#0f172a`, Cards: `#1e293b`). Use Tailwind CSS for styling.
2. **Layout:** Sidebar navigation with sections: Overview, Variables, Correlations, Missing Values, and Samples.
3. **Overview Section:** 
   - Dashboard-style KPIs for Global Table Stats: Row count (`n`), Variable count (`n_var`), Memory Size, and Duplicate % (`p_duplicates`).
   - A prioritized "Alerts" feed showing data quality warnings (e.g., HIGH_CARDINALITY, CONSTANT, MISSING).
4. **Variables Section:** 
   - A searchable list of column cards.
   - Each card displays primary stats (Mean, Distinct %, Missing %).
   - A "Toggle Details" button that expands a deep-dive view containing:
     - **Full Statistics:** A 2-column grid of all available metrics (Quantiles, Skewness, Kurtosis, Monotonicity, etc.).
     - **Distribution:** A responsive Chart.js bar chart for value frequencies (histogram).
     - **Text Analysis:** If available, show Mean/Min/Max length and the Length Histogram.
     - **Extreme Values:** Tables for the "5 Smallest" and "5 Largest" values.
5. **Correlations:** 
   - A high-fidelity interactive Heatmap or Grid Table for Pearson and Spearman matrices.
6. **Missing Values:**
   - A visualization section mirroring the "Matrix" and "Bar" charts from the JSON.
7. **Samples:**
   - A clean, paginated data table for the "Head" and "Tail" samples.

**Technical Implementation:**
- **Stack:** Pure HTML5, Tailwind CSS, Lucide Icons, and Chart.js (all via CDN).
- **Architecture:** The JSON data should be assigned to a constant `const reportData = {...}` at the top of the script.
- **Responsiveness:** Ensure charts and tables scale for all screen sizes.
- **Data Handling:** Implement logic to handle missing or `null` values gracefully (don't break if a metric like 'skewness' is missing).

**Input Data Schema Reference:**
The UI must support the standard YData/Ibis JSON format, specifically capturing:
- `table`: {memory_size, record_size, n, n_var, types, ...}
- `variables`: { [col_name]: { type, mean, std, 5%, 25%, 50%, 75%, 95%, histogram, length_histogram, extreme_values_smallest, extreme_values_largest, monotonic_increasing, ... } }
- `correlations`: { pearson: { columns, matrix }, spearman: { columns, matrix } }
- `alerts`: [ { column_name, alert_type, values, ... } ]
