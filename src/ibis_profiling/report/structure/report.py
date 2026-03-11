from ..presentation.core import Container, Table


class Report:
    """Main entry point for report structural assembly."""

    def __init__(self, table_stats: dict, variables: dict, alerts: list):
        self.table_stats = table_stats
        self.variables = variables
        self.alerts = alerts

    def get_structure(self) -> Container:
        """Assembles the high-level sections into a single container."""
        sections = [
            self._get_overview_section(),
            self._get_variables_section(),
            # self._get_interactions_section(),
            # self._get_correlations_section(),
            # self._get_missing_values_section(),
            # self._get_sample_section()
        ]
        return Container(sections, sequence_type="sections", name="report")

    def _get_overview_section(self) -> Container:
        stats_table = Table(self.table_stats, name="dataset_statistics")
        alerts_list = Container(self.alerts, sequence_type="list", name="alerts")
        return Container([stats_table, alerts_list], sequence_type="tabs", name="overview")

    def _get_variables_section(self) -> Container:
        var_items = []
        for col, stats in self.variables.items():
            var_items.append(Container([Table(stats)], name=col))
        return Container(var_items, sequence_type="accordion", name="variables")
