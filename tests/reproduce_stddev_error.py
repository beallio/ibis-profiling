import ibis
from ibis_profiling.metrics import safe_col


def test_manual_corr_fix():
    data_path = "/tmp/ibis-profiling/bench_data_500000.parquet"
    con = ibis.duckdb.connect()
    table = con.read_parquet(data_path)

    c1, c2 = "id", "mostly_null"

    s1 = safe_col(table[c1])
    s2 = safe_col(table[c2])

    # Manual pearson
    expr = s1.cov(s2, how="pop") / (s1.std(how="pop") * s2.std(how="pop"))

    print(f"Executing manual correlation for ({c1}, {c2})...")
    try:
        res = table.aggregate(expr.name("corr")).execute()
        print(f"Result:\n{res}")
    except Exception as e:
        print(f"FAILED: {e}")


if __name__ == "__main__":
    test_manual_corr_fix()
