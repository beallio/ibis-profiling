from .profiler import profile, profile_excel, Profiler
from .metrics import registry
from .wrapper import ProfileReport
from .report import ProfileReport as InternalProfileReport


def __getattr__(name):
    if name == "__version__":
        from ._version import get_version

        v = get_version()
        # Cache it in the module's globals for subsequent accesses
        globals()["__version__"] = v
        return v
    raise AttributeError(f"module {__name__} has no attribute {name}")


__all__ = [
    "profile",
    "registry",
    "ProfileReport",
    "profile_excel",
    "Profiler",
    "InternalProfileReport",
    "__version__",
]
