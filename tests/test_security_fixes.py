import ibis
import pandas as pd
from ibis_profiling import profile
from ibis_profiling.engine import ExecutionEngine


def test_xss_prevention():
    """Verify that potentially dangerous characters in data are Base64 encoded in HTML."""
    import base64
    import json

    df = pd.DataFrame({"x": ["</script><script>alert('xss')</script>"]})
    table = ibis.memtable(df)
    report = profile(table)
    html = report.to_html()

    # The raw script tag should NOT be in the HTML
    assert "</script><script>" not in html

    # We assume the data is Base64 encoded.
    # Let's find the Base64 string.
    # It's injected into {{REPORT_DATA}} which is assigned to ENCODED_REPORT_DATA
    import re

    match = re.search(r'const ENCODED_REPORT_DATA = "(.*?)";', html)
    assert match is not None
    encoded_data = match.group(1)

    # Decode and verify
    decoded_json = base64.b64decode(encoded_data).decode("utf-8")
    data = json.loads(decoded_json)
    assert (
        data["variables"]["x"]["histogram"]["bins"][0] == "</script><script>alert('xss')</script>"
    )


def test_sql_injection_get_storage_size():
    """Verify that malformed table names don't cause SQL injection."""
    engine = ExecutionEngine()

    # Mock a table with a malicious name
    # In practice, this might come from a backend that allows weird table names
    class MockOp:
        def __init__(self, name):
            self.name = name

    class MockTable:
        def op(self):
            return MockOp("'); DROP TABLE students; --")

    # Should return None or handle safely without executing malicious SQL
    size = engine.get_storage_size(MockTable())
    assert size is None
