import time
import pandas as pd
from ydata_profiling import ProfileReport


def main():
    path = "loan_data_5M.parquet"
    print(f"Profiling 5 Million Records from {path} with ydata-profiling (Minimal)...")

    df = pd.read_parquet(path)

    start = time.time()
    ProfileReport(df, minimal=True).get_description()
    duration = time.time() - start

    print(f"ydata-profiling 5M Duration: {duration:.2f} seconds")


if __name__ == "__main__":
    main()
