import pandas as pd


class ProfileReport:
    def __init__(self, raw_results: pd.DataFrame, schema: dict):
        self.raw_results = raw_results
        self.schema = schema
        self.dataset_stats = {}
        self.column_stats = {}
        self._build()

    def _build(self):
        if self.raw_results.empty:
            return

        row = self.raw_results.iloc[0]  # Single row containing all aggregates

        for col_name, dtype in self.schema.items():
            self.column_stats[col_name] = {"type": str(dtype)}

        for col, val in row.items():
            if col.startswith("_dataset__"):
                metric_name = col.replace("_dataset__", "", 1)
                self.dataset_stats[metric_name] = val
            elif "__" in col:
                col_name, metric_name = col.split("__", 1)
                if col_name in self.column_stats:
                    self.column_stats[col_name][metric_name] = val

    def to_dict(self):
        return {"dataset": self.dataset_stats, "columns": self.column_stats}
