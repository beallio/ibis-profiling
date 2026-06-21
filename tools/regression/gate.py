#!/usr/bin/env python
"""Standing profiler regression gate (conservative variant for the trunk re-apply).

Profiles a fixed, deterministic 2M x 20 dataset single-threaded and diffs the result
against a committed baseline. Run after each merge to catch unintended profiler
output changes.

This variant EXCLUDES `correlations` and `interactions` from the comparison (in
addition to volatile fields): on this trunk the profiler samples them with an
unseeded `table.sample()`, so they are non-deterministic run-to-run. Everything
else (per-variable stats, types, histograms, table stats, missing, alerts, sample)
is compared exactly.

Usage:
  ./run.sh uv run python tools/regression/gate.py                 # check (exit 1 on diff)
  ./run.sh uv run python tools/regression/gate.py --update-baseline
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import dataset as ds  # noqa: E402

BASELINE = os.path.join(HERE, "baseline_2M_20col.json")


def _normalize(d: dict) -> dict:
    d = json.loads(json.dumps(d, default=str, sort_keys=True))
    d.pop("interactions", None)
    d.pop("correlations", None)
    d.pop("package", None)
    an = d.get("analysis")
    if isinstance(an, dict):
        for k in ("date_start", "date_end", "duration", "performance"):
            an.pop(k, None)
    return d


def _profile_normalized() -> dict:
    import ibis

    from ibis_profiling import profile

    if not os.path.exists(ds.DEFAULT_PATH):
        print(f"dataset missing; regenerating {ds.DEFAULT_PATH} ...", file=sys.stderr)
        ds.generate_regression_dataset()

    con = ibis.duckdb.connect()
    con.raw_sql("SET threads TO 1")  # deterministic aggregation order
    table = con.read_parquet(ds.DEFAULT_PATH)
    return _normalize(profile(table).to_dict())


def _diff(base, cur):
    out = []

    def walk(p, x, y):
        if isinstance(x, dict) and isinstance(y, dict):
            for k in set(x) | set(y):
                if k in x and k in y:
                    walk(f"{p}.{k}", x[k], y[k])
                else:
                    out.append(f"{p}.{k}: only in {'baseline' if k in x else 'current'}")
        elif isinstance(x, list) and isinstance(y, list):
            if len(x) != len(y):
                out.append(f"{p}: list len {len(x)} != {len(y)}")
            else:
                for i, (u, v) in enumerate(zip(x, y)):
                    walk(f"{p}[{i}]", u, v)
        elif x != y:
            out.append(f"{p}: {x!r} != {y!r}")

    walk("", base, cur)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--update-baseline", action="store_true", help="overwrite the baseline")
    args = ap.parse_args()

    cur = _profile_normalized()

    if args.update_baseline:
        with open(BASELINE, "w") as f:
            json.dump(cur, f, sort_keys=True, indent=2)
        print(f"baseline updated: {BASELINE}")
        return 0

    if not os.path.exists(BASELINE):
        print(f"no baseline at {BASELINE}; run with --update-baseline first", file=sys.stderr)
        return 2

    with open(BASELINE) as f:
        base = json.load(f)
    cur = json.loads(json.dumps(cur, sort_keys=True))

    diffs = _diff(base, cur)
    print(f"regression gate: {len(diffs)} differences on the deterministic surface")
    for d in diffs[:40]:
        print("  ", d)
    if len(diffs) > 40:
        print(f"   ... and {len(diffs) - 40} more")
    if diffs:
        print("RESULT: REGRESSION ❌")
        return 1
    print("RESULT: PASS ✅ (correlations/interactions excluded — non-deterministic on this trunk)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
