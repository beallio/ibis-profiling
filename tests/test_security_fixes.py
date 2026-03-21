import ibis
import pandas as pd
from ibis_profiling import profile
from ibis_profiling.engine import ExecutionEngine


def test_xss_prevention():
    """Verify that potentially dangerous characters in data are escaped in HTML."""
    df = pd.DataFrame({"x": ["</script><script>alert('xss')</script>"]})
    table = ibis.memtable(df)
    report = profile(table)
    html = report.to_html()

    # The raw script tag should NOT be in the HTML
    assert "</script><script>" not in html
    # But the data should be there, escaped as unicode
    assert "\\u003c/script\\u003e\\u003cscript\\u003e" in html


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
