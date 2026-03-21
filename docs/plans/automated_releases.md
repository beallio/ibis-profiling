# Plan: Automated GitHub Releases

Automate the process of creating GitHub releases, generating release notes, and publishing to PyPI when a version tag is pushed.

## Problem Definition
Currently, publishing to PyPI requires a manual GitHub Release creation. We want to automate this so that pushing a tag (e.g., `v0.1.3`) automatically:
1. Creates a GitHub Release.
2. Generates release notes based on commit history.
3. Triggers the PyPI publishing workflow.

## Architecture Overview
We will transition from a manual "release published" trigger to a "tag pushed" trigger.
- A new `release.yml` workflow will handle the release creation.
- The `publish.yml` workflow will be updated to trigger upon the completion of the release or directly on tag push.

## Implementation Plan

### 1. Update `.github/workflows/publish.yml`
Modify the trigger to run on tag pushes instead of only on release publication, or keep it as is if `release.yml` triggers it.

### 2. Create `.github/workflows/release.yml`
Create a workflow that:
- Triggers on `v*` tags.
- Uses `softprops/action-gh-release` to create the release.
- Uses GitHub's `generate_release_notes: true` feature.

### 3. Coordinate Versioning
The project already uses `hatch-vcs`, so the version in the built package will automatically match the git tag.

## Verification & Testing
1. Push a test tag (e.g., `v0.1.3-rc1`) and verify:
   - `release.yml` runs and creates a draft or pre-release.
   - Release notes are generated correctly.
   - `publish.yml` is triggered.
2. Ensure permissions are correctly set for `GITHUB_TOKEN`.

## Future Considerations
- Automatic CHANGELOG.md updates.
- Conventional Commits enforcement to improve release note quality.
