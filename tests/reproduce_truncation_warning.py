import ibis
import pandas as pd
import numpy as np
from ibis_profiling import ProfileReport


def test_truncation_warning():
    # Create a dataset with many columns to trigger truncation
    # Default CORRELATIONS_MAX_COLUMNS is usually 50 or 100
    # Let's create 150 columns
    n_cols = 150
    data = {f"col_{i}": np.random.rand(100) for i in range(n_cols)}
    df = pd.DataFrame(data)
    table = ibis.memtable(df)

    # We want to ensure we hit the truncation limits
    # Missing Heatmap/Matrix limits are also usually 50

    report = ProfileReport(table)

    # Check default theme
    html_default = report.to_html(theme="default")
    # Check ydata theme
    html_ydata = report.to_html(theme="ydata-like")

    # Check if "truncated" or "Displaying Top" or similar warning is in the HTML
    # For interactions it is "most interactive variables"

    # Missing Matrix truncation warning should be something like "Displaying first 50 columns"
    # Actually, let's see what the warning SHOULD be.

    # Based on my grep, neither template has a generic "truncated" warning for Correlations or Missing.

    print("Checking default theme...")
    if "truncated" in html_default.lower():
        print("Found 'truncated' in default theme")
    else:
        print("NOT found 'truncated' in default theme")

    print("Checking ydata-like theme...")
    if "truncated" in html_ydata.lower():
        print("Found 'truncated' in ydata-like theme")
    else:
        print("NOT found 'truncated' in ydata-like theme")


if __name__ == "__main__":
    test_truncation_warning()
