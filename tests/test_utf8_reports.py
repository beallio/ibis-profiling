import os
import ibis
import pytest
import json
import base64
import re
from ibis_profiling import ProfileReport


def test_utf8_report_content(tmp_path):
    # Create data with various UTF-8 characters
    data = {
        "text": [
            "Hello World",
            "Emojis: 🚀🔥🌈",
            "CJK: 你好世界",
            "Special: \u2022 \u2122 \u00ae",
            "German: Müller Straße",
            None,
        ],
        "values": [1, 2, 3, 4, 5, 6],
    }
    table = ibis.memtable(data)

    # Test both themes
    for theme in ["default", "ydata-like"]:
        report = ProfileReport(table, title=f"UTF-8 Test {theme}")
        output_file = tmp_path / f"report_{theme}.html"
        report.to_file(str(output_file), theme=theme)

        assert os.path.exists(output_file)
        html_content = output_file.read_text(encoding="utf-8")

        # Extract Base64 encoded data
        match = re.search(r'const ENCODED_REPORT_DATA = "(.*?)";', html_content)
        assert match is not None, f"Could not find ENCODED_REPORT_DATA in {theme} report"

        encoded_data = match.group(1)
        # Decode using Python (equivalent to TextDecoder in JS)
        decoded_json = base64.b64decode(encoded_data).decode("utf-8")
        report_data = json.loads(decoded_json)

        # Verify characters are preserved in the parsed object
        # The sample structure is {"head": {"col1": [vals], ...}}
        head_sample = report_data["sample"]["head"]
        text_values = head_sample["text"]

        assert "Emojis: 🚀🔥🌈" in text_values
        assert "CJK: 你好世界" in text_values
        assert "German: Müller Straße" in text_values


if __name__ == "__main__":
    # Manual run if needed
    pytest.main([__file__])
