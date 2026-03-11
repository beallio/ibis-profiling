from ..presentation.core import Container, Table, Image
from .variables.render_numeric import render_numeric
from .variables.render_categorical import render_categorical


class Report:
    """Canonical Report Assembler following ydata section hierarchy."""

    def __init__(self, model: dict):
        self.model = model
        self.table = model.get("table", {})
        self.variables = model.get("variables", {})
        self.alerts = model.get("alerts", [])
        self.correlations = model.get("correlations", {})
        self.missing = model.get("missing", {})
        self.sample = model.get("sample", {})

    def get_structure(self) -> Container:
        """Assembles the seven primary sections of a YData report."""
        sections = [
            self._get_overview_section(),
            self._get_variables_section(),
            self._get_correlations_section(),
            self._get_missing_values_section(),
            self._get_sample_section(),
        ]
        return Container(sections, sequence_type="sections", name="report")

    def _get_overview_section(self) -> Container:
        stats_table = Table(self.table, name="dataset_statistics")
        alerts_list = Container(self.alerts, sequence_type="list", name="alerts")
        return Container([stats_table, alerts_list], sequence_type="tabs", name="overview")

    def _get_variables_section(self) -> Container:
        var_items = []
        for col, stats in self.variables.items():
            if stats.get("type") == "Numeric":
                var_items.append(render_numeric(stats))
            else:
                var_items.append(render_categorical(stats))
        return Container(var_items, sequence_type="accordion", name="variables")

    def _get_correlations_section(self) -> Container:
        # Each correlation matrix is a tab
        items = []
        for name, data in self.correlations.items():
            items.append(Table(data, name=name))
        return Container(items, sequence_type="tabs", name="correlations")

    def _get_missing_values_section(self) -> Container:
        items = []
        for name, data in self.missing.items():
            items.append(Image(data, name=name))
        return Container(items, sequence_type="tabs", name="missing_values")

    def _get_sample_section(self) -> Container:
        items = []
        for name, data in self.sample.items():
            items.append(Table(data, name=name))
        return Container(items, sequence_type="list", name="sample")
