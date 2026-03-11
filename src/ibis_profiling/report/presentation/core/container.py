from typing import List, Optional
from .renderable import Renderable


class Container(Renderable):
    """A logical grouping of other renderable elements."""

    def __init__(
        self,
        items: List[Renderable],
        sequence_type: str = "list",
        name: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.items = items
        self.sequence_type = sequence_type

    def render(self) -> List[Renderable]:
        return self.items
