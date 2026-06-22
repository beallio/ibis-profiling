import os
import glob
import pytest


def pytest_collection_modifyitems(config, items):
    browsers_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")
    has_chromium = False

    if browsers_path:
        pattern = os.path.join(browsers_path, "chromium-*", "chrome-linux*", "chrome")
        if glob.glob(pattern):
            has_chromium = True

    if not has_chromium:
        skip_e2e = pytest.mark.skip(reason="Playwright Chromium absent. Skipping e2e tests.")
        for item in items:
            if "test_e2e" in item.nodeid:
                item.add_marker(skip_e2e)
