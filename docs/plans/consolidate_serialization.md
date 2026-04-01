# Plan: Consolidate JSON Serialization and Type Conversion

## Problem Definition
`ReportEncoder` and `ProfileReport._to_json_serializable` in `src/ibis_profiling/report/report.py` contain redundant logic for converting Ibis scalars, Polars types, and Python temporal objects into JSON-compatible formats. This duplication leads to maintenance overhead and potential inconsistencies.

## Architecture Overview
1.  **Unified Utility**: Extract common conversion logic into a top-level function `serialize_report_value(val: Any) -> Any`.
2.  **ReportEncoder Integration**: Update `ReportEncoder.default` to delegate to `serialize_report_value`.
3.  **ProfileReport Integration**: Update `ProfileReport._to_json_serializable` to delegate to `serialize_report_value`.
4.  **Consistency**: Ensure `NaN`, `Inf`, `Decimal`, and `Ibis.Scalar` are handled identically in both paths.

## Core Data Structures
No changes to data structures.

## Public Interfaces
No changes to public interfaces.

## Phased Approach

### Phase 1: Infrastructure & Utility
- [ ] Implement `serialize_report_value(val: Any) -> Any` in `src/ibis_profiling/report/report.py`.
- [ ] Initialize `fix/consolidate-serialization` branch.

### Phase 2: Refactor ReportEncoder
- [ ] Update `ReportEncoder.default` to use `serialize_report_value`.
- [ ] Ensure it falls back to `super().default()` for unknown types.

### Phase 3: Refactor ProfileReport
- [ ] Update `ProfileReport._to_json_serializable` to use `serialize_report_value`.
- [ ] Ensure it handles fallback markers (`__unsupported_type__`) consistently.

### Phase 4: Verification
- [ ] Create `tests/test_serialization.py` to verify consistent behavior for all edge cases (NaN, Inf, Decimal, Ibis Scalar).
- [ ] Verify `to_json()` output matches `to_html()` embedded data.
- [ ] Run full test suite.

## Git Strategy
- Branch: `fix/consolidate-serialization`
- Commits:
    - `feat: add serialize_report_value utility`
    - `refactor: use serialize_report_value in ReportEncoder`
    - `refactor: use serialize_report_value in ProfileReport`
