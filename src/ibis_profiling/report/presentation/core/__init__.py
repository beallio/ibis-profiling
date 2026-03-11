from typing import Any, List, Optional


class Renderable:
    """Base class for all report elements."""

    def __init__(self, content: Any, name: Optional[str] = None, **kwargs):
        self.content = content
        self.name = name
        self.args = kwargs


class Container(Renderable):
    """A logical grouping of other renderable elements (e.g., Tabs, Accordion)."""

    def __init__(self, items: List[Renderable], sequence_type: str = "list", **kwargs):
        super().__init__(items, **kwargs)
        self.sequence_type = sequence_type


class Table(Renderable):
    """A logical representation of a data table."""

    pass


class HTML(Renderable):
    """A raw HTML snippet."""

    pass


class Image(Renderable):
    """An image or plot."""

    pass
