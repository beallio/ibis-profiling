from pathlib import Path


def test_plans_directory():
    assert Path("docs/plans").exists()


def test_gemini_file():
    assert Path("GEMINI.md").exists()
