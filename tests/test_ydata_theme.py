import os
import ibis
from ibis_profiling import ProfileReport


def test_ydata_theme_interactions(tmp_path):
    # Create a small table with numeric columns
    data = {
        "x": [1.0, 2.0, 3.0, 4.0, 5.0],
        "y": [5.0, 4.0, 3.0, 2.0, 1.0],
    }
    table = ibis.memtable(data)

    # Run profile with minimal=False
    report = ProfileReport(table, minimal=False, title="Interactions Test")

    output = tmp_path / "report.html"
    report.to_file(str(output), theme="ydata-like")

    assert os.path.exists(output)
    content = output.read_text()

    # Check for Interactions section in the HTML
    assert "Interactions" in content
    assert "InteractionsSection" in content
    assert "ScatterPlot" in content
    # Check that interactions data is embedded in the JSON payload
    assert '"interactions":{"x":{"y":[{"x":1.0,"y":5.0}' in content


def test_ydata_theme_no_interactions_when_minimal(tmp_path):
    # Create a small table with numeric columns
    data = {
        "x": [1.0, 2.0, 3.0, 4.0, 5.0],
        "y": [5.0, 4.0, 3.0, 2.0, 1.0],
    }
    table = ibis.memtable(data)

    # Run profile with minimal=True
    report = ProfileReport(table, minimal=True, title="No Interactions Test")

    output = tmp_path / "report.html"
    report.to_file(str(output), theme="ydata-like")

    assert os.path.exists(output)
    content = output.read_text()

    # Check that Interactions section is NOT in the navItems (in the embedded JSON it should be empty)
    # The string "Interactions" might still be in the React component definition but not in navItems
    assert '"interactions":{}' in content
