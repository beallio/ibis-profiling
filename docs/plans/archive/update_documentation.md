# Plan: Update Documentation and Add Screenshots (Using Chromium CLI)

## Objective
1.  Remove the "Contributing" section from the `README.md`.
2.  Update the `README.md` to include recently added features:
    -   Excel file profiling support (`ProfileReport.from_excel`).
    -   Custom report titles.
3.  Use `chromium-browser` CLI to take screenshots of the report and embed them in the `README.md`.

## Key Files
- `README.md`: The main documentation file.
- `src/ibis_profiling/assets/img/`: Directory for storing screenshots.

## Implementation Steps

### 1. Update README Content
- Remove the "Contributing" section.
- Add "Excel Support" to the Features list.
- Add an "Excel Ingestion" example to the Usage section.
- Document the `title` parameter in `ProfileReport`.

### 2. Generate Screenshots
- Use `chromium-browser --headless --screenshot` to capture:
    - Overview (default scroll).
    - Variables (simulated scroll if possible, or just a large window size).
    - Save to `src/ibis_profiling/assets/img/`.

### 3. Embed Screenshots in README
- Insert the generated images into the `README.md` under a new "Preview" section.

## Verification & Testing
1.  Verify the updated `README.md` renders correctly.
2.  Ensure screenshots exist and look professional.
