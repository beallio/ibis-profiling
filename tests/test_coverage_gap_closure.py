from unittest.mock import MagicMock
import ibis
import polars as pl
from ibis_profiling.engine import ExecutionEngine
from ibis_profiling.report.report import ReportEncoder
from datetime import datetime, date


def test_engine_storage_info_unsupported():
    engine = ExecutionEngine()
    # Mock a non-duckdb backend
    mock_table = MagicMock()
    mock_table._find_backend.return_value = MagicMock(name="postgres")
    assert engine.get_storage_size(mock_table) is None

    # Mock failure in _find_backend
    mock_table._find_backend.side_effect = Exception("error")
    assert engine.get_storage_size(mock_table) is None


def test_engine_duckdb_storage_info():
    engine = ExecutionEngine()
    mock_con = MagicMock()
    mock_con.name = "duckdb"

    # Mock pragma result
    mock_res = MagicMock()
    mock_res.is_empty.return_value = False
    mock_res.__getitem__.return_value = MagicMock()
    mock_res["estimated_size"].sum.return_value = 1024
    mock_con.con.execute.return_value.pl.return_value = mock_res

    mock_table = MagicMock()
    mock_table._find_backend.return_value = mock_con

    # 1. DatabaseTable op
    mock_op = MagicMock(spec=ibis.expr.operations.relations.DatabaseTable)
    mock_op.name = "test_table"
    mock_table.op.return_value = mock_op
    assert engine.get_storage_size(mock_table) == 1024

    # 2. UnboundTable op
    mock_op = MagicMock(spec=ibis.expr.operations.relations.UnboundTable)
    mock_op.name = "test_table"
    mock_table.op.return_value = mock_op
    assert engine.get_storage_size(mock_table) == 1024

    # 3. Other op
    mock_table.op.return_value = MagicMock()
    assert engine.get_storage_size(mock_table) is None


def test_report_encoder():
    encoder = ReportEncoder()

    # datetime/date
    dt = datetime(2026, 3, 11, 12, 0)
    assert encoder.default(dt) == "2026-03-11T12:00:00"
    d = date(2026, 3, 11)
    assert encoder.default(d) == "2026-03-11"

    # NaN / Inf
    assert encoder.default(float("nan")) is None
    assert encoder.default(float("inf")) is None

    # Ibis Scalar
    # Use a real ibis scalar to ensure isinstance check works
    real_scalar = ibis.literal(42)
    assert encoder.default(real_scalar) == 42

    # item() fallback
    # Some numpy/polars types have .item()
    mock_val = MagicMock()
    mock_val.item.return_value = 10
    # We need to make sure it doesn't match other types
    # In the real code, it falls through to this if it's not datetime, scalar, etc.
    assert encoder.default(mock_val) == 10


def test_profile_report_from_excel(tmp_path):
    from ibis_profiling.report.report import ProfileReport

    excel_path = tmp_path / "test.xlsx"
    df = pl.DataFrame({"a": [1, 2, 3]})
    df.write_excel(excel_path)

    report = ProfileReport.from_excel(str(excel_path))
    assert "a" in report.variables


def test_profile_report_to_file_json(tmp_path):
    import json
    import ibis.expr.datatypes as dt
    from ibis_profiling.report.report import ProfileReport

    json_path = tmp_path / "profile_report.json"
    report = ProfileReport(pl.DataFrame([{"_dataset__row_count": 1}]), {"dummy": dt.Int64()})
    report.to_file(str(json_path))

    assert json_path.exists()
    with open(json_path) as f:
        data = json.load(f)
        assert data["table"]["n"] == 1
