import ibis
import pandas as pd
from ibis_profiling import ProfileReport

# Setup logging to see what's happening if possible,
# but Ibis doesn't log SQL by default unless configured.
# We can use a custom backend or mock.


def test_query_count():
    df = pd.DataFrame({f"col{i}": [1, 2, 3, 4, 5, 1, 2, i] for i in range(10)})
    con = ibis.duckdb.connect()
    t = con.create_table("test", df)

    # We want to intercept queries. DuckDB doesn't make it easy to count queries directly
    # without looking at logs, but we can try to use a tracer if ibis supports it.

    print("Generating report...")
    profile = ProfileReport(t)
    # The complex pass is where n_unique is calculated
    profile.to_json()
    print("Done")


if __name__ == "__main__":
    test_query_count()
