from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Alert:
    alert_type: str
    fields: list[str]
    level: str
    extra: dict[str, Any]
    _present_fields: frozenset[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Alert":
        d_copy = dict(d)
        alert_type = d_copy.pop("alert_type", "")
        fields = d_copy.pop("fields", [])
        level = d_copy.pop("level", "")
        return cls(alert_type, fields, level, d_copy, frozenset(d.keys()))

    def to_dict(self) -> dict[str, Any]:
        res = {
            "alert_type": self.alert_type,
            "fields": self.fields,
            "level": self.level,
            **self.extra,
        }
        return {k: res[k] for k in self._present_fields if k in res}


@dataclass(frozen=True)
class AnalysisMetadata:
    title: str
    date_start: str
    date_end: str
    extra: dict[str, Any]
    _present_fields: frozenset[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "AnalysisMetadata":
        d_copy = dict(d)
        title = d_copy.pop("title", "")
        date_start = d_copy.pop("date_start", "")
        date_end = d_copy.pop("date_end", "")
        return cls(title, date_start, date_end, d_copy, frozenset(d.keys()))

    def to_dict(self) -> dict[str, Any]:
        res = {
            "title": self.title,
            "date_start": self.date_start,
            "date_end": self.date_end,
            **self.extra,
        }
        return {k: res[k] for k in self._present_fields if k in res}


@dataclass(frozen=True)
class TableProfile:
    n: int | float
    n_var: int
    n_cells_missing: int
    n_vars_with_missing: int
    n_vars_all_missing: int
    n_vars_constant: int
    types: dict[str, int]
    extra: dict[str, Any]
    _present_fields: frozenset[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TableProfile":
        d_copy = dict(d)
        n = d_copy.pop("n", 0)
        n_var = d_copy.pop("n_var", 0)
        n_cells_missing = d_copy.pop("n_cells_missing", 0)
        n_vars_with_missing = d_copy.pop("n_vars_with_missing", 0)
        n_vars_all_missing = d_copy.pop("n_vars_all_missing", 0)
        n_vars_constant = d_copy.pop("n_vars_constant", 0)
        types = d_copy.pop("types", {})
        return cls(
            n,
            n_var,
            n_cells_missing,
            n_vars_with_missing,
            n_vars_all_missing,
            n_vars_constant,
            types,
            d_copy,
            frozenset(d.keys()),
        )

    def to_dict(self) -> dict[str, Any]:
        res = {
            "n": self.n,
            "n_var": self.n_var,
            "n_cells_missing": self.n_cells_missing,
            "n_vars_with_missing": self.n_vars_with_missing,
            "n_vars_all_missing": self.n_vars_all_missing,
            "n_vars_constant": self.n_vars_constant,
            "types": self.types,
            **self.extra,
        }
        return {k: res[k] for k in self._present_fields if k in res}


NumberStat = int | float | str | None
BoolStat = bool | str | None


@dataclass(frozen=True)
class NumericStats:
    mean: NumberStat
    std: NumberStat
    variance: NumberStat
    minimum: NumberStat
    maximum: NumberStat
    total: NumberStat
    p5: NumberStat
    p25: NumberStat
    p50: NumberStat
    p75: NumberStat
    p95: NumberStat
    mad: NumberStat
    skewness: NumberStat
    kurtosis: NumberStat
    cv: NumberStat
    iqr: NumberStat
    value_range: NumberStat
    n_zeros: NumberStat
    p_zeros: NumberStat
    n_negative: NumberStat
    p_negative: NumberStat
    n_infinite: NumberStat
    p_infinite: NumberStat
    histogram: dict[str, Any] | None
    extreme_values_smallest: list[Any] | None
    extreme_values_largest: list[Any] | None
    monotonic_increasing: BoolStat
    monotonic_decreasing: BoolStat
    extra: dict[str, Any]
    _present_fields: frozenset[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "NumericStats":
        d_copy = dict(d)
        return cls(
            mean=d_copy.pop("mean", None),
            std=d_copy.pop("std", None),
            variance=d_copy.pop("variance", None),
            minimum=d_copy.pop("min", None),
            maximum=d_copy.pop("max", None),
            total=d_copy.pop("sum", None),
            p5=d_copy.pop("5%", None),
            p25=d_copy.pop("25%", None),
            p50=d_copy.pop("50%", None),
            p75=d_copy.pop("75%", None),
            p95=d_copy.pop("95%", None),
            mad=d_copy.pop("mad", None),
            skewness=d_copy.pop("skewness", None),
            kurtosis=d_copy.pop("kurtosis", None),
            cv=d_copy.pop("cv", None),
            iqr=d_copy.pop("iqr", None),
            value_range=d_copy.pop("range", None),
            n_zeros=d_copy.pop("n_zeros", None),
            p_zeros=d_copy.pop("p_zeros", None),
            n_negative=d_copy.pop("n_negative", None),
            p_negative=d_copy.pop("p_negative", None),
            n_infinite=d_copy.pop("n_infinite", None),
            p_infinite=d_copy.pop("p_infinite", None),
            histogram=d_copy.pop("histogram", None),
            extreme_values_smallest=d_copy.pop("extreme_values_smallest", None),
            extreme_values_largest=d_copy.pop("extreme_values_largest", None),
            monotonic_increasing=d_copy.pop("monotonic_increasing", None),
            monotonic_decreasing=d_copy.pop("monotonic_decreasing", None),
            extra=d_copy,
            _present_fields=frozenset(d.keys()),
        )

    def to_dict(self) -> dict[str, Any]:
        res = {
            "mean": self.mean,
            "std": self.std,
            "variance": self.variance,
            "min": self.minimum,
            "max": self.maximum,
            "sum": self.total,
            "5%": self.p5,
            "25%": self.p25,
            "50%": self.p50,
            "75%": self.p75,
            "95%": self.p95,
            "mad": self.mad,
            "skewness": self.skewness,
            "kurtosis": self.kurtosis,
            "cv": self.cv,
            "iqr": self.iqr,
            "range": self.value_range,
            "n_zeros": self.n_zeros,
            "p_zeros": self.p_zeros,
            "n_negative": self.n_negative,
            "p_negative": self.p_negative,
            "n_infinite": self.n_infinite,
            "p_infinite": self.p_infinite,
            "histogram": self.histogram,
            "extreme_values_smallest": self.extreme_values_smallest,
            "extreme_values_largest": self.extreme_values_largest,
            "monotonic_increasing": self.monotonic_increasing,
            "monotonic_decreasing": self.monotonic_decreasing,
            **self.extra,
        }
        return {k: res[k] for k in self._present_fields if k in res}


@dataclass(frozen=True)
class TextStats:
    mean_length: NumberStat
    min_length: NumberStat
    max_length: NumberStat
    n_empty: NumberStat
    p_empty: NumberStat
    histogram: dict[str, Any] | None
    length_histogram: dict[str, Any] | None
    extreme_values_smallest: list[Any] | None
    extreme_values_largest: list[Any] | None
    extra: dict[str, Any]
    _present_fields: frozenset[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TextStats":
        d_copy = dict(d)
        return cls(
            mean_length=d_copy.pop("mean_length", None),
            min_length=d_copy.pop("min_length", None),
            max_length=d_copy.pop("max_length", None),
            n_empty=d_copy.pop("n_empty", None),
            p_empty=d_copy.pop("p_empty", None),
            histogram=d_copy.pop("histogram", None),
            length_histogram=d_copy.pop("length_histogram", None),
            extreme_values_smallest=d_copy.pop("extreme_values_smallest", None),
            extreme_values_largest=d_copy.pop("extreme_values_largest", None),
            extra=d_copy,
            _present_fields=frozenset(d.keys()),
        )

    def to_dict(self) -> dict[str, Any]:
        res = {
            "mean_length": self.mean_length,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "n_empty": self.n_empty,
            "p_empty": self.p_empty,
            "histogram": self.histogram,
            "length_histogram": self.length_histogram,
            "extreme_values_smallest": self.extreme_values_smallest,
            "extreme_values_largest": self.extreme_values_largest,
            **self.extra,
        }
        return {k: res[k] for k in self._present_fields if k in res}


NUMERIC_STAT_KEYS = frozenset(
    {
        "mean",
        "std",
        "variance",
        "min",
        "max",
        "sum",
        "5%",
        "25%",
        "50%",
        "75%",
        "95%",
        "mad",
        "skewness",
        "kurtosis",
        "cv",
        "iqr",
        "range",
        "n_zeros",
        "p_zeros",
        "n_negative",
        "p_negative",
        "n_infinite",
        "p_infinite",
        "histogram",
        "extreme_values_smallest",
        "extreme_values_largest",
        "monotonic_increasing",
        "monotonic_decreasing",
    }
)

TEXT_STAT_KEYS = frozenset(
    {
        "mean_length",
        "min_length",
        "max_length",
        "n_empty",
        "p_empty",
        "histogram",
        "length_histogram",
        "extreme_values_smallest",
        "extreme_values_largest",
    }
)


@dataclass(frozen=True)
class VariableProfile:
    type: str | None
    count: int | float | None
    n_missing: int | float | None
    p_missing: float | None
    stats: NumericStats | TextStats | None
    extra: dict[str, Any]
    _present_fields: frozenset[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "VariableProfile":
        d_copy = dict(d)
        typ = d_copy.pop("type", None)
        count = d_copy.pop("count", None)
        n_missing = d_copy.pop("n_missing", None)
        p_missing = d_copy.pop("p_missing", None)
        stats: NumericStats | TextStats | None = None
        if typ == "Numeric":
            stats = NumericStats.from_dict(
                {key: d_copy.pop(key) for key in d if key in NUMERIC_STAT_KEYS}
            )
        elif typ == "Categorical":
            stats = TextStats.from_dict(
                {key: d_copy.pop(key) for key in d if key in TEXT_STAT_KEYS}
            )
        return cls(
            type=typ,
            count=count,
            n_missing=n_missing,
            p_missing=p_missing,
            stats=stats,
            extra=d_copy,
            _present_fields=frozenset(d.keys()),
        )

    def to_dict(self) -> dict[str, Any]:
        res = {
            "type": self.type,
            "count": self.count,
            "n_missing": self.n_missing,
            "p_missing": self.p_missing,
        }
        res.update(self.extra)
        if self.stats is not None:
            res.update(self.stats.to_dict())
        # Using dict.get so we get None for missing keys, but only if they were present initially
        return {k: res.get(k) for k in self._present_fields}


@dataclass(frozen=True)
class ReportModel:
    analysis: AnalysisMetadata
    table: TableProfile
    variables: dict[str, VariableProfile]
    correlations: Any
    interactions: Any
    missing: Any
    alerts: list[Alert]
    samples: Any
    package: dict[str, str]

    @classmethod
    def from_internal(cls, report: Any) -> "ReportModel":
        from ibis_profiling import __version__

        return cls(
            analysis=AnalysisMetadata.from_dict(report.analysis),
            table=TableProfile.from_dict(report.table),
            variables={k: VariableProfile.from_dict(v) for k, v in report.variables.items()},
            correlations=report.correlations,
            interactions=report.interactions,
            missing=report.missing,
            alerts=[Alert.from_dict(a) for a in report.alerts],
            samples=report.samples,
            package={"name": "ibis-profiling", "version": __version__},
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "analysis": self.analysis.to_dict(),
            "table": self.table.to_dict(),
            "variables": {k: v.to_dict() for k, v in self.variables.items()},
            "correlations": self.correlations,
            "interactions": self.interactions,
            "missing": self.missing,
            "alerts": [a.to_dict() for a in self.alerts],
            "sample": self.samples,
            "package": self.package,
        }
