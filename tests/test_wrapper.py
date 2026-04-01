import ibis
import pandas as pd
from ibis_profiling.wrapper import ProfileReport


def test_wrapper_initialization():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    table = ibis.memtable(df)

    report = ProfileReport(table, title="Wrapper Test")

    # Verify the internal report is created
    assert report._report is not None
    assert report._report.analysis["title"] == "Wrapper Test"

    # Verify to_dict works
    data = report.to_dict()
    assert "variables" in data
    assert "a" in data["variables"]
    assert "b" in data["variables"]


def test_wrapper_html_export():
    df = pd.DataFrame({"a": [1, 2, 3]})
    table = ibis.memtable(df)
    report = ProfileReport(table)

    html = report.to_html()
    assert "<html" in html
    assert "Ibis Profiling Report" in html


def test_wrapper_json_export():
    df = pd.DataFrame({"a": [1, 2, 3]})
    table = ibis.memtable(df)
    report = ProfileReport(table)

    json_data = report.to_json()
    assert '"variables"' in json_data
