import pandas as pd
import ibis
import pyarrow as pa
import pyarrow.parquet as pq
from decimal import Decimal
from ibis_profiling import ProfileReport


def test_decimal_overflow_and_serialization(tmp_path):
    # Create a parquet file with a Decimal column that would overflow variance
    data = {"dec_val": [Decimal("34071996840314972.0"), Decimal("1.0")]}
    df = pd.DataFrame(data)
    schema = pa.schema(
        [
            ("dec_val", pa.decimal128(20, 1))  # Precision 20, Scale 1
        ]
    )
    table = pa.Table.from_pandas(df, schema=schema)
    parquet_path = tmp_path / "overflow.parquet"
    pq.write_table(table, str(parquet_path))

    con = ibis.duckdb.connect()
    t = con.read_parquet(str(parquet_path))

    # This should not raise Overflow or JSON serialization errors
    report = ProfileReport(t)
    json_data = report.to_json()

    assert "dec_val" in json_data
    # Verify the value is present and was converted to float for JSON
    import json

    data_dict = json.loads(json_data)
    stats = data_dict["variables"]["dec_val"]
    assert stats["max"] == 34071996840314972.0
    assert "mean" in stats
    assert "std" in stats
