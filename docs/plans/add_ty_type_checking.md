# Plan: Integrate `ty` Type Checking

## Problem Definition
The project currently uses `ruff` for linting and formatting but lacks a high-performance type checking step in the mandatory pre-commit lifecycle. `ty` (by Astral) provides a fast, Rust-based alternative to `mypy` and `pyright` that fits well with the existing `uv` and `ruff` ecosystem.

## Goals
- Add `ty` to development dependencies.
- Fix existing type diagnostics to achieve a "green" baseline.
- Integrate `ty check` into the mandatory project protocol (`GEMINI.md`).

## Implementation Strategy
1. **Dependency Management**:
   - Run `uv add --dev ty` to update `pyproject.toml` and `uv.lock`.
2. **Type Error Resolution**:
   - Address `possibly-missing-attribute` warnings by using explicit subpackage imports (e.g., `import ibis.expr.datatypes as dt`).
   - Fix `invalid-assignment` and `unsupported-operator` errors by adding proper type annotations to models (especially `SummaryTable` and `VariableMetadata`).
   - Correct `invalid-method-override` in `ReportEncoder`.
3. **Protocol Update**:
   - Update `GEMINI.md` to include `uv run ty check src/` in the quality control section.

## Verification Plan
- Run `uv run ty check src/` and ensure zero diagnostics.
- Run `uv run ruff check .` and `uv run pytest` to ensure no regressions.
