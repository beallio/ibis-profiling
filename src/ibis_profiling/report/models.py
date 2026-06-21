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


@dataclass(frozen=True)
class VariableProfile:
    type: str | None
    count: int | float | None
    n_missing: int | float | None
    p_missing: float | None
    extra: dict[str, Any]
    _present_fields: frozenset[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "VariableProfile":
        d_copy = dict(d)
        typ = d_copy.pop("type", None)
        count = d_copy.pop("count", None)
        n_missing = d_copy.pop("n_missing", None)
        p_missing = d_copy.pop("p_missing", None)
        return cls(
            type=typ,
            count=count,
            n_missing=n_missing,
            p_missing=p_missing,
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
