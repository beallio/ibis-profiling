from typing import Any, Optional


class Renderable:
    """Base class for all report elements."""

    def __init__(self, name: Optional[str] = None, **kwargs):
        self.name = name
        self.args = kwargs

    def render(self) -> Any:
        raise NotImplementedError("Renderable is an abstract class.")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
