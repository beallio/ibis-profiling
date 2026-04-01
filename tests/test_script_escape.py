import ibis
from ibis_profiling import ProfileReport
from ibis_profiling.report.report import ProfileReport as InternalProfileReport
import pytest


def test_script_tag_escaping_in_assets():
    # 1. Inject a "malicious" asset into the class cache
    # This simulates a vendor asset containing </script>
    malicious_content = "console.log('escape me: </script>');"
    InternalProfileReport._asset_cache["tailwind.min.js"] = malicious_content

    try:
        df = ibis.memtable({"a": [1, 2, 3]})
        report = ProfileReport(df)

        # 2. Generate offline report (which inlines assets)
        html = report.to_html(offline=True)

        # 3. Verify that raw </script> is NOT present in the HTML (except for actual closing tags)
        # We check for our specific string
        assert malicious_content not in html

        # 4. Verify that the escaped version IS present
        assert "console.log('escape me: <\\/script>');" in html

    finally:
        # Cleanup cache to avoid affecting other tests
        if "tailwind.min.js" in InternalProfileReport._asset_cache:
            del InternalProfileReport._asset_cache["tailwind.min.js"]


if __name__ == "__main__":
    pytest.main([__file__])
