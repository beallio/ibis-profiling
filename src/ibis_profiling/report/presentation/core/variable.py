from typing import Optional
from .renderable import Renderable


class Variable(Renderable):
    """A logical representation of a variable profile section."""

    def __init__(
        self,
        top: Renderable,
        bottom: Optional[Renderable] = None,
        name: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.top = top
        self.bottom = bottom

    def render(self) -> dict:
        return {"top": self.top, "bottom": self.bottom}
