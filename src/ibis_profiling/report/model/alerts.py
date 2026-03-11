from typing import List, Dict, Any


class AlertEngine:
    """Rule-based engine to generate ydata-style alerts."""

    @staticmethod
    def get_alerts(table_stats: dict, variables: dict) -> List[Dict[str, Any]]:
        alerts = []
        n = table_stats.get("n", 0)

        for col, stats in variables.items():
            # Constant Column
            if stats.get("n_distinct") == 1:
                alerts.append({"type": "CONSTANT", "fields": [col], "level": "warning"})

            # High Correlation (to be implemented)

            # Missing Values
            p_missing = stats.get("p_missing", 0)
            if p_missing > 0.05:
                alerts.append(
                    {"type": "MISSING", "fields": [col], "value": p_missing, "level": "info"}
                )

            # Unique Values
            n_distinct = stats.get("n_distinct", 0)
            if n > 0 and n_distinct == n:
                alerts.append({"type": "UNIQUE", "fields": [col], "level": "warning"})

            # Zeros
            zeros = stats.get("zeros", 0)
            if n > 0 and (zeros / n) > 0.1:
                alerts.append({"type": "ZEROS", "fields": [col], "value": zeros, "level": "info"})

            # Skewness (to be implemented)

            # High Cardinality
            n_distinct = stats.get("n_distinct", 0)
            if n > 0 and (n_distinct / n) > 0.5 and stats.get("type") == "Categorical":
                alerts.append(
                    {
                        "type": "HIGH_CARDINALITY",
                        "fields": [col],
                        "value": n_distinct,
                        "level": "warning",
                    }
                )

        return alerts
