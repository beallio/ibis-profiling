from typing import List, Optional
from .renderable import Renderable


class Alerts(Renderable):
    """A logical representation of a list of alerts."""

    def __init__(self, alerts: List[dict], name: Optional[str] = None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.alerts = alerts

    def render(self) -> List[dict]:
        return self.alerts
