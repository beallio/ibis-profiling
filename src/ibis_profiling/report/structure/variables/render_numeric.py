from ...presentation.core import Container, Table, Image
from ...formatters import fmt_numeric, fmt_percent


def render_numeric(stats: dict) -> Container:
    """Defines the structural layout for a Numeric variable."""
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
            {"name": "Mean", "value": fmt_numeric(stats.get("mean"))},
            {"name": "Minimum", "value": fmt_numeric(stats.get("min"))},
            {"name": "Maximum", "value": fmt_numeric(stats.get("max"))},
            {"name": "Zeros", "value": fmt_numeric(stats.get("n_zeros"))},
        ],
        name="summary",
    )

    # Placeholder for distribution chart
    distribution = Image(stats.get("histogram"), name="distribution")

    return Container([summary, distribution], sequence_type="grid", name="numeric_details")
