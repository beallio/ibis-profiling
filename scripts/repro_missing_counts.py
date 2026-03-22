import ibis
import pandas as pd
from ibis_profiling import profile


def check_missing_counts():
    n = 100
    data = {"a": [1.0] * n, "b": ["x"] * n, "c": ["y"] * n}
    # Inject missing values
    data["a"][0] = None
    data["b"][0] = None
    data["c"][0] = None

    df = pd.DataFrame(data)
    table = ibis.memtable(df)
    report = profile(table)

    missing = report.to_dict()["missing"]
    print(f"Missing Bar Columns: {missing['bar']['matrix']['columns']}")
    print(f"Missing Bar Counts: {missing['bar']['matrix']['counts']}")

    heatmap_matrix = missing["heatmap"]["matrix"]
    if isinstance(heatmap_matrix, list):
        print(f"Heatmap Matrix is a list of length {len(heatmap_matrix)}")
    else:
        print(f"Heatmap Matrix is a {type(heatmap_matrix)}: {heatmap_matrix}")

    for col in ["a", "b", "c"]:
        print(f"Variable {col} n_missing: {report.to_dict()['variables'][col].get('n_missing')}")


if __name__ == "__main__":
    check_missing_counts()
