"""Deterministic regression dataset (2M rows x 20 cols).

Seeded so the exact same bytes are reproducible. Mixed types to exercise the
profiler: numeric, categorical, bool, date, integer-timestamp, PII-ish strings,
high-cardinality ids, nulls, and empty strings.
"""

from datetime import date

import numpy as np
import polars as pl

DEFAULT_PATH = "/tmp/ibis-profiling/regression_2M_20col.parquet"
DEFAULT_SEED = 20260620
N_ROWS = 2_000_000


def generate_regression_dataset(path: str = DEFAULT_PATH, seed: int = DEFAULT_SEED) -> str:
    """Generate the regression dataset to ``path`` and return the path."""
    import os

    os.makedirs(os.path.dirname(path), exist_ok=True)
    n = N_ROWS
    rng = np.random.default_rng(seed)

    cats = np.array(["alpha", "beta", "gamma", "delta", "epsilon", "zeta"])
    regions = np.array(["north", "south", "east", "west", "central"])
    countries = np.array(["US", "CA", "GB", "DE", "FR", "JP", "AU", "BR"])

    discount = rng.uniform(0, 0.5, n)
    discount[rng.random(n) < 0.10] = np.nan

    notes_choices = np.array(["", "ok", "review", "flagged", "n/a"])
    notes = rng.choice(notes_choices, n, p=[0.08, 0.4, 0.2, 0.12, 0.20]).astype(object)
    notes[rng.random(n) < 0.05] = None

    df = pl.DataFrame(
        {
            "id": np.arange(n, dtype=np.int64),
            "uuid_str": [f"u{v:08d}" for v in rng.integers(0, 5_000_000, n)],
            "age": rng.integers(18, 90, n),
            "income": rng.normal(60000, 15000, n),
            "score": rng.uniform(0, 1, n),
            "category": rng.choice(cats, n),
            "region": rng.choice(regions, n),
            "is_active": rng.random(n) < 0.6,
            "signup_date": [
                date(2020, 1, 1).toordinal() + int(d) for d in rng.integers(0, 1500, n)
            ],
            "last_login_ts": rng.integers(1_600_000_000, 1_750_000_000, n),
            "balance": rng.normal(0, 5000, n),
            "transactions": rng.poisson(8, n),
            "rating": rng.integers(1, 6, n),
            "email": [f"user{v}@example.com" for v in rng.integers(0, 3_000_000, n)],
            "phone": [f"555-{v:04d}" for v in rng.integers(0, 10000, n)],
            "country_code": rng.choice(countries, n),
            "discount": discount,
            "notes": notes,
            "quantity": rng.integers(1, 100, n),
            "price": np.round(rng.uniform(1, 999, n), 2),
        }
    )
    df = df.with_columns(
        pl.col("signup_date").map_elements(lambda o: date.fromordinal(o), return_dtype=pl.Date)
    )
    df.write_parquet(path)
    return path


if __name__ == "__main__":
    import sys

    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    p = generate_regression_dataset(out)
    print(f"wrote {p}")
