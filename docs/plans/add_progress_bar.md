# Plan: Add CLI Progress Bar and Performance Tracking

## Problem Definition
When running the `ProfileReport` CLI on large datasets, there is no visual feedback on the progress of the profiling stages. Additionally, there is no built-in way to track how much time each stage (Global Aggregates, Correlations, etc.) takes, making it difficult to debug performance bottlenecks.

## Architecture Overview
1.  **Performance Tracking**: The `Profiler.run()` method will be updated to record the duration of each internal phase. These timings will be stored in the `InternalProfileReport` metadata.
2.  **Progress Bar**: The CLI (`ibis_profiling.cli:main`) will use `click.progressbar` to provide a visual indicator. It will pass a callback to the `Profiler` to update the bar as phases complete.
3.  **Debug Output**: A new `--debug` flag in the CLI will print a summary table of the time spent in each profiling phase.

## Core Data Structures
- `report.analysis["performance"]`: A dictionary mapping phase names to durations (in milliseconds).

## Public Interfaces
- CLI: Added `--debug` flag.
- `Profiler`: Refined usage of `on_progress` callback.

## Phased Approach

### Phase 1: Core Logic (Performance Tracking)
- [ ] Update `Profiler.run` to track start/end times for each major block.
- [ ] Store results in `report.analysis["performance"]`.
- [ ] Ensure `_update_progress` is called with accurate incremental values that sum to 100.

### Phase 2: CLI Integration (Progress Bar & Debug)
- [ ] Add `--debug` option to `main` in `src/ibis_profiling/cli.py`.
- [ ] Implement a progress handler in `cli.py` using `click.progressbar`.
- [ ] Pass the progress handler to `ProfileReport` / `profile()`.
- [ ] Print performance summary at the end if `--debug` is enabled.

### Phase 3: Verification
- [ ] Create `tests/test_progress.py` to verify `on_progress` callback behavior.
- [ ] Verify `performance` metadata is present in `to_dict()`.
- [ ] Manual verification of CLI output.

## Git Strategy
- Branch: `feat/cli-progress-and-debug`
- Incremental commits for each phase.
