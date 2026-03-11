from typing import Any, Optional
from .renderable import Renderable


class Image(Renderable):
    """A logical representation of an image or plot."""

    def __init__(self, content: Any, alt: str = "", name: Optional[str] = None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.content = content
        self.alt = alt

    def render(self) -> Any:
        return self.content
