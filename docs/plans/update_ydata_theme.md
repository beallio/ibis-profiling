# Plan: Update YData-like Theme and Test Visuals

This plan outlines the steps to restructure the YData-like theme into a single-page layout and improve its visual details, followed by generating a full report for verification.

## 1. Explore & Analyze

-   **Current State:**
    -   `src/ibis_profiling/templates/ydata-like.html` uses tab-based navigation.
    -   `VariableCard` is collapsed by default.
    -   Non-numeric variables have a "More details" button.
    -   "NaN" is used in several places instead of "Null".
-   **Objective:**
    -   Convert to single-page with sticky header links.
    -   Expand details by default.
    -   Compress non-numeric variable details into the card (remove button).
    -   Replace "NaN" with "Null".
    -   Improve histogram labels.
    -   Generate a comprehensive test report.

## 2. Proposed Changes

### 2.1. Template Structure (`ydata-like.html`)
-   **App Component:**
    -   Remove `activeTab` state.
    -   Render `OverviewSection`, `VariablesSection` (wrapping `VariableCard` loop), `MissingValuesSection`, and `SampleSection` vertically.
    -   Add IDs to section containers (`#overview`, `#variables`, `#missing`, `#sample`).
    -   Update header navigation to use anchor links (`<a href="#overview">...</a>`).
-   **VariableCard Component:**
    -   Change `const [expanded, setExpanded] = useState(true);` (default to true).
    -   For `Numeric` type: Keep toggle logic.
    -   For `Categorical` and `Boolean`: Remove toggle button and always show details inline.
-   **Visuals:**
    -   Update `HistogramChart` to have more padding/spacing for labels.
    -   Replace "NaN" strings with "Null" in `SampleSection` and `VariableCard`.
    -   Improve `VariableDetails` for categorical variables to show a summary if possible.

### 2.2. Test Script
-   Create `scripts/generate_full_ydata_report.py` to generate a report with varied data types and alerts.

## 3. Implementation Plan

### Phase 1: Template Refactoring
1.  Modify `src/ibis_profiling/templates/ydata-like.html`:
    -   Restructure `App` for single-page layout.
    -   Update `VariableCard` and `VariableDetails`.
    -   Apply visual fixes (NaN -> Null, Histogram spacing).

### Phase 2: Verification
1.  Create and run `scripts/generate_full_ydata_report.py`.
2.  Manually inspect the generated HTML.

## 4. Verification & Testing

### Test Cases
-   **Layout:** Verify all sections are visible on a single page.
-   **Navigation:** Verify clicking header links jumps to the correct section.
-   **Expansion:** Verify variable details are expanded by default.
-   **Categorical Display:** Verify categorical variables don't have a toggle button.
-   **Text Labels:** Verify "NaN" is replaced by "Null".
