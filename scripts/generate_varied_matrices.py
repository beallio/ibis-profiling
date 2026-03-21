import ibis
import pandas as pd
import numpy as np
from ibis_profiling import profile
import os


def generate_varied_correlations(n=1000):
    rng = np.random.default_rng(42)

    # 1. Linear relationship (Pearson/Spearman ~0.9)
    x = rng.normal(0, 1, n)
    y = x + rng.normal(0, 0.3, n)

    # 2. Inverse relationship (Pearson/Spearman ~ -0.9)
    z = -x + rng.normal(0, 0.3, n)

    # 3. Non-linear but monotonic (Spearman > Pearson)
    w = np.exp(x)

    # 4. Varied Nullity
    # col_a has nulls at start
    # col_b has nulls overlapping with a
    # col_c has nulls independent of a
    nulls_a = [None if i < n // 4 else 1.0 for i in range(n)]
    nulls_b = [None if i < n // 6 else 1.0 for i in range(n)]
    nulls_c = [None if i % 5 == 0 else 1.0 for i in range(n)]

    data = {
        "linear_pos": y,
        "linear_neg": z,
        "nonlinear_monotonic": w,
        "random": rng.standard_cauchy(n),
        "nulls_high_corr": nulls_a,
        "nulls_med_corr": nulls_b,
        "nulls_low_corr": nulls_c,
    }
    return ibis.memtable(pd.DataFrame(data))


def main():
    output_dir = "/tmp/ibis-profiling/varied_test"
    os.makedirs(output_dir, exist_ok=True)

    table = generate_varied_correlations()

    print("Generating report with varied correlations...")
    report = profile(table, title="Varied Correlations & Nullity")

    report.to_file(os.path.join(output_dir, "varied_matrices.html"))
    report.to_file(os.path.join(output_dir, "varied_matrices.json"))

    print(f"Report generated: {output_dir}/varied_matrices.html")


if __name__ == "__main__":
    main()
