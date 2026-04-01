import ibis
import re
from ibis_profiling import ProfileReport


def test_csp_tightening_offline():
    df = ibis.memtable({"a": [1, 2, 3]})
    report = ProfileReport(df)
    html = report.to_html(offline=True)

    # 1. Verify nonce is present in CSP
    nonce_match = re.search(r"script-src 'nonce-([^']+)'", html)
    assert nonce_match, "Nonce missing from CSP"
    nonce = nonce_match.group(1)

    # 2. Verify all script tags have the nonce
    # We use a regex that looks for tags at the start of a line or after a newline
    # to avoid matching strings inside inlined JS (like in ReactDOM)
    script_tags = re.findall(r"(?:^|\n)\s*<script[^>]*>", html)
    for tag in script_tags:
        tag = tag.strip()
        assert f'nonce="{nonce}"' in tag, f"Script tag missing nonce: {tag}"

    # 3. Verify unsafe-inline and unsafe-eval are missing from script-src
    csp_match = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">', html)
    assert csp_match, "CSP meta tag missing"
    csp_content = csp_match.group(1)

    directives = {d.split(" ")[0]: d for d in csp_content.split("; ") if d}
    assert "'unsafe-inline'" not in directives["script-src"]
    assert "'unsafe-eval'" not in directives["script-src"]

    # 4. Verify connect-src is 'none'
    assert "connect-src 'none'" in csp_content


def test_csp_tightening_online():
    df = ibis.memtable({"a": [1, 2, 3]})
    report = ProfileReport(df)
    html = report.to_html(offline=False)

    # 1. Verify nonce is present
    nonce_match = re.search(r"script-src 'nonce-([^']+)'", html)
    assert nonce_match
    nonce = nonce_match.group(1)

    # 2. Verify script tags have nonce (including CDN ones)
    script_tags = re.findall(r"(?:^|\n)\s*<script[^>]*>", html)
    for tag in script_tags:
        tag = tag.strip()
        assert f'nonce="{nonce}"' in tag

    # 3. Verify unsafe-eval is present (required for online Tailwind)
    csp_match = re.search(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">', html)
    assert csp_match
    csp_content = csp_match.group(1)

    directives = {d.split(" ")[0]: d for d in csp_content.split("; ") if d}
    assert "'unsafe-eval'" in directives["script-src"]
    assert "'unsafe-inline'" not in directives["script-src"]

    # 4. Verify connect-src is not 'none'
    assert "connect-src *" in csp_content


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
