import ibis
import json
from ibis_profiling import profile


def main():
    path = "loan_data_1M.parquet"
    con = ibis.duckdb.connect()
    table = con.read_parquet(path)
    report = profile(table)

    with open("ibis_1M_full.json", "w") as f:
        json.dump(report.to_dict(), f, indent=2)
    print("Full Ibis stats saved to ibis_1M_full.json")


if __name__ == "__main__":
    main()
