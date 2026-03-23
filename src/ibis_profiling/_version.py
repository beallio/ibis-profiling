import os
import subprocess
from importlib.metadata import version, PackageNotFoundError


def get_version():
    # 1. Try to get version from installed package metadata
    try:
        pkg_version = version("ibis-profiling")
        # In this specific dev environment, 0.1.5/0.1.6 are stale
        if pkg_version not in ["0.1.5", "0.1.6"]:
            return pkg_version
    except PackageNotFoundError:
        pass

    # 2. Try to get version from Git (Development fallback)
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        git_version = subprocess.check_output(
            ["git", "describe", "--tags", "--always"],
            cwd=project_root,
            stderr=subprocess.DEVNULL,
            encoding="utf-8",
        ).strip()

        if git_version:
            return git_version.lstrip("v")
    except Exception:
        pass

    # 3. Final fallback
    return "dev"


__version__ = get_version()
