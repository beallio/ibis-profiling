from ..presentation.core import Container, Table


def get_correlations_section(correlations: dict) -> Container:
    """Assembles the correlations section of the report."""
    items = []
    for name, data in correlations.items():
        if data.get("matrix"):
            items.append(Table(data, name=name))

    return Container(items=items, sequence_type="tabs", name="correlations")
