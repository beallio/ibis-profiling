import pandas as pd
from click.testing import CliRunner
from ibis_profiling.cli import main
import os


def test_cli_format_override_html_to_json_ext():
    """Verify --format html produces HTML even if output ends in .json"""
    runner = CliRunner()
    df = pd.DataFrame({"a": [1, 2, 3]})

    with runner.isolated_filesystem():
        df.to_csv("data.csv", index=False)
        # Force HTML format on a .json file
        result = runner.invoke(
            main, ["-f", "data.csv", "--output", "report.json", "--format", "html"]
        )

        assert result.exit_code == 0
        assert os.path.exists("report.json")

        with open("report.json", "r") as f:
            content = f.read()
            # HTML should start with <!DOCTYPE html> or at least contain <html>
            assert "<!DOCTYPE html>" in content or "<html>" in content
            # It should NOT be a valid JSON
            import json

            try:
                json.loads(content)
                assert False, "Should not be valid JSON"
            except json.JSONDecodeError:
                pass


def test_cli_format_override_json_to_html_ext():
    """Verify --format json produces JSON even if output ends in .html"""
    runner = CliRunner()
    df = pd.DataFrame({"a": [1, 2, 3]})

    with runner.isolated_filesystem():
        df.to_csv("data.csv", index=False)
        # Force JSON format on a .html file
        result = runner.invoke(
            main, ["-f", "data.csv", "--output", "report.html", "--format", "json"]
        )

        assert result.exit_code == 0
        assert os.path.exists("report.html")

        with open("report.html", "r") as f:
            content = f.read()
            # Should be valid JSON
            import json

            data = json.loads(content)
            assert "variables" in data
            assert "analysis" in data
