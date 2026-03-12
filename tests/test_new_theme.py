import ibis
import pandas as pd
import numpy as np
import os
import sys

# Add src to path if not already there
if "src" not in sys.path:
    sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from ibis_profiling import profile


def test_new_theme_generation():
    # 1. Create dummy data
    df = pd.DataFrame(
        {
            "num": np.random.randn(100),
            "cat": np.random.choice(["A", "B", "C"], 100),
            "bool": np.random.choice([True, False], 100),
            "missing": [None] * 50 + [1.0] * 50,
        }
    )
    t = ibis.memtable(df)

    # 2. Profile with new theme and custom title
    custom_title = "Custom New Theme Report"
    report = profile(t, title=custom_title)

    output_path = "/tmp/ibis-profiling/test_new_theme.html"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    report.to_file(output_path, theme="new_theme")

    # 3. Verify output
    assert os.path.exists(output_path)
    with open(output_path, "r") as f:
        html = f.read()

    # Check for custom title
    assert custom_title in html

    # Check for Materialize CSS
    assert "materialize.min.css" in html

    # Check for React 18
    assert "react@18" in html

    # Check for placeholder replacement
    assert "{{REPORT_DATA}}" not in html
    assert "REPORT_DATA =" in html

    print(f"Successfully generated and verified new theme report at {output_path}")


if __name__ == "__main__":
    test_new_theme_generation()
