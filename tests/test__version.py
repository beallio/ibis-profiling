from ibis_profiling import __version__


def test_version_format():
    """Verify that the version string exists and is not 'unknown'."""
    assert __version__ is not None
    assert __version__ != "unknown"
    # Should be something like 0.1.6 or 0.1.6-xx-gxxxx
    assert "." in __version__


def test_git_version_fallback():
    """Verify that we can manually trigger the git describe logic if metadata fails."""
    from ibis_profiling._version import get_version

    # This should return something valid if run in the project root
    v = get_version()
    assert v is not None
    assert v != "unknown"
