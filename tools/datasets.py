"""Reusable synthetic dataset helpers for profiling scripts."""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import polars as pl


def generate_dataframe(*, rows: int, columns: int = 8, seed: int = 42) -> pl.DataFrame:
    """Generate a deterministic mixed-type Polars DataFrame."""
    if rows < 0:
        raise ValueError("rows must be non-negative")
    if columns < 1:
        raise ValueError("columns must be at least 1")

    rng = random.Random(seed)
    generators = (
        lambda: [rng.randrange(0, max(rows, 1) * 10) for _ in range(rows)],
        lambda: [rng.uniform(-1_000.0, 1_000.0) for _ in range(rows)],
        lambda: [f"text_{rng.randrange(1_000)}" for _ in range(rows)],
        lambda: [rng.choice(("alpha", "beta", "gamma", "delta")) for _ in range(rows)],
        lambda: [datetime(2020, 1, 1) + timedelta(days=rng.randrange(1_826)) for _ in range(rows)],
        lambda: [rng.choice((True, False)) for _ in range(rows)],
    )
    prefixes = ("integer", "numeric", "text", "category", "datetime", "boolean")

    data: dict[str, Any] = {}
    for index in range(columns):
        kind = index % len(generators)
        data[f"{prefixes[kind]}_{index}"] = generators[kind]()
    return pl.DataFrame(data)


def write_parquet(path: str | Path, *, rows: int, columns: int = 8, seed: int = 42) -> Path:
    """Generate a synthetic DataFrame, write it to Parquet, and return its path."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    generate_dataframe(rows=rows, columns=columns, seed=seed).write_parquet(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--cols", type=int, default=8)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    output = write_parquet(args.out, rows=args.rows, columns=args.cols, seed=args.seed)
    print(output)


if __name__ == "__main__":
    main()
