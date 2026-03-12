# Plan: Restore and Improve Screenshot Automation

## Objective
Restore `scripts/take_screenshots.py` as a maintainable tool for future documentation updates. Improve the SPA template to allow deep-linking to tabs via URL hashes, enabling the screenshot script to work without manual code modifications.

## Key Files
- `src/ibis_profiling/templates/spa.html`: Update React state initialization.
- `scripts/take_screenshots.py`: Re-implement using `chromium-browser` CLI and URL hashes.

## Implementation Steps

### 1. Update SPA Template
- Modify `src/ibis_profiling/templates/spa.html`:
    - Initialize `activeTab` using `window.location.hash.slice(1)` with a fallback to `'overview'`.
    - Add a `useEffect` to listen for `hashchange` events to allow dynamic switching if needed.

### 2. Implement Reusable Screenshot Script
- Create `scripts/take_screenshots.py`:
    - Use `subprocess` to call `chromium-browser --headless --screenshot`.
    - Target specific tabs by appending hashes (e.g., `file://path/report.html#missing`).
    - Capture Overview, Variables, and Missing tabs.
    - Save to `src/ibis_profiling/assets/img/`.

### 3. Verification
- Generate a sample report.
- Run `python scripts/take_screenshots.py`.
- Verify the 3 screenshot files are created and show the correct tabs.
