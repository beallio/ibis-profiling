from typing import List, Dict, Any


class AlertEngine:
    """Rule-based engine to generate ydata-style alerts."""

    @staticmethod
    def get_alerts(table_stats: dict, variables: dict) -> List[Dict[str, Any]]:
        # Map of (alert_type, level) -> list of fields
        grouped_alerts = {}

        n = table_stats.get("n", 0)

        for col, stats in variables.items():
            col_n = stats.get("n") or n
            n_distinct = stats.get("n_distinct") or 0
            p_missing = stats.get("p_missing") or 0.0
            n_zeros = stats.get("n_zeros") or 0
            v_type = stats.get("type")

            # 1. Constant (High Priority)
            if n_distinct == 1:
                key = ("CONSTANT", "warning")
                grouped_alerts.setdefault(key, []).append(col)
                continue

            # 2. Unique (Avoid noise on high-precision continuous floats)
            if col_n > 0 and n_distinct == col_n:
                if v_type in ["Categorical", "Numeric"]:
                    if v_type == "Categorical" or (v_type == "Numeric" and n_distinct < 1000000):
                        key = ("UNIQUE", "warning")
                        grouped_alerts.setdefault(key, []).append(col)

            # 3. High Cardinality (only if not unique)
            elif col_n > 0 and (n_distinct / col_n) > 0.5 and v_type == "Categorical":
                key = ("HIGH_CARDINALITY", "warning")
                grouped_alerts.setdefault(key, []).append(col)

            # 4. Missing Values
            if p_missing > 0.05:
                key = ("MISSING", "info")
                grouped_alerts.setdefault(key, []).append(col)

            # 5. Zeros
            if col_n > 0 and (n_zeros / col_n) > 0.1:
                key = ("ZEROS", "info")
                grouped_alerts.setdefault(key, []).append(col)

            # 6. Skewness
            skew = stats.get("skewness")
            if skew is not None and abs(skew) > 10:
                key = ("SKEWED", "info")
                grouped_alerts.setdefault(key, []).append(col)

        # Convert back to list format
        final_alerts = []
        for (alert_type, level), fields in grouped_alerts.items():
            final_alerts.append(
                {"alert_type": alert_type, "fields": sorted(fields), "level": level}
            )

        return sorted(final_alerts, key=lambda x: (x["level"] == "info", x["alert_type"]))
