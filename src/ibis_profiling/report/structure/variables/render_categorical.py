from ...presentation.core import Container, Table
from ...formatters import fmt_numeric, fmt_percent


def render_categorical(stats: dict) -> Container:
    """Defines the structural layout for a Categorical variable."""
    summary = Table(
        [
            {
                "name": "Distinct",
                "value": fmt_numeric(stats.get("n_distinct")),
                "perc": fmt_percent(stats.get("p_distinct", 0)),
            },
            {
                "name": "Missing",
                "value": fmt_numeric(stats.get("n_missing")),
                "perc": fmt_percent(stats.get("p_missing", 0)),
            },
            {"name": "Unique", "value": fmt_numeric(stats.get("n_unique"))},
        ],
        name="summary",
    )

    # Placeholder for value counts table/chart
    value_counts = Table(stats.get("value_counts", []), name="common_values")

    return Container([summary, value_counts], sequence_type="grid", name="categorical_details")
