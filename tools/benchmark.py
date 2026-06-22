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
    table: ibis.Table, *, repeat: int = 1, full: bool = False, **profile_kwargs: Any
) -> dict[str, float]:
    """Profile a table repeatedly and return elapsed-time statistics.

    When ``full`` is True the timed region also serializes the report via ``to_dict()``
    (finalize + render), measuring the whole pipeline rather than just query execution.
    Extra keyword arguments are forwarded to ``profile`` (e.g. ``n_unique_threshold``).
    """
    if repeat < 1:
        raise ValueError("repeat must be at least 1")

    durations = []
    for _ in range(repeat):
        started = time.perf_counter()
        report = profile(table, **profile_kwargs)
        if full:
            report.to_dict()
        durations.append(time.perf_counter() - started)

    return {
        "min_seconds": min(durations),
        "median_seconds": statistics.median(durations),
        "mean_seconds": statistics.fmean(durations),
        "max_seconds": max(durations),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parquet")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--minimal", action="store_true")
    parser.add_argument(
        "--full",
        action="store_true",
        help="also time report serialization (profile().to_dict()), not just query execution",
    )
    parser.add_argument(
        "--kwarg",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="extra integer profile kwarg, repeatable (e.g. --kwarg n_unique_threshold=50000000)",
    )
    args = parser.parse_args()

    profile_kwargs: dict[str, Any] = {"minimal": args.minimal}
    for item in args.kwarg:
        key, _, value = item.partition("=")
        profile_kwargs[key] = int(value)

    connection = ibis.duckdb.connect()
    table = connection.read_parquet(args.parquet)
    result = benchmark_profile(table, repeat=args.repeat, full=args.full, **profile_kwargs)
    print(json.dumps(result, indent=2))
    print(f"kwargs: {profile_kwargs} full={args.full} repeat={args.repeat}")


if __name__ == "__main__":
    main()
