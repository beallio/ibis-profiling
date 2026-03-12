from typing import List, Dict, Any


class AlertEngine:
    """Rule-based engine to generate ydata-style alerts."""

    @staticmethod
    def get_alerts(table_stats: dict, variables: dict) -> List[Dict[str, Any]]:
        alerts = []
        n = table_stats.get("n", 0)

        for col, stats in variables.items():
            n_distinct = stats.get("n_distinct", 0)
            p_missing = stats.get("p_missing", 0)
            n_zeros = stats.get("n_zeros", 0)
            v_type = stats.get("type")

            # 1. Constant (High Priority)
            if n_distinct == 1:
                alerts.append({"alert_type": "CONSTANT", "fields": [col], "level": "warning"})
                continue  # Skip other alerts for constant columns

            # 2. Unique
            if n > 0 and n_distinct == n:
                alerts.append({"alert_type": "UNIQUE", "fields": [col], "level": "warning"})
                # We still allow MISSING/ZEROS for unique columns (e.g. PKs)

            # 3. High Cardinality (only if not unique)
            elif n > 0 and (n_distinct / n) > 0.5 and v_type == "Categorical":
                alerts.append(
                    {
                        "alert_type": "HIGH_CARDINALITY",
                        "fields": [col],
                        "value": n_distinct,
                        "level": "warning",
                    }
                )

            # 4. Missing Values
            if p_missing > 0.05:
                alerts.append(
                    {"alert_type": "MISSING", "fields": [col], "value": p_missing, "level": "info"}
                )

            # 5. Zeros
            if n > 0 and (n_zeros / n) > 0.1:
                alerts.append(
                    {"alert_type": "ZEROS", "fields": [col], "value": n_zeros, "level": "info"}
                )

            # 6. Skewness
            skew = stats.get("skewness")
            if skew is not None and abs(skew) > 10:
                alerts.append(
                    {"alert_type": "SKEWED", "fields": [col], "value": skew, "level": "info"}
                )

        return alerts
