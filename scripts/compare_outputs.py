import json
import os
import argparse
from math import isclose


def compare_metrics(ibis_val, ydata_val, rel_tol=1e-5):
    if ibis_val is None or ydata_val is None:
        return ibis_val == ydata_val
    try:
        return isclose(float(ibis_val), float(ydata_val), rel_tol=rel_tol)
    except (ValueError, TypeError):
        return str(ibis_val) == str(ydata_val)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=50000)
    parser.add_argument("--mode", type=str, default="full")
    args = parser.parse_args()

    ibis_path = f"/tmp/ibis-profiling/benchmarks/{args.size}/ibis_{args.mode}.json"
    ydata_path = f"/tmp/ibis-profiling/benchmarks/{args.size}/ydata_{args.mode}.json"

    if not os.path.exists(ibis_path) or not os.path.exists(ydata_path):
        print(f"Required JSON files for comparison not found: {ibis_path} or {ydata_path}")
        return

    with open(ibis_path, "r") as f:
        ibis_data = json.load(f)
    with open(ydata_path, "r") as f:
        ydata_data = json.load(f)

    print(f"--- Comparison Report for {args.size:,} rows ({args.mode.capitalize()} Mode) ---")

    # 1. Global Stats
    ibis_table = ibis_data.get("table", {})
    ydata_table = ydata_data.get("table", {})

    stats_to_compare = [
        "n_var",
        "n",
        "n_cells_missing",
        "n_duplicates",
        "n_vars_with_missing",
        "n_vars_all_missing",
        "memory_size",
    ]

    print("\n[Global Table Statistics]")
    for stat in stats_to_compare:
        iv = ibis_table.get(stat)
        yv = ydata_table.get(stat)
        match = compare_metrics(iv, yv)
        if stat == "memory_size":
            print(
                f"{stat:20} | Ibis: {str(iv):10} | ydata: {str(yv):10} | Present: {iv is not None}"
            )
        else:
            print(f"{stat:20} | Ibis: {str(iv):10} | ydata: {str(yv):10} | Match: {match}")

    # 2. Variable Stats
    ibis_vars = ibis_data.get("variables", {})
    ydata_vars = ydata_data.get("variables", {})

    var_metrics = [
        "mean",
        "std",
        "min",
        "max",
        "50%",
        "25%",
        "75%",
        "skewness",
        "kurtosis",
        "n_distinct",
        "n_infinite",
        "n_zeros",
        "monotonic_increasing",
        "monotonic_decreasing",
        "extreme_values_smallest",
        "extreme_values_largest",
    ]

    print("\n[Variable-Level Statistics (Sample)]")
    for var_name in sorted(ibis_vars.keys()):
        if var_name not in ydata_vars:
            print(f"Variable {var_name} missing in ydata output")
            continue

        print(f"\n--- {var_name} ---")
        iv_data = ibis_vars[var_name]
        yv_data = ydata_vars[var_name]

        for metric in var_metrics:
            iv = iv_data.get(metric)
            yv = yv_data.get(metric)
            if iv is not None or yv is not None:
                if isinstance(iv, list) or isinstance(yv, list):
                    # For extreme values, just check presence and count
                    print(
                        f"  {metric:15} | Ibis List: {len(iv) if iv else 0} | ydata List: {len(yv) if yv else 0}"
                    )
                else:
                    match = compare_metrics(iv, yv)
                    print(
                        f"  {metric:15} | Ibis: {str(iv):10} | ydata: {str(yv):10} | Match: {match}"
                    )

    # 3. Alerts
    ibis_alerts = ibis_data.get("alerts", [])
    ydata_alerts = ydata_data.get("alerts", [])

    print("\n[Alerts]")
    print(f"Ibis Alert Count: {len(ibis_alerts)}")
    print(f"ydata Alert Count: {len(ydata_alerts)}")

    # Simple count of alert types
    def get_alert_counts(alerts):
        counts = {}
        for a in alerts:
            # ydata alerts are strings in recent versions or dicts in others
            if isinstance(a, dict):
                atype = a.get("alert_type")
            else:
                atype = str(a).split(":")[0]  # Hacky parsing if string
            counts[atype] = counts.get(atype, 0) + 1
        return counts

    ia_counts = get_alert_counts(ibis_alerts)
    ya_counts = get_alert_counts(ydata_alerts)

    all_types = set(ia_counts.keys()) | set(ya_counts.keys())
    for atype in sorted(all_types, key=lambda x: str(x)):
        print(
            f"  {str(atype):20} | Ibis: {ia_counts.get(atype, 0):3} | ydata: {ya_counts.get(atype, 0):3}"
        )


if __name__ == "__main__":
    main()
