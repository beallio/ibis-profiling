from ..presentation.core import Container, Table, Alerts


def get_overview_section(table_stats: dict, alerts: list) -> Container:
    """Assembles the overview section of the report."""
    stats_table = Table(table_stats, name="dataset_statistics")
    alerts_comp = Alerts(alerts, name="alerts")

    return Container(items=[stats_table, alerts_comp], sequence_type="tabs", name="overview")
