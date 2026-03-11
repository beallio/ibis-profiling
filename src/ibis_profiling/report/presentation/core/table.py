from typing import Any, Optional
from .renderable import Renderable


class Table(Renderable):
    """A logical representation of a data table."""

    def __init__(self, data: Any, name: Optional[str] = None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.data = data

    def render(self) -> Any:
        return self.data
