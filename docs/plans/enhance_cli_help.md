# Plan: Enhance CLI Help and Versioning

Improve the CLI's `--help` output to be more descriptive, include the package version, and add a dedicated `--version` flag.

## Problem Definition
The current CLI help output is basic and does not display the package version. Users have no direct way to check the installed version via the CLI (e.g., `ProfileReport --version`).

## Architecture Overview
1.  **Version Integration:** Use `ibis_profiling.__version__` to retrieve the current package version.
2.  **Click Version Flag:** Utilize `@click.version_option` to add a standard `--version` flag.
3.  **Enhanced Help:** Reorganize and improve the command docstring for better readability and detail.

## Key Files
- `src/ibis_profiling/cli.py`: Main CLI implementation using `click`.

## Proposed Solution
Update `src/ibis_profiling/cli.py` to:
- Import `__version__` from `ibis_profiling`.
- Use `@click.version_option` with the retrieved version.
- Update the `main` docstring to provide more comprehensive help.
- Optionally group options or add more context to help messages.

## Phased Approach

### Phase 1: Logic Implementation
- [ ] Modify `src/ibis_profiling/cli.py`:
    - Add `from ibis_profiling import __version__`.
    - Add `@click.version_option(version=__version__)`.
    - Enhance the `main` docstring with more details about supported formats and features.

### Phase 2: Verification
- [ ] Run `ProfileReport --version` and verify output.
- [ ] Run `ProfileReport --help` and verify the new descriptive text and version inclusion (Click's `version_option` adds version to help by default in some configurations, but we should verify).

## Git Strategy
- **Branch:** `feat/enhance-cli-help`
- **Commits:**
    - Add `--version` flag and enhance help text.

## Testing Strategy
- **Version Check:** `ProfileReport --version` should return the correct version string.
- **Help Check:** `ProfileReport --help` should show the updated description and options.
- **Regression:** Ensure CLI still functions correctly for all file types.
