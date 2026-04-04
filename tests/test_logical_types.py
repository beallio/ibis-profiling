import ibis
from ibis_profiling.logical_types import (
    IbisLogicalTypeSystem,
    Categorical,
    String,
    Email,
    UUID,
    URL,
)


def test_categorical_detection():
    # con = ibis.duckdb.connect()
    # High cardinality
    df1 = ibis.memtable({"a": [str(i) for i in range(100)]})
    # Low cardinality (Categorical)
    df2 = ibis.memtable({"a": ["A", "B", "A", "B"] * 25})

    ts = IbisLogicalTypeSystem()

    assert ts.infer_type(df1, "a") == String
    assert ts.infer_type(df2, "a") == Categorical


def test_email_detection():
    # Email detection
    df_email = ibis.memtable(
        {"a": ["test@example.com", "user.name@domain.co.uk", "invalid-email"] * 10}
    )
    # All emails (except maybe some nulls/invalids, let's test robust detection)
    df_perfect_email = ibis.memtable({"a": ["a@b.com", "c@d.net"] * 10})

    ts = IbisLogicalTypeSystem()

    # Debug Email.matches directly
    is_email = Email.matches(df_perfect_email, "a")
    assert is_email, "Should be detected as Email"

    assert ts.infer_type(df_perfect_email, "a") == Email
    assert ts.infer_type(df_email, "a") == Categorical  # Low cardinality string


def test_uuid_detection():
    import uuid

    # Valid UUIDs
    df_uuid = ibis.memtable({"a": [str(uuid.uuid4()) for _ in range(10)]})

    ts = IbisLogicalTypeSystem()
    assert ts.infer_type(df_uuid, "a") == UUID


def test_url_detection():
    # Valid URLs
    df_url = ibis.memtable(
        {"a": ["https://google.com", "http://domain.co.uk/path?q=1", "ftp://files.org"] * 10}
    )
    # Mixed data (not URLs)
    df_not_url = ibis.memtable({"a": ["not a url", "http://google.com"] * 10})

    ts = IbisLogicalTypeSystem()
    assert ts.infer_type(df_url, "a") == URL
    assert ts.infer_type(df_not_url, "a") != URL
