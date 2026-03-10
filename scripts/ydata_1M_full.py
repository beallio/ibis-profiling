import json
import pandas as pd
from ydata_profiling import ProfileReport


def main():
    path = "loan_data_1M.parquet"
    df = pd.read_parquet(path)

    # Run minimal profile to get the core stats
    profile = ProfileReport(df, minimal=True)
    stats = profile.get_description()

    # Extract only the serializable part of the description
    # ydata stats object is complex, we just need table and variables
    out = {"table": stats.table, "variables": stats.variables}

    # Convert types for JSON
    def clean_dict(d):
        if isinstance(d, dict):
            return {str(k): clean_dict(v) for k, v in d.items()}
        elif isinstance(d, (list, tuple)):
            return [clean_dict(x) for x in d]
        elif hasattr(d, "item") and not hasattr(d, "shape"):  # Scalar numpy/pandas
            try:
                return d.item()
            except Exception:
                return str(d)
        elif hasattr(d, "isoformat"):
            return d.isoformat()
        elif isinstance(d, (int, float, str, bool, type(None))):
            return d
        else:
            return str(d)

    with open("ydata_1M_full.json", "w") as f:
        json.dump(clean_dict(out), f, indent=2)
    print("Full ydata stats saved to ydata_1M_full.json")


if __name__ == "__main__":
    main()
