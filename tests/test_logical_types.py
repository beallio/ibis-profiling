import ibis
from ibis_profiling.logical_types import (
    IbisLogicalTypeSystem,
    Categorical,
    String,
    Email,
    UUID,
    URL,
    IPAddress,
    PhoneNumber,
    Boolean,
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


def test_ip_address_detection():
    # IPv4
    df_ipv4 = ibis.memtable({"a": ["192.168.1.1", "8.8.8.8", "127.0.0.1"] * 10})
    # IPv6
    df_ipv6 = ibis.memtable(
        {"a": ["2001:0db8:85a3:0000:0000:8a2e:0370:7334", "::1", "fb00::1"] * 10}
    )
    # Mixed data
    df_not_ip = ibis.memtable({"a": ["not an ip", "192.168.1.1"] * 10})

    ts = IbisLogicalTypeSystem()
    assert ts.infer_type(df_ipv4, "a") == IPAddress
    assert ts.infer_type(df_ipv6, "a") == IPAddress
    assert ts.infer_type(df_not_ip, "a") != IPAddress


def test_phone_number_detection():
    # E.164
    df_e164 = ibis.memtable({"a": ["+1234567890", "+442071234567", "+1-541-754-3010"] * 10})
    # US format
    df_us = ibis.memtable({"a": ["(541) 754-3010", "541-754-3010", "5417543010"] * 10})
    # Mixed data
    df_not_phone = ibis.memtable({"a": ["not a phone", "123"] * 10})

    ts = IbisLogicalTypeSystem()
    assert ts.infer_type(df_e164, "a") == PhoneNumber
    assert ts.infer_type(df_us, "a") == PhoneNumber
    assert ts.infer_type(df_not_phone, "a") != PhoneNumber


def test_boolean_detection():
    # Yes/No strings
    df_yes_no = ibis.memtable({"a": ["yes", "no", "Yes", "NO"] * 10})
    # 1/0 integers
    df_one_zero = ibis.memtable({"a": [1, 0, 1, 0] * 10})
    # True/False strings
    df_true_false = ibis.memtable({"a": ["true", "false", "t", "f"] * 10})

    ts = IbisLogicalTypeSystem()
    assert ts.infer_type(df_yes_no, "a") == Boolean
    assert ts.infer_type(df_one_zero, "a") == Boolean
    assert ts.infer_type(df_true_false, "a") == Boolean
