import ibis
import pandas as pd


def test_ibis_batching():
    con = ibis.duckdb.connect()
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    t = con.create_table("t", df)

    # Singleton count for 'a'
    vc_a = t.a.value_counts()
    count_a = vc_a.filter(vc_a.columns[1] == 1).count()

    # Singleton count for 'b'
    vc_b = t.b.value_counts()
    count_b = vc_b.filter(vc_b.columns[1] == 1).count()

    try:
        # In Ibis 9.0+, count() on a table returns a scalar expr.
        # But we need to make sure Ibis knows it's a scalar subquery.
        # Some backends allow .to_scalar() or .as_scalar()

        agg = t.aggregate([count_a.name("a_unique"), count_b.name("b_unique")])
        print("SQL (standard):")
        print(ibis.to_sql(agg))
    except Exception as e:
        print(f"Standard failed: {e}")

    # Try to see if we can use a simpler expression for singletons.
    # What if we use grouping?
    # No, we want a single row result.

    # Try manually constructing a scalar subquery if possible.
    # Actually, Ibis should handle this if we use the right API.


if __name__ == "__main__":
    test_ibis_batching()
