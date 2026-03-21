## 🔴 1. Security Vulnerabilities

**Critical: Cross-Site Scripting (XSS) via Unescaped JSON Injection**
*   **Location:** `src/ibis_profiling/report/report.py` (`to_html`)
*   **Issue:** The report data is serialized to JSON and blindly injected into the HTML template using string replacement (`html.replace("{{REPORT_DATA}}", report_json)`). Python's standard `json.dumps` does not escape HTML control characters like `<` or `>`. If a malicious or malformed dataset contains strings like `</script><script>alert(1)</script>` (e.g., within column names, categorical values, or string lengths), it will break out of the JavaScript context in the generated HTML report and execute arbitrary code.
*   **Recommendation:** Never inject raw JSON directly into HTML. Serialize using `json.dumps(..., separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")` to ensure the payload is safe for inclusion inside a `<script>` tag, or utilize a proper templating engine (like Jinja2) with strict contextual autoescaping.

---

## 🟠 2. Performance Bottlenecks

**High: N+1 Query Execution for Complex Metrics**
*   **Location:** `src/ibis_profiling/planner.py` (`build_complex_metrics`)
*   **Issue:** The query planner treats complex metrics (`top_values`, `extreme_values_smallest`, `extreme_values_largest`, `length_histogram`) as isolated expressions, creating separate plans *per column*. For a dataset with 100 columns, this generates hundreds of individual Ibis queries. In a lazy-evaluation engine, this results in the N+1 query problem, forcing the backend to perform multiple full table scans or maintain excessive parallel execution graphs, crippling performance on large datasets.
*   **Recommendation:** Consolidate these operations. Utilize Ibis window functions, array aggregations, or unified `GROUP BY` passes to calculate multi-column distributions in a single scan where backend support allows.

**High: Exact Value Counts for Singletons (`n_unique`)**
*   **Location:** `src/ibis_profiling/metrics.py`
*   **Issue:** The `n_unique` metric (counting values that appear exactly once) forces an exact `value_counts()` on the entire column. For high-cardinality data (e.g., UUIDs or primary keys in a 100M+ row dataset), this requires a massive hash table that will lead to severe Out-Of-Memory (OOM) errors and execution bottlenecks.
*   **Recommendation:** Exclude `n_unique` from default passes on large datasets, or replace it with an approximate sketch algorithm (e.g., HyperLogLog variants) if supported by the underlying engine.

---

## 🟡 3. Edge-Case Bugs

**Medium: Silent Precision Loss for 64-bit Integers and Decimals**
*   **Location:** `src/ibis_profiling/metrics.py` (`safe_col`)
*   **Issue:** To "ensure consistent behavior," `safe_col` aggressively casts *all* `dt.Numeric` types to `dt.Float64`. This silently truncates precision for `dt.Int64` (values > 2^53) and high-precision `dt.Decimal` types. Financial datasets or wide IDs will silently compute incorrect `min`, `max`, and `sum` statistics.
*   **Recommendation:** Apply type casting conditionally. Preserve exact types for strictly arithmetic aggregations (`min`, `max`, `sum`) and only cast to `Float64` for inherently floating-point statistical aggregations (`std`, `mean`, `variance`).

**Medium: Flawed Regex Minification Breaking UI Logic**
*   **Location:** `src/ibis_profiling/report/report.py` (`to_html`)
*   **Issue:** The naive regex used for minifying HTML (`re.sub(r"^//.*$", "", html, flags=re.MULTILINE)`) only matches single-line comments at the absolute start of a line. Indented JavaScript comments (`    // comment`) are completely ignored. Furthermore, the block comment remover (`re.sub(r"/\*.*?\*/", ...)`) is context-blind and will corrupt valid string literals (e.g., `let url = "http://example.com/*path*/";`).
*   **Recommendation:** Remove regex-based minification. Use dedicated AST-aware minification libraries (`htmlmin`, `rcssmin`, `rjsmin`), or rely on pre-minified template assets.

**Low: Exception Masking in CLI Fallback Logic**
*   **Location:** `src/ibis_profiling/cli.py` (`main`)
*   **Issue:** If a file extension is unrecognized, the CLI attempts `ibis.read_parquet`, blindly catches all `Exception`s, and falls back to `read_csv`. If the file is genuinely a Parquet file but fails due to a permission error or schema corruption, the CLI swallows the actual error, attempts to parse it as CSV, and outputs a highly confusing CSV parsing error to the user.
*   **Recommendation:** Catch specific backend exceptions or inspect file magic bytes instead of utilizing blind `try...except` control flow.

---

## 🔵 4. Architectural Anti-Patterns

**Medium: God Class Violation (`ProfileReport`)**
*   **Location:** `src/ibis_profiling/report/report.py`
*   **Issue:** `ProfileReport` is a monolith. It manages internal data modeling, computes complex derived metrics inline within `_build`, orchestrates recursive JSON sanitization, handles HTML templating, manages file I/O, and even acts as a factory for Excel ingestion. This violates the Single Responsibility Principle (SRP) and makes the class rigid and untestable.
*   **Recommendation:** Decompose the monolith into domain-specific components: `ReportDataModel`, `MetricsCalculator`, and `ReportRenderer`.

**Medium: Leaky Abstractions and Backend Coupling**
*   **Location:** `src/ibis_profiling/engine.py` (`get_storage_size`)
*   **Issue:** Ibis is designed to be a backend-agnostic abstraction layer. However, `ExecutionEngine` hardcodes a check for `con.name == "duckdb"` and executes raw, dialect-specific SQL (`CALL pragma_storage_info()`). This violates the Open-Closed Principle; supporting DataFusion or Polars storage estimation will require modifying this core file again.
*   **Recommendation:** Implement a `BackendStrategy` interface. Abstract backend-specific optimizations into a registry of adapters rather than relying on `if/else` type checking on the connection object.

**Medium: Dict-Driven Development (Primitive Obsession)**
*   **Location:** `src/ibis_profiling/report/report.py`
*   **Issue:** The internal state of the report is managed via deeply nested, untyped dictionaries (`self.variables`, `self.table`). This "stringly-typed" architecture forces the pervasive use of `.get(...)` and manual type checks (e.g., `isinstance(current_wm, int)`), making the codebase highly susceptible to `KeyError`s and hostile to refactoring.
*   **Recommendation:** Migrate to strongly-typed data structures using `dataclasses` or `pydantic`. This will enforce schema contracts at runtime and provide static type safety guarantees.
