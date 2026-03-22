import ibis
import numpy as np
import pandas as pd
from ibis_profiling import profile
import os
from datetime import datetime, timedelta


def create_edge_case_data(n=1000):
    """Generates data with edge cases like all nulls, constant values, etc."""
    rng = np.random.default_rng(42)

    # Timestamps
    start_date = datetime(2020, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n)]

    data = {
        "all_missing": [None] * n,
        "constant_num": [42.0] * n,
        "constant_str": ["stable"] * n,
        "bool_true": [True] * n,
        "bool_mixed": rng.choice([True, False, None], n),
        "high_cardinality": [f"user_{i}" for i in range(n)],
        "timestamp": dates,
        "numeric_with_extreme": [
            1e15 if i == 0 else -1e15 if i == 1 else rng.random() for i in range(n)
        ],
        "numeric_with_nan": [float("nan") if i % 10 == 0 else rng.random() for i in range(n)],
        "empty_strings": ["" if i % 5 == 0 else "content" for i in range(n)],
        "whitespace_only": [" " if i % 7 == 0 else "valid" for i in range(n)],
    }

    # Add many columns to test rotation (e.g., 10 more numeric columns)
    for i in range(10):
        data[f"extra_col_{i:02d}"] = rng.standard_normal(n)
        # Inject some missingness into extra columns
        mask = rng.random(n) < (i / 100.0)  # progressively more missing
        for j in range(n):
            if mask[j]:
                data[f"extra_col_{i:02d}"][j] = None

    return ibis.memtable(pd.DataFrame(data))


def create_correlated_data(n=1000):
    """Generates data with strong correlations and interactions."""
    rng = np.random.default_rng(123)
    x = rng.standard_normal(n)

    data = {
        "linear_pos": x * 2 + rng.normal(0, 0.1, n),
        "linear_neg": -x * 3 + rng.normal(0, 0.5, n),
        "quadratic": x**2 + rng.normal(0, 0.1, n),
        "sinusoidal": np.sin(x * 3) + rng.normal(0, 0.05, n),
        "random_normal": rng.standard_normal(n),
        "random_uniform": rng.uniform(-5, 5, n),
        "categorical_grouped": rng.choice(["A", "B", "C"], n),
    }
    # Add dependent categoricals
    data["dependent_cat"] = [
        f"{data['categorical_grouped'][i]}_{rng.choice([1, 2])}" for i in range(n)
    ]

    # Inject missing values to some correlated columns
    for col in ["linear_pos", "quadratic", "categorical_grouped"]:
        mask = rng.random(n) < 0.1
        for i in range(n):
            if mask[i]:
                data[col][i] = None

    return ibis.memtable(pd.DataFrame(data))


def create_financial_data(n=10000):
    """Generates synthetic loan/financial data (subset of generate_test_data.py)."""
    rng = np.random.default_rng(99)
    data = {
        "loan_amount": rng.uniform(5000, 50000, size=n),
        "interest_rate": rng.uniform(0.05, 0.25, size=n),
        "term_months": rng.choice([12, 24, 36, 48, 60, 72, 84], size=n),
        "credit_score": rng.integers(300, 850, size=n).astype(float),
        "loan_status": rng.choice(["Current", "Fully Paid", "Late", "Default"], size=n),
        "region": rng.choice(["West", "Midwest", "South", "Northeast"], size=n),
    }
    # Inject missing values
    for col in ["interest_rate", "loan_status", "region"]:
        mask = rng.random(n) < 0.05
        for i in range(n):
            if mask[i]:
                data[col][i] = None

    return ibis.memtable(pd.DataFrame(data))


def main():
    output_dir = "/tmp/ibis-profiling/test_reports/comprehensive"
    os.makedirs(output_dir, exist_ok=True)

    datasets = [
        ("edge_cases", create_edge_case_data(1000)),
        ("correlated", create_correlated_data(1000)),
        ("financial", create_financial_data(10000)),
    ]

    themes = ["default", "ydata-like"]

    for name, table in datasets:
        print(f"Profiling {name} dataset...")
        report = profile(table, title=f"Comprehensive Test: {name.replace('_', ' ').title()}")

        for theme in themes:
            filename = f"{name}_{theme}.html"
            path = os.path.join(output_dir, filename)
            print(f"  Generating {theme} report -> {path}")
            report.to_file(path, theme=theme)

    print(f"\nExhaustive test reports generated in: {output_dir}")


if __name__ == "__main__":
    main()
