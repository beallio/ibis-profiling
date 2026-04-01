# Plan: Escape Inline JS Assets to Avoid Script Breakouts

## Problem Definition
When inlining JS assets into HTML reports, raw content is inserted into `<script>` tags. If an asset contains the string `</script>`, it will prematurely terminate the tag, potentially leading to broken HTML or XSS vulnerabilities.

## Architecture Overview
The solution involves adding an escaping step during the asset inlining process in `ProfileReport.to_html`.

- **Profiler**: Update the `to_html` loop that inlines vendor assets.
- **Escaping**: Replace `</script` with `<\/script` in the asset content. This is safe for JavaScript execution but prevents the HTML parser from seeing it as a closing tag.

## Core Data Structures
- No changes to data structures.

## Public Interfaces
- No changes to public interfaces.

## Dependency Requirements
- No new dependencies.

## Testing Strategy
- **Functional**: `tests/test_script_escape.py` will:
    - Mock a vendor asset containing `</script>`.
    - Generate an offline report.
    - Verify that the resulting HTML does not have an unescaped `</script>` inside the content.
    - Verify that the JS content remains valid (using `<\/script`).

## Phased Approach

### Phase 1: Infrastructure & API
- [ ] Create feature branch `fix/escape-inline-js`.
- [ ] Create reproduction test `tests/test_script_escape.py`.

### Phase 2: Core Logic (Escaping)
- [ ] Implement escaping in `ProfileReport.to_html` in `src/ibis_profiling/report/report.py`.
- [ ] Verify `tests/test_script_escape.py` passes.

### Phase 3: Verification & Cleanup
- [ ] Run full test suite.
- [ ] Execute PE review.
- [ ] Submit PR.

## Git Strategy
- Branch: `fix/escape-inline-js`
- Commit after each functional step.
