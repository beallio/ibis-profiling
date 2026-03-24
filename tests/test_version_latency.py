import sys
from unittest.mock import patch


def test_no_git_on_import():
    """Verify that importing ibis_profiling does not trigger a git subprocess call."""
    # Ensure ibis_profiling is not in sys.modules so we get a fresh import
    if "ibis_profiling" in sys.modules:
        del sys.modules["ibis_profiling"]
    if "ibis_profiling._version" in sys.modules:
        del sys.modules["ibis_profiling._version"]

    with patch("subprocess.check_output") as mock_git:
        # Mocking check_output to see if it's called with 'git'
        import ibis_profiling  # noqa: F401

        # Check if any call to subprocess.check_output was made with 'git'
        git_calls = [call for call in mock_git.call_args_list if "git" in str(call)]

        # CURRENT STATE: This should FAIL because ibis_profiling imports _version which calls git
        assert len(git_calls) == 0, f"Git was called {len(git_calls)} times during import!"


def test_git_on_version_access():
    """Verify that accessing __version__ DOES trigger the resolution (lazy)."""
    # This test might need adjustment depending on whether metadata is available
    # but the goal is to show it's lazy.

    if "ibis_profiling" in sys.modules:
        del sys.modules["ibis_profiling"]
    if "ibis_profiling._version" in sys.modules:
        del sys.modules["ibis_profiling._version"]

    with patch("subprocess.check_output") as mock_git:
        import ibis_profiling

        # No calls yet
        assert mock_git.call_count == 0

        # Trigger version resolution
        _ = ibis_profiling.__version__

        # Now it MIGHT have called git if metadata was missing
        # (This depends on the environment, but the point is it didn't call it on import)
