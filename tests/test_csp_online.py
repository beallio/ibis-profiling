import ibis
from ibis_profiling import ProfileReport


def test_csp_online_allows_cdns():
    df = ibis.memtable({"a": [1, 2, 3]})
    report = ProfileReport(df)

    # Generate HTML in online mode
    html_online = report.to_html(offline=False)

    # Verify CSP contains CDN origins
    expected_csp = "default-src 'self'; script-src 'unsafe-inline' 'unsafe-eval' 'self' https://cdn.tailwindcss.com https://unpkg.com; style-src 'unsafe-inline'; img-src 'self' data: blob: https://raw.githubusercontent.com; font-src 'self' data:; connect-src *;"
    assert f'content="{expected_csp}"' in html_online


def test_csp_offline_is_strict():
    df = ibis.memtable({"a": [1, 2, 3]})
    report = ProfileReport(df)

    # Generate HTML in offline mode
    html_offline = report.to_html(offline=True)

    # Verify CSP does NOT contain CDN origins
    assert "https://cdn.tailwindcss.com" not in html_offline
    # Note: the URLs might be in the assets dict in the JSON but shouldn't be in the CSP meta tag
    # We check the specific CSP line
    expected_csp = "default-src 'self'; script-src 'unsafe-inline' 'unsafe-eval'; style-src 'unsafe-inline'; img-src 'self' data: blob: https://raw.githubusercontent.com; font-src 'self' data:; connect-src 'none';"
    assert f'content="{expected_csp}"' in html_offline


if __name__ == "__main__":
    test_csp_online_allows_cdns()
    test_csp_offline_is_strict()
