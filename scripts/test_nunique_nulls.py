import ibis
import pandas as pd


def test_nunique_nulls():
    con = ibis.duckdb.connect()
    df = pd.DataFrame({"a": [1, 2, None, 1]})
    t = con.create_table("t", df)

    nunique = t.a.nunique().execute()
    count = t.a.count().execute()
    total = t.count().execute()

    print(f"Data: {df['a'].tolist()}")
    print(f"nunique: {nunique} (should be 2: [1, 2])")
    print(f"count (non-null): {count} (should be 3: [1, 2, 1])")
    print(f"total: {total} (should be 4)")


if __name__ == "__main__":
    test_nunique_nulls()
