import ibis
import polars as pl
import os
from ibis_profiling import ProfileReport


def test_html_minification():
    df = pl.DataFrame({"a": [1, 2, 3]})
    table = ibis.memtable(df)
    report = ProfileReport(table)

    # Test with minification (default)
    html_min = report.to_html()
    # Test without minification
    html_full = report.to_html(minify=False)

    assert len(html_min) < len(html_full)
    # Check that minified has fewer newlines
    assert html_min.count("\n") < html_full.count("\n")

    # Test to_file with and without minify
    min_path = "/tmp/ibis-profiling/minified.html"
    full_path = "/tmp/ibis-profiling/full.html"

    report.to_file(min_path, minify=True)
    report.to_file(full_path, minify=False)

    assert os.path.getsize(min_path) < os.path.getsize(full_path)

    # Cleanup
    if os.path.exists(min_path):
        os.remove(min_path)
    if os.path.exists(full_path):
        os.remove(full_path)


if __name__ == "__main__":
    test_html_minification()
    print("Minification test passed!")
