# Plan: Fix `n_var` Metadata Inflation

## Problem Definition
The `n_var` (number of variables) metric in `ProfileReport._build` is currently computed as `len(self.schema)`. Since `self.schema` includes a synthetic `_dataset` entry (used for global metadata), this counts as an extra variable, inflating the count by one. This inflation also skews derived metrics like `p_cells_missing`.

## Proposed Solution
Update `ProfileReport._build` to compute `n_var` using the number of real variables (either `len(schema_copy)` after popping `_dataset` or `len(self.variables)`).

## Key Files & Context
- `src/ibis_profiling/report/report.py`: Location of `ProfileReport._build`.
- `tests/test_n_var_metadata.py`: New test file to verify the fix.

## Implementation Plan

### Phase 1: Infrastructure & Reproduction
- [ ] Create a reproduction test in `tests/test_n_var_metadata.py` that asserts `n_var` matches the number of actual columns even when `_dataset` metadata is present.
- [ ] Verify the test fails.

### Phase 2: Core Logic
- [ ] Modify `src/ibis_profiling/report/report.py` to use `len(self.variables)` for `n_var`.
- [ ] Ensure `p_cells_missing` uses this corrected `n_var`.

### Phase 3: Verification
- [ ] Run the reproduction test and ensure it passes.
- [ ] Run the full test suite to ensure no regressions.

## Git Strategy
- Branch: `fix/n_var_metadata_inflation`
- Commit frequency: After each phase.

## Task Decomposition

### Phase 1: Infrastructure & Reproduction
- **Task 1.1**: Create `tests/test_n_var_metadata.py` with a test case that checks `n_var` against a known number of columns.
    - **Scope**: Test creation.
    - **Validation**: `./run.sh uv run pytest tests/test_n_var_metadata.py` (should fail).
- **Task 1.2**: Commit the failing test.
    - **Scope**: Git commit.

### Phase 2: Core Logic
- **Task 2.1**: Update `src/ibis_profiling/report/report.py` to use `len(self.variables)` for `n_var`.
    - **Scope**: Code modification.
    - **Validation**: `./run.sh uv run pytest tests/test_n_var_metadata.py` (should pass).
- **Task 2.2**: Commit the fix.
    - **Scope**: Git commit.

### Phase 3: Verification & Docs
- **Task 3.1**: Run full test suite.
    - **Scope**: Verification.
    - **Validation**: All tests pass via `./run.sh uv run pytest`.
- **Task 3.2**: Record session log.
    - **Scope**: Documentation.
