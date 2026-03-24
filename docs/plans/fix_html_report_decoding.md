# Plan: Fix HTML Report Decoding

## Objective
Address the code review finding regarding deprecated `escape(atob(...))` usage in HTML reports. 
Replace it with a modern decoding method using `TextDecoder` and `Uint8Array` to handle Base64-encoded UTF-8 data correctly and efficiently.

## Background & Motivation
The current implementation uses `decodeURIComponent(escape(atob(data)))` to decode UTF-8 from Base64.
- `atob` only handles Latin-1 (binary) strings.
- `escape` is deprecated.
- This combination can fail on certain UTF-8 sequences and is inefficient for large payloads.
- Modern browsers support `TextDecoder`, which is the standard way to handle character encodings.

## Scope & Impact
- **Templates affected:** `src/ibis_profiling/templates/default.html`, `src/ibis_profiling/templates/ydata-like.html`.
- **Logic affected:** JS initialization code that parses `REPORT_DATA`.
- **Infrastructure:** No changes to Python side (it still sends Base64).
- **Security:** Maintains the XSS protection provided by Base64 encoding.

## Proposed Solution
Update the JavaScript in both templates to use:
```javascript
const bytes = Uint8Array.from(atob(ENCODED_REPORT_DATA), c => c.charCodeAt(0));
const REPORT_DATA = JSON.parse(new TextDecoder().decode(bytes));
```
This is more efficient and handles UTF-8 robustly.

## Git Strategy
- **Branch:** `fix/html-decoding`
- **Commits:**
  1. Refactor `default.html` decoding logic.
  2. Refactor `ydata-like.html` decoding logic.
  3. Add UTF-8 and large data regression tests.

## Implementation Plan

### Phase 1: Research & Setup
- [x] **Task 1.1: Create branch**
    - Scope: Create a new branch `fix/html-decoding`.
    - Validation: `./run.sh git branch` shows the new branch.
- [x] **Task 1.2: Audit templates**
    - Scope: Identify all occurrences of `atob` and `escape` in the codebase.
    - Validation: `grep` output identifies `default.html` and `ydata-like.html`.

### Phase 2: UI (Templates)
- [x] **Task 2.1: Update `default.html` decoding**
    - Scope: Replace line 132 in `src/ibis_profiling/templates/default.html` with `TextDecoder` logic.
    - Validation: Manual check of a generated default report.
- [x] **Task 2.2: Update `ydata-like.html` decoding**
    - Scope: Replace line 106 in `src/ibis_profiling/templates/ydata-like.html` with `TextDecoder` logic.
    - Validation: Manual check of a generated ydata-like report.

### Phase 3: Logic (Verification & Testing)
- [x] **Task 3.1: Create UTF-8 Stress Test**
    - Scope: Create `tests/test_utf8_reports.py` with Emojis, CJK characters, and malformed-ish sequences.
    - Validation: `./run.sh uv run pytest tests/test_utf8_reports.py` passes.
- [x] **Task 3.2: Create Large Data Test**
    - Scope: Create a test that generates a 5MB+ JSON payload (e.g. many columns/unique values) and ensure HTML report still renders.
    - Validation: Playwright (if available) or checking for `REPORT_DATA` integrity in the HTML.
- [x] **Task 3.3: Run Regression Suite**
    - Scope: Run all existing tests to ensure no regressions.
    - Validation: `./run.sh uv run pytest tests/` passes.

### Phase 4: Finalization
- [x] **Task 4.1: Record session summary**
    - Scope: Document the changes and findings in `docs/agent_conversations/`.
    - Validation: JSON log exists.

## Completion Criteria
- [x] Both templates updated with modern decoding logic.
- [x] UTF-8 characters are correctly rendered.
- [x] Large reports are handled without errors.
- [x] Full test suite passes.

## Verification
- `./run.sh uv run pytest tests/test_utf8_reports.py`
- Manual inspection of a generated report with complex characters.
