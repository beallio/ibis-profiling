#!/usr/bin/env python3
"""
Automated Screenshot Utility for Ibis Profiling Reports.
Uses chromium-browser CLI in headless mode to capture report sections.
Requires: chromium-browser installed on the system path.
"""

import os
import sys
import subprocess
import argparse


def take_screenshot(url, output_path, width=1440, height=1200):
    """Captures a single screenshot using Chromium CLI."""
    cmd = [
        "chromium-browser",
        "--headless",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        f"--window-size={width},{height}",
        f"--screenshot={output_path}",
        url,
    ]
    try:
        # Give it a tiny bit of extra time to render the SPA content
        # Chromium --screenshot doesn't have a wait-for-selector, so we hope the default is enough
        # or we might need a more complex wrapper.
        # For SPA, we often need a small delay.
        # A trick is to use a slightly more complex command if needed, but let's try direct first.
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        if os.path.exists(output_path):
            print(f"Captured: {output_path}")
            return True

    except subprocess.CalledProcessError as e:
        print(f"Error capturing {url}: {e.stderr}")
    return False


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
    abs_report_path = "file://" + os.path.abspath(args.report)

    # Define the views we want to capture
    views = [
        {"name": "report_overview.png", "hash": "overview", "height": 1000},
        {"name": "report_variables.png", "hash": "variables", "height": 1200},
        {"name": "report_missing.png", "hash": "missing", "height": 1000},
    ]

    print(f"Generating screenshots for {args.report}...")
    for view in views:
        url = f"{abs_report_path}#{view['hash']}"
        output = os.path.join(args.output_dir, view["name"])

        # We use a slightly larger height to ensure content is visible
        take_screenshot(url, output, height=view["height"])

    print("\nScreenshot generation complete.")


if __name__ == "__main__":
    main()
