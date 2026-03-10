import json
import os


def format_val(v):
    if isinstance(v, float):
        return f"{v:.6f}"
    return str(v)


def main():
    output_dir = os.getenv("IBIS_PROFILING_TMP", "/tmp/ibis-profiling")
    ibis_path = os.path.join(output_dir, "ibis_1M_full.json")
    ydata_path = os.path.join(output_dir, "ydata_1M_full.json")

    if not os.path.exists(ibis_path) or not os.path.exists(ydata_path):
        print(f"Error: Missing benchmark results in {output_dir}")
        print("Please run benchmark_ibis_1M.py and benchmark_ydata_1M.py first.")
        return

    with open(ibis_path) as f:
        ibis_res = json.load(f)
    with open(ydata_path) as f:
        ydata_res = json.load(f)

    ibis = ibis_res["report"]
    ydata = ydata_res

    print("# Full Parity Report (1 Million Records)")
    print("\n## Dataset Statistics")
    print("| Metric | Ibis-Native | ydata-profiling | Parity |")
    print("| :--- | :--- | :--- | :--- |")

    ibis_n = ibis["dataset"]["row_count"]
    ydata_n = ydata["table"]["n"]
    print(f"| Row Count (n) | {ibis_n} | {ydata_n} | {'✅' if ibis_n == ydata_n else '❌'} |")

    ibis_nvar = ibis["dataset"]["n_var"]
    ydata_nvar = ydata["table"]["n_var"]
    print(
        f"| Variables (n_var) | {ibis_nvar} | {ydata_nvar} | {'✅' if ibis_nvar == ydata_nvar else '❌'} |"
    )

    print("\n## Column Statistics (Numerical - loan_amount)")
    print("| Metric | Ibis-Native | ydata-profiling | Parity |")
    print("| :--- | :--- | :--- | :--- |")

    metrics = [
        "mean",
        "min",
        "max",
        "std",
        "sum",
        "n_distinct",
        "n_unique",
        "missing",
        "p25",
        "median",
        "p75",
    ]
    # Mapping Ibis names to ydata names
    map_names = {"missing": "n_missing", "p25": "25%", "median": "50%", "p75": "75%"}

    i_col = ibis["columns"]["loan_amount"]
    y_col = ydata["variables"]["loan_amount"]

    for m in metrics:
        y_m = map_names.get(m, m)
        iv = i_col.get(m)
        yv = y_col.get(y_m)

        # Check parity with tolerance for floats
        parity = False
        if iv is None or yv is None:
            parity = iv == yv
        elif isinstance(iv, (int, float, str)) and isinstance(yv, (int, float, str)):
            try:
                iv_f = float(iv)
                yv_f = float(yv)
                parity = abs(iv_f - yv_f) < 1e-2
            except Exception:
                parity = str(iv) == str(yv)
        else:
            parity = str(iv) == str(yv)

        label = m
        if m == "n_distinct":
            label = "Distinct"
        if m == "n_unique":
            label = "Unique (Singletons)"

        print(
            f"| {label.capitalize()} | {format_val(iv)} | {format_val(yv)} | {'✅' if parity else '❌'} |"
        )

    print("\n## Performance Summary")
    print(f"- **Ibis-Native:** {ibis_res['duration']:.4f} seconds")
    print(f"- **ydata-profiling:** {ydata_res['duration']:.4f} seconds")
    print(f"- **Speedup:** **{ydata_res['duration'] / ibis_res['duration']:.1f}x**")


if __name__ == "__main__":
    main()
