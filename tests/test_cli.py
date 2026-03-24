import os
import pytest
from click.testing import CliRunner
from ibis_profiling.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "test.csv"
    path.write_text("id,val\n1,a\n2,b\n3,a")
    return str(path)


@pytest.fixture
def sample_parquet(tmp_path):
    import polars as pl

    path = tmp_path / "test.parquet"
    df = pl.DataFrame({"id": [1, 2, 3], "val": ["a", "b", "a"]})
    df.write_parquet(path)
    return str(path)


def test_cli_csv(runner, sample_csv, tmp_path):
    output = tmp_path / "report.html"
    result = runner.invoke(main, ["--file-path", sample_csv, "--output", str(output)])
    assert result.exit_code == 0
    assert os.path.exists(output)
    assert "Report successfully generated" in result.output


def test_cli_parquet(runner, sample_parquet, tmp_path):
    output = tmp_path / "report.html"
    result = runner.invoke(main, ["--file-path", sample_parquet, "--output", str(output)])
    assert result.exit_code == 0
    assert os.path.exists(output)
    assert "Report successfully generated" in result.output


def test_cli_json(runner, sample_csv, tmp_path):
    output = tmp_path / "report.json"
    result = runner.invoke(main, ["--file-path", sample_csv, "--output", str(output)])
    assert result.exit_code == 0
    assert os.path.exists(output)
    assert "Generating JSON report" in result.output


def test_cli_minimal(runner, sample_csv, tmp_path):
    output = tmp_path / "report.html"
    result = runner.invoke(main, ["--file-path", sample_csv, "--output", str(output), "--minimal"])
    assert result.exit_code == 0
    assert os.path.exists(output)


def test_cli_invalid_file(runner):
    result = runner.invoke(main, ["--file-path", "nonexistent.csv"])
    assert result.exit_code != 0
    assert "Error: File not found" in result.output


def test_cli_version(runner):
    from ibis_profiling import __version__

    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_cli_help(runner):
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Ultra-high-performance data profiling natively for Ibis" in result.output
    assert "--version" in result.output
    assert "-h, --help" in result.output
