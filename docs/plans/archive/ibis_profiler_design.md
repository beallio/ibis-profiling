# Plan: Ibis-Native Data Profiling System

## Problem Definition
Traditional profiling systems (like `ydata-profiling`) iterate over datasets column-by-column, often loading data into memory (Pandas). This fails on large datasets. This project aims to build a **profiling query compiler** built natively on **Ibis**. The system will treat data profiling as a query planning problem, translating dozens of statistical metrics into a minimal set of optimal, batched queries that execute directly in the remote backend.

## Architecture Overview
The system is divided into five core components:
1. **Dataset Inspector:** Analyzes the `ibis.Table` schema to extract column types and basic dataset-level metadata without executing queries.
2. **Metric Registry:** A central catalog of `Metric` definitions detailing applicability (e.g., numeric only) and query compilation rules (e.g., an Ibis aggregation expression).
3. **Query Planner:** The core compiler. It matches columns against the Metric Registry, filters invalid combinations, and groups compatible expressions into a few efficient query plans.
4. **Execution Engine:** Dispatches the compiled Ibis expression graphs to the backend and handles caching/sampling.
5. **Report Builder:** Transforms raw backend results into a structured JSON/Dict report.

## Core Data Structures
- `Metric`: Statistical metric definition (name, category, `applies_to`, `build_expr`).
- `ProfilingPlan`: Batched execution plans (e.g., `global_aggregations`, `distributions`).
- `ProfileReport`: Final structured output containing dataset and column stats.

## Public Interfaces
- `profile(table: ibis.Table) -> dict`: The main entrypoint.
- `MetricRegistry.register(metric: Metric)`: Extensibility API for custom metrics.

## Dependency Requirements
- `ibis-framework`: Core expression engine.
- `pydantic` or `dataclasses`: For structures.
- `pytest`, `pytest-cov`: For testing.
- `ruff`, `mypy`: For code quality.

## Testing Strategy
Following strict Bottom-Up TDD:
1. **Unit Tests (Planner/Compiler):** Assert the Planner successfully batches multiple metrics into minimal `.aggregate()` calls.
2. **Integration Tests (Execution):** Use the DuckDB backend with a known dataset to verify exact statistic computations.
3. **Performance Tests:** Ensure query counts stay under limits (e.g., < 5 queries).
