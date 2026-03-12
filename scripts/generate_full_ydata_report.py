import ibis
import pandas as pd
import numpy as np
from ibis_profiling import profile


def generate_complex_data():
    np.random.seed(42)
    n = 10000  # More data for better stats

    # 1. Numeric with skewed distribution and some nulls
    numeric_skewed = np.random.exponential(scale=2.0, size=n)
    numeric_skewed[np.random.choice(n, 500, replace=False)] = np.nan

    # 2. Categorical with high cardinality
    cats = [f"Category_{i}" for i in range(100)]
    categorical_high = np.random.choice(cats, n)

    # 3. Categorical with low cardinality and many nulls
    categorical_low = np.random.choice(["Red", "Green", "Blue", "Yellow"], n)
    # Create missing pattern correlation with numeric_skewed
    missing_indices = np.where(np.isnan(numeric_skewed))[0]
    # Make categorical_low missing where numeric_skewed is missing (positive correlation)
    categorical_low[missing_indices] = None
    # Add some random missing too
    random_missing = np.random.choice(n, 1000, replace=False)
    categorical_low[random_missing] = None

    # 4. Boolean
    boolean_col = np.random.choice([True, False], n)
    boolean_col_with_nulls = boolean_col.astype(object)
    boolean_col_with_nulls[np.random.choice(n, 200, replace=False)] = None

    # 5. Constant
    constant_col = ["ConstantValue"] * n

    # 6. Uniform numeric
    numeric_uniform = np.random.uniform(0, 100, n)

    # 7. Integers with some zeros and missing
    integers = np.random.randint(0, 10, n)
    integers[np.random.choice(n, 500, replace=False)] = 0
    # Create negative correlation of nullity with categorical_low
    # Missing where categorical_low is NOT missing
    not_missing_indices = np.where(~pd.isna(categorical_low))[0]
    integers_with_nulls = integers.astype(float)
    # Inject missing values randomly instead of just the first 800
    missing_sample_indices = np.random.choice(
        not_missing_indices, min(800, len(not_missing_indices)), replace=False
    )
    integers_with_nulls[missing_sample_indices] = np.nan

    # 8. Strongly correlated numeric columns
    x = np.linspace(0, 10, n)
    y = 2 * x + np.random.normal(0, 1, n)
    z = -1 * x + np.random.normal(0, 0.5, n)

    df = pd.DataFrame(
        {
            "numeric_skewed": numeric_skewed,
            "categorical_high": categorical_high,
            "categorical_low": categorical_low,
            "boolean_col": boolean_col_with_nulls,
            "constant_col": constant_col,
            "numeric_uniform": numeric_uniform,
            "integers_with_zeros": integers_with_nulls,
            "corr_positive": y,
            "corr_negative": z,
            "base_val": x,
        }
    )

    return df


def main():
    df = generate_complex_data()
    table = ibis.memtable(df)

    print("Profiling complex dataset (10k rows)...")
    report = profile(table)

    output_path = "/tmp/ibis-profiling/full_ydata_report.html"
    print(f"Generating report to {output_path}...")
    report.to_file(output_path, theme="ydata-like")

    print(f"SUCCESS: Report generated at {output_path}")


if __name__ == "__main__":
    main()
