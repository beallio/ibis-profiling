#!/usr/bin/env python3
"""
Automated Screenshot Utility for Ibis Profiling Reports using Playwright.
Provides robust waiting for React SPAs and deep-linking support.
"""

import os
import sys
import argparse
from playwright.sync_api import sync_playwright


def take_screenshots(report_path, output_dir, width=1440):
    with sync_playwright() as p:
        # We use a standard desktop viewport
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": 900})

        abs_url = "file://" + os.path.abspath(report_path)

        # 1. Full Page Preview (Auto-resizing to content)
        print("Capturing full preview...")
        page.goto(abs_url)
        # Wait for the main title to ensure React has rendered
        page.wait_for_selector("text=Ibis Profiler", state="attached", timeout=15000)
        # Small sleep for any final animations or chart rendering
        page.wait_for_timeout(3000)

        preview_path = os.path.join(output_dir, "report_preview.png")
        page.screenshot(path=preview_path, full_page=True)
        print(f"Saved: {preview_path}")

        # 2. Overview Section
        print("Capturing overview...")
        page.goto(f"{abs_url}#overview")
        page.wait_for_timeout(1000)
        overview_path = os.path.join(output_dir, "report_overview.png")
        page.screenshot(path=overview_path)
        print(f"Saved: {overview_path}")

        # 3. Variables Section
        print("Capturing variables...")
        page.goto(f"{abs_url}#variables")
        page.wait_for_timeout(1000)
        vars_path = os.path.join(output_dir, "report_variables.png")
        page.screenshot(path=vars_path)
        print(f"Saved: {vars_path}")

        # 4. Missing Tab
        print("Capturing missing tab...")
        page.goto(f"{abs_url}#missing")
        page.wait_for_timeout(1000)
        # Check if missing matrix is present (some reports might not have it)
        missing_path = os.path.join(output_dir, "report_missing.png")
        page.screenshot(path=missing_path)
        print(f"Saved: {missing_path}")

        browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Generate screenshots for an Ibis Profiling report."
    )
    parser.add_argument("report", help="Path to the HTML report file.")
    parser.add_argument(
        "--output-dir",
        default="src/ibis_profiling/assets/img",
        help="Directory to save screenshots.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.report):
        print(f"Error: Report file '{args.report}' not found.")
        sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Generating screenshots for {args.report} using Playwright...")
    try:
        take_screenshots(args.report, args.output_dir)
        print("\nScreenshot generation complete.")
    except Exception as e:
        print(f"Error during screenshot generation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
