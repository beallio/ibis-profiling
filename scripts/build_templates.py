import os
import re
import json
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright
import pandas as pd
import numpy as np
import ibis
from ibis_profiling import profile

TEMPLATE_DIR = Path("src/ibis_profiling/templates")


def get_maximal_encoded():
    # Generate data designed to trigger all components
    np.random.seed(42)
    n = 100
    df = pd.DataFrame(
        {
            "numeric_1": np.random.randn(n),
            "numeric_2": np.random.randn(n) * 10,
            "missing_a": [np.nan if i % 3 == 0 else float(i) for i in range(n)],
            "missing_b": [np.nan if i % 5 == 0 else float(i) for i in range(n)],
            "categorical": np.random.choice(["Alpha", "Beta", "Gamma"], n),
            "boolean": np.random.choice([True, False], n),
        }
    )
    # Correlated column
    df["correlated_col"] = df["numeric_1"] * 2 + np.random.randn(n) * 0.1

    table = ibis.memtable(df)
    report = profile(table, title="Maximal Build Report", compute_duplicates=True)

    report_dict = report.to_dict()
    report_json = json.dumps(report_dict)
    return base64.b64encode(report_json.encode("utf-8")).decode("utf-8")


def build_template(template_path: Path):
    print(f"Building {template_path.name}...")

    with open(template_path, "r") as f:
        src_html = f.read()

    # Maximal base64 string
    maximal_encoded = get_maximal_encoded()

    # Create a temporary file for playwright to load
    temp_path = template_path.with_suffix(".temp.html")
    with open(temp_path, "w") as f:
        f.write(src_html.replace("{{REPORT_DATA}}", maximal_encoded))

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))

        url = f"file://{temp_path.absolute()}"
        page.goto(url, wait_until="networkidle")
        page.wait_for_selector("#root", state="attached", timeout=10000)

        # 1. Extract compiled JS
        compiled_js = page.evaluate("""
            () => {
                const scripts = document.querySelectorAll('script[type="text/babel"]');
                if (scripts.length === 0) return null;
                const src = scripts[0].innerHTML;
                return Babel.transform(src, { presets: ['react'] }).code;
            }
        """)

        browser.close()

    # Cleanup temp file
    os.remove(temp_path)

    if not compiled_js:
        print(f"Error: Could not extract compiled JS for {template_path.name}")
        return

    # Preserve {{REPORT_DATA}} placeholder
    compiled_js = compiled_js.replace(maximal_encoded, "{{REPORT_DATA}}")

    prod_html = src_html

    # Find and replace Babel script block with compiled JS
    babel_start = prod_html.find('<script type="text/babel">')
    babel_end = prod_html.find("</script>", babel_start) + len("</script>")

    if babel_start != -1 and babel_end != -1:
        prod_html = (
            prod_html[:babel_start]
            + f'<script nonce="{{{{NONCE}}}}" type="text/javascript">{compiled_js}</script>'
            + prod_html[babel_end:]
        )

    # Remove Babel JIT script (Fixed Tracking Prevention)
    prod_html = re.sub(r"\s*<!-- Babel for in-browser JSX compilation -->", "", prod_html)
    prod_html = re.sub(
        r'\s*<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>',
        "",
        prod_html,
    )

    # Note: We KEEP Tailwind JIT for now to ensure perfect visuals.
    # The console suppressor added to the source files will silence the warnings.

    # Write the compiled template
    output_path = template_path.parent / f"{template_path.name.replace('.src.html', '.html')}"
    with open(output_path, "w") as f:
        f.write(prod_html)

    print(f"Generated {output_path.name}")


def main():
    templates = list(TEMPLATE_DIR.glob("*.src.html"))
    for t in templates:
        build_template(t)


if __name__ == "__main__":
    main()
