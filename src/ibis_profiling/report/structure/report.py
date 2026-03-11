from ..presentation.core import Container, Table
from .overview import get_overview_section
from .correlations import get_correlations_section
from .variables.render_numeric import render_numeric
from .variables.render_categorical import render_categorical


class Report:
    """Canonical Report Assembler that mirrors ydata's hierarchical structure."""

    def __init__(self, model: dict):
        self.model = model

    def get_structure(self) -> Container:
        """Assembles the primary sections into a logically ordered Container."""
        sections = [
            get_overview_section(self.model.get("table", {}), self.model.get("alerts", [])),
            self._get_variables_section(),
            get_correlations_section(self.model.get("correlations", {})),
            self._get_sample_section(),
        ]
        return Container(sections, sequence_type="sections", name="report")

    def _get_variables_section(self) -> Container:
        var_items = []
        variables = self.model.get("variables", {})
        for col, stats in variables.items():
            if stats.get("type") == "Numeric":
                var_items.append(render_numeric(stats))
            else:
                var_items.append(render_categorical(stats))
        return Container(var_items, sequence_type="accordion", name="variables")

    def _get_sample_section(self) -> Container:
        items = []
        sample = self.model.get("sample", {})
        for name, data in sample.items():
            items.append(Table(data, name=name))
        return Container(items, sequence_type="list", name="sample")
