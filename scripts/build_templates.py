import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

TEMPLATE_DIR = Path("src/ibis_profiling/templates")


def build_template(template_path: Path):
    print(f"Building {template_path.name}...")

    with open(template_path, "r") as f:
        src_html = f.read()

    # Dummy base64 string that is valid
    dummy_encoded = "eyJhbmFseXNpcyI6IHsidGl0bGUiOiAiQlVJTEQiLCAiZGF0ZV9zdGFydCI6ICIyMDI2LTAxLTAxIiwgImRhdGVfZW5kIjogIjIwMjYtMDEtMDEifSwgInRhYmxlIjogeyJuIjogMCwgIm5fdmFyIjogMCwgIm1lbW9yeV9zaXplIjogMCwgInJlY29yZF9zaXplIjogMCwgInR5cGVzIjogeyJOdW1lcmljIjogMSwgIkNhdGVnb3JpY2FsIjogMX19LCAidmFyaWFibGVzIjogeyJhIjogeyJ0eXBlIjogIk51bWVyaWMiLCAiaGlzdG9ncmFtIjogeyJiaW5zIjogWzAsIDFdLCAiY291bnRzIjogWzEwLCAyMF19fX0sICJhbGVydHMiOiBbXX0="

    # Create a temporary file for playwright to load
    temp_path = template_path.with_suffix(".temp.html")
    with open(temp_path, "w") as f:
        # Ensure it has the dummy data
        f.write(src_html.replace("{{REPORT_DATA}}", dummy_encoded))

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))

        # Load the file
        url = f"file://{temp_path.absolute()}"
        page.goto(url, wait_until="networkidle")

        # Wait for Babel to finish (usually it replaces the script tag or mounts #root)
        page.wait_for_selector("#root", state="attached", timeout=10000)

        # 1. Extract compiled JS
        # Babel Standalone usually injects compiled code into a new script tag or executes it.
        # We can actually ask Babel to compile it explicitly for us via the page.evaluate
        compiled_js = page.evaluate("""
            () => {
                const scripts = document.querySelectorAll('script[type="text/babel"]');
                if (scripts.length === 0) return null;
                const src = scripts[0].innerHTML;
                return Babel.transform(src, { presets: ['react'] }).code;
            }
        """)

        if not compiled_js:
            print(f"Error: Could not extract compiled JS for {template_path.name}")
            return

        print(f"Compiled JS length: {len(compiled_js)}")
        if dummy_encoded in compiled_js:
            print("Found dummy_encoded in compiled JS")
        else:
            print("WARNING: dummy_encoded NOT FOUND in compiled JS!")
            # Sample around where it should be
            idx = src_html.find("ENCODED_REPORT_DATA")
            if idx != -1:
                print(f"Compiled JS snippet: {compiled_js[idx : idx + 200]}")

        # 2. Extract Tailwind CSS
        generated_css = page.evaluate("""
            () => {
                const styles = Array.from(document.querySelectorAll('style'));
                // The source template has one style tag. Anything else was injected.
                // We want the injected one that looks like Tailwind.
                const twStyle = styles.find(s => 
                    s.innerHTML.includes('--tw-') || 
                    s.innerHTML.includes('Tailwind CSS') ||
                    s.innerHTML.length > 5000
                );
                return twStyle ? twStyle.innerHTML : "";
            }
        """)

        browser.close()

    # Cleanup temp file
    os.remove(temp_path)

    # Ensure we preserve the {{REPORT_DATA}} placeholder in the compiled code
    compiled_js = compiled_js.replace(dummy_encoded, "{{REPORT_DATA}}")

    # 3. Construct production HTML
    # We want to remove Babel and Tailwind JIT scripts
    # and replace the JSX script with standard JS script

    prod_html = src_html

    # Find the start and end of the babel script tag
    babel_start = prod_html.find('<script type="text/babel">')
    babel_end = prod_html.find("</script>", babel_start) + len("</script>")

    if babel_start != -1 and babel_end != -1:
        prod_html = (
            prod_html[:babel_start]
            + f'<script type="text/javascript">{compiled_js}</script>'
            + prod_html[babel_end:]
        )
    else:
        print(f"Warning: Could not find babel script tag in {template_path.name}")

    # Remove Tailwind JIT script
    prod_html = re.sub(r"\s*<!-- Tailwind CSS -->", "", prod_html)
    prod_html = re.sub(r'\s*<script src="https://cdn.tailwindcss.com"></script>', "", prod_html)

    # Remove Babel script
    prod_html = re.sub(r"\s*<!-- Babel for in-browser JSX compilation -->", "", prod_html)
    prod_html = re.sub(
        r'\s*<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>',
        "",
        prod_html,
    )

    # Inject generated CSS if found
    if generated_css:
        # Avoid duplicate tailwind style tags if we run multiple times
        prod_html = prod_html.replace(
            "</head>", f'<style id="tailwind-static">{generated_css}</style></head>'
        )

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
