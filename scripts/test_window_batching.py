import ibis
import pandas as pd


def test_window_nulls():
    con = ibis.duckdb.connect()
    df = pd.DataFrame({"a": [1, 2, None, 1]})
    t = con.create_table("t", df)

    # window count for 'a'
    win_a = ibis.window(group_by=t.a)
    count_a = t.a.count().over(win_a)
    # Important: count(col) over window excludes the current row if it is null?
    # No, count(col) counts non-nulls in the partition.
    # If the current row is null, is it in a partition with other nulls? Yes.
    # But count(t.a) for that partition will be 0 if all are null.

    is_unique_a = ((count_a == 1) & t.a.notnull()).cast("int")

    try:
        m = t.mutate(unique_a=is_unique_a)
        agg = m.aggregate([m.unique_a.sum().name("a_unique")])
        print("Data:")
        print(df)
        print("Results:")
        print(agg.execute())
    except Exception as e:
        print(f"Window batching failed: {e}")


if __name__ == "__main__":
    test_window_nulls()
