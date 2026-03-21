import ibis
import pandas as pd
import numpy as np
from ibis_profiling import profile
import os
import time


def generate_5M_data(n=5_000_000):
    rng = np.random.default_rng(42)
    data = {
        "id": np.arange(n),
        "val_numeric": rng.normal(100, 15, n),
        "val_monotonic": np.sort(rng.uniform(0, 1000, n)),
        "val_with_nulls": [None if i % 10 == 0 else float(i) for i in range(n)],
        "val_also_nulls": [None if i % 7 == 0 else float(i) for i in range(n)],
        "category": rng.choice(["A", "B", "C", "D", "E"], size=n),
    }
    return ibis.memtable(pd.DataFrame(data))


def main():
    output_dir = "/tmp/ibis-profiling/verify_5M"
    os.makedirs(output_dir, exist_ok=True)

    print("Generating 5M x 5col dataset...")
    table = generate_5M_data()

    # 1. Full Profile (Now includes Spearman/Mono by default)
    print("\n1. Generating FULL profile (default)...")
    start = time.time()
    report_full = profile(table, minimal=False, title="5M Full Default")
    report_full.to_file(os.path.join(output_dir, "full_default.html"))
    report_full.to_file(os.path.join(output_dir, "full_default.json"))
    print(f"   Done in {time.time() - start:.2f}s")

    # 2. Minimal Profile
    print("\n2. Generating MINIMAL profile...")
    start = time.time()
    report_min = profile(table, minimal=True, title="5M Minimal")
    report_min.to_file(os.path.join(output_dir, "minimal.html"))
    print(f"   Done in {time.time() - start:.2f}s")

    # 3. Full with explicit disabling
    print("\n3. Generating FULL profile (explicitly disabling expensive checks)...")
    start = time.time()
    report_explicit = profile(
        table,
        minimal=False,
        correlations=False,
        monotonicity=False,
        title="5M Full No-Spearman-No-Mono",
    )
    report_explicit.to_file(os.path.join(output_dir, "full_no_expensive.html"))
    print(f"   Done in {time.time() - start:.2f}s")

    print(f"\nVerification complete. Reports in {output_dir}")


if __name__ == "__main__":
    main()
