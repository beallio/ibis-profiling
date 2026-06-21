"""Small timing harness for profiling an Ibis table."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from typing import Any

import ibis

from ibis_profiling import profile


def benchmark_profile(
    table: ibis.Table, *, repeat: int = 1, **profile_kwargs: Any
) -> dict[str, float]:
    """Profile a table repeatedly and return elapsed-time statistics."""
    if repeat < 1:
        raise ValueError("repeat must be at least 1")

    durations = []
    for _ in range(repeat):
        started = time.perf_counter()
        profile(table, **profile_kwargs)
        durations.append(time.perf_counter() - started)

    return {
        "min_seconds": min(durations),
        "mean_seconds": statistics.fmean(durations),
        "max_seconds": max(durations),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parquet")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--minimal", action="store_true")
    args = parser.parse_args()

    connection = ibis.duckdb.connect()
    table = connection.read_parquet(args.parquet)
    result = benchmark_profile(table, repeat=args.repeat, minimal=args.minimal)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
