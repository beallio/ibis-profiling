import json
import os
import argparse
from math import isclose


def compare_metrics(v1, v2, rel_tol=1e-4):
    if v1 is None or v2 is None:
        return v1 == v2
    try:
        # ydata sometimes returns strings for numbers in some contexts, or numpy types
        f1, f2 = float(v1), float(v2)
        if f1 == 0 and f2 == 0:
            return True
        return isclose(f1, f2, rel_tol=rel_tol)
    except (ValueError, TypeError):
        return str(v1) == str(v2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=str, required=True)
    args = parser.parse_args()

    base_dir = f"/tmp/ibis-profiling/benchmarks/{args.size}"
    ibis_path = os.path.join(base_dir, "ibis_stats.json")
    ydata_path = os.path.join(base_dir, "ydata_stats.json")

    with open(ibis_path, "r") as f:
        ibis_data = json.load(f)
    with open(ydata_path, "r") as f:
        ydata_data = json.load(f)

    print(f"\n--- Discrepancy Report for {args.size} rows ---")

    # Table stats
    ibis_table = ibis_data.get("table", {})
    ydata_table = ydata_data.get("table", {})

    table_metrics = ["n", "n_var", "n_cells_missing"]
    print("\n[Global Table Statistics]")
    for m in table_metrics:
        iv = ibis_table.get(m)
        yv = ydata_table.get(m)
        match = compare_metrics(iv, yv)
        print(f"{m:20} | Ibis: {str(iv):10} | ydata: {str(yv):10} | Match: {match}")

    # Variable stats
    ibis_vars = ibis_data.get("variables", {})
    ydata_vars = ydata_data.get("variables", {})

    metrics = [
        "mean",
        "std",
        "min",
        "max",
        "n_distinct",
        "n_missing",
        "n_zeros",
        "kurtosis",
        "skewness",
    ]

    print("\n[Variable-Level Statistics Discrepancies (rel_tol=1e-4)]")
    discrepancy_count = 0
    for var in sorted(ibis_vars.keys()):
        if var not in ydata_vars:
            print(f"Variable {var} missing in ydata output")
            continue

        iv_data = ibis_vars[var]
        yv_data = ydata_vars[var]

        discrepancies = []
        for m in metrics:
            iv = iv_data.get(m)
            yv = yv_data.get(m)

            if iv is not None and yv is not None:
                if not compare_metrics(iv, yv):
                    discrepancies.append(f"{m}: Ibis={iv}, ydata={yv}")

        if discrepancies:
            discrepancy_count += 1
            print(f"Column {var}:")
            for d in discrepancies:
                print(f"  - {d}")

    if discrepancy_count == 0:
        print("No discrepancies found in the listed metrics.")
    else:
        print(f"\nFound discrepancies in {discrepancy_count} columns.")


if __name__ == "__main__":
    main()
