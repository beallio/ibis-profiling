# Plan: Improve Test Coverage (Target 90%+)

## Objective
Close existing test coverage gaps in `engine.py`, `formatters.py`, `report.py`, and the `presentation/structure` layers to ensure the core logic is fully validated.

## Key Files & Gaps
- `src/ibis_profiling/report/formatters.py`: Missing tests for `fmt_bytes`, `fmt_numeric` (edge cases), and `fmt_color`.
- `src/ibis_profiling/engine.py`: Missing tests for `get_storage_size` (DuckDB pragma checks).
- `src/ibis_profiling/report/presentation/core/variable.py`: Missing tests for `Variable.render`.
- `src/ibis_profiling/report/structure/report.py`: `get_structure` and related helper methods are partially untested.
- `src/ibis_profiling/report/report.py`: `ReportEncoder` and `to_json` error handling.

## Implementation Steps

### 1. New Test Suite for Formatters & Engine
- Create `tests/test_coverage_gap_closure.py`:
    - Add test cases for `fmt_bytes` (0B, KiB, MiB, GiB, TiB).
    - Add test cases for `fmt_numeric` (None, Scientific notation, standard).
    - Add test cases for `fmt_color` (various thresholds).
    - Add test cases for `ExecutionEngine.get_storage_size` using a mocked DuckDB backend and `UnboundTable`.

### 2. Enhance Presentation Layer Tests
- Update `tests/test_variable.py` or add to gap closure:
    - Test `Variable.render()` directly.
    - Test `Container.render()` for different sequence types.

### 3. Enhance Structure Layer Tests
- Update `tests/test_report.py`:
    - Ensure `get_structure()` is called and its output inspected in a full integration test.
    - Specifically trigger `_get_sample_section` by providing sample data in the model.
    - Specifically trigger `_get_variables_section` for both Numeric and Categorical types.

### 4. Serialization Gaps
- Add test cases for `ReportEncoder`:
    - Test serialization of `datetime`, `date`, and `Ibis Scalar`.
    - Test handling of `NaN` and `Inf` in the encoder.

## Verification & Testing
1. Run `pytest --cov=src --cov-report=term-missing`.
2. Target: Increase total coverage from 84% to >90%.
