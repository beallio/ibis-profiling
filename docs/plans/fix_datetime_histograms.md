# Plan: Robust DateTime Histogram Logic

Address the issue where DateTime histograms are disabled if `min`/`max` values are already `datetime` objects instead of strings.

## Problem Definition
The current implementation of `Profiler._run_advanced_pass` assumes that `min` and `max` values for DateTime columns are always strings and uses `dateutil.parser.isoparse` to convert them to `datetime` objects. If these values are already `datetime` objects (which many backends return), `isoparse` fails, and the histogram calculation is silently skipped.

## Architecture Overview
The fix will involve:
1. Detecting the type of `min`/`max` values.
2. Converting `datetime.datetime`, `datetime.date`, `numpy.datetime64`, and `pandas.Timestamp` directly to epoch seconds.
3. Using `isoparse` only as a fallback for strings.
4. Adding warnings for conversion failures.

## Key Files & Context
- `src/ibis_profiling/__init__.py`: Contains `Profiler._run_advanced_pass` where the histogram logic resides.

## Proposed Solution
Update `_run_advanced_pass` in `src/ibis_profiling/__init__.py` to include a more robust conversion logic for DateTime values.

```python
            if v_type == "DateTime":
                col = col.epoch_seconds().cast("float64")
                v_min_raw = stats.get("min")
                v_max_raw = stats.get("max")

                def to_timestamp(val):
                    if val is None:
                        return None
                    # 1. Handle string/bytes (fallback to isoparse)
                    if isinstance(val, (str, bytes)):
                        import dateutil.parser
                        try:
                            return dateutil.parser.isoparse(val).timestamp()
                        except Exception:
                            return None
                    # 2. Handle datetime objects
                    from datetime import datetime, date
                    if isinstance(val, datetime):
                        return val.timestamp()
                    if isinstance(val, date):
                        return datetime.combine(val, datetime.min.time()).timestamp()
                    # 3. Handle pandas/numpy if available
                    if hasattr(val, "timestamp") and callable(val.timestamp):
                        return val.timestamp()
                    # Final fallback: try to use it as-is if it's already numeric? 
                    # Unlikely for DateTime, but safer to return None if we can't convert.
                    return None

                v_min = to_timestamp(v_min_raw)
                v_max = to_timestamp(v_max_raw)
                
                if v_min_raw and v_max_raw and (v_min is None or v_max is None):
                    report.analysis.setdefault("warnings", []).append(
                        f"Histogram failed for {col_name}: Could not convert min/max ({v_min_raw}/{v_max_raw}) to timestamp."
                    )
```

## Git Strategy
- **Branch:** `fix/datetime-histograms`
- **Commits:**
  - Create reproduction test.
  - Implement robust DateTime conversion.
  - Verify fix.

## Phased Approach

### Phase 1: Infrastructure & Verification
- [ ] Create `tests/test_datetime_histograms.py` that reproduces the failure by mocking `stats["min"]` and `stats["max"]` as `datetime` objects.
- [ ] Verify that the test fails in the current state.

### Phase 2: Logic Implementation
- [ ] Update `src/ibis_profiling/__init__.py`: Modify `_run_advanced_pass` to use the robust conversion logic.
- [ ] Ensure that `isoparse` is only called for strings/bytes.

### Phase 3: Verification & Cleanup
- [ ] Run the reproduction test and ensure it passes.
- [ ] Run the full test suite to ensure no regressions.
- [ ] Update documentation if necessary (none expected for this internal change).

## Testing Strategy
- **Reproduction Test:** Ensure `datetime` objects don't break the histogram.
- **Regression Test:** Ensure string values (from serialized reports) still work.
- **Edge Cases:**
  - `None` values.
  - Invalid strings.
  - `datetime.date` objects.
