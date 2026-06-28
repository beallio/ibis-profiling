import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import ibis
import ibis.expr.datatypes as dt
import ibis.expr.types as ir


class LogicalType(ABC):
    name: str
    display_label: str

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.name = cls.__name__
        if "display_label" not in cls.__dict__:
            cls.display_label = cls.name

    @classmethod
    @abstractmethod
    def get_check_exprs(cls, col: ibis.Column) -> dict[str, ir.Scalar]:
        """Return Ibis expressions to aggregate for this logical type."""
        ...

    @classmethod
    @abstractmethod
    def evaluate(cls, results: dict[str, Any]) -> bool:
        """Evaluate aggregate results to decide whether this type matches."""
        ...

    @classmethod
    def matches(cls, table: ibis.Table, column: str) -> bool:
        """Check one table column against this logical type."""
        exprs = {
            f"{cls.name}_{key}": value for key, value in cls.get_check_exprs(table[column]).items()
        }
        result = (
            table.aggregate([value.name(key) for key, value in exprs.items()])
            .to_pandas()
            .iloc[0]
            .to_dict()
        )
        prefix = f"{cls.name}_"
        type_results = {
            key[len(prefix) :]: value for key, value in result.items() if key.startswith(prefix)
        }
        return cls.evaluate(type_results)


@dataclass(frozen=True)
class LogicalTypeRule:
    name: str
    display_label: str
    regex: str | None = None
    allowed_values: frozenset[str] | None = None
    accepted_physical_types: tuple[type[dt.DataType], ...] = (dt.String,)

    def __post_init__(self) -> None:
        if (self.regex is None) == (self.allowed_values is None):
            raise ValueError("exactly one of regex or allowed_values must be provided")

    @property
    def __name__(self) -> str:
        """Retain compatibility with callers that treated logical types as classes."""
        return self.name

    def get_check_exprs(self, col: ibis.Column) -> dict[str, ir.Scalar]:
        if not isinstance(col.type(), self.accepted_physical_types):
            return {"has_non_null": ibis.literal(False)}

        if self.regex is not None:
            all_match = (col.re_search(self.regex) | col.isnull()).all()
        else:
            values = sorted(value.lower() for value in self.allowed_values or ())
            all_match = (col.lower().isin(values) | col.isnull()).all()

        return {
            "has_non_null": col.notnull().any(),
            "all_match": all_match,
        }

    def evaluate(self, results: dict[str, Any]) -> bool:
        return bool(results.get("has_non_null", False) and results.get("all_match", False))

    def matches(self, table: ibis.Table, column: str) -> bool:
        """Check one table column against this logical type."""
        exprs = {
            f"{self.name}_{key}": value
            for key, value in self.get_check_exprs(table[column]).items()
        }
        result = (
            table.aggregate([value.name(key) for key, value in exprs.items()])
            .to_pandas()
            .iloc[0]
            .to_dict()
        )
        prefix = f"{self.name}_"
        type_results = {
            key[len(prefix) :]: value for key, value in result.items() if key.startswith(prefix)
        }
        return self.evaluate(type_results)


class String(LogicalType):
    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> dict[str, ir.Scalar]:
        return {"is_string": ibis.literal(isinstance(col.type(), dt.String))}

    @classmethod
    def evaluate(cls, results: dict[str, Any]) -> bool:
        return bool(results.get("is_string", False))


class DateTime(LogicalType):
    display_label = "Date Time"
    ISO8601_REGEX = (
        r"^\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?$"
    )

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> dict[str, ir.Scalar]:
        if isinstance(col.type(), (dt.Date, dt.Timestamp)):
            return {"dt_is_native": ibis.literal(True)}
        if isinstance(col.type(), dt.String):
            return {
                "dt_has_non_null": col.notnull().any(),
                "dt_all_match": (col.re_search(cls.ISO8601_REGEX) | col.isnull()).all(),
            }
        return {"dt_is_native": ibis.literal(False)}

    @classmethod
    def evaluate(cls, results: dict[str, Any]) -> bool:
        if results.get("dt_is_native", False):
            return True
        return bool(results.get("dt_has_non_null", False) and results.get("dt_all_match", False))


class Boolean(LogicalType):
    BOOLEAN_STRINGS = {"true", "false", "t", "f", "yes", "no", "y", "n", "1", "0"}

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> dict[str, ir.Scalar]:
        if isinstance(col.type(), dt.Boolean):
            return {"bool_is_native": ibis.literal(True)}
        if isinstance(col.type(), dt.String):
            return {
                "bool_has_non_null": col.notnull().any(),
                "bool_all_match": (col.lower().isin(cls.BOOLEAN_STRINGS) | col.isnull()).all(),
            }
        if isinstance(col.type(), dt.Integer):
            return {
                "bool_has_non_null": col.notnull().any(),
                "bool_all_match": (col.isin([0, 1]) | col.isnull()).all(),
            }
        return {"bool_is_native": ibis.literal(False)}

    @classmethod
    def evaluate(cls, results: dict[str, Any]) -> bool:
        if results.get("bool_is_native", False):
            return True
        return bool(
            results.get("bool_has_non_null", False) and results.get("bool_all_match", False)
        )


class Count(LogicalType):
    COUNT_REGEX = r"^\d+$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> dict[str, ir.Scalar]:
        if isinstance(col.type(), dt.Integer):
            return {
                "count_has_non_null": col.notnull().any(),
                "count_all_positive": ((col >= 0) | col.isnull()).all(),
            }
        if isinstance(col.type(), dt.String):
            return {
                "count_has_non_null": col.notnull().any(),
                "count_all_match": (col.re_search(cls.COUNT_REGEX) | col.isnull()).all(),
            }
        return {"count_has_non_null": ibis.literal(False)}

    @classmethod
    def evaluate(cls, results: dict[str, Any]) -> bool:
        if "count_all_positive" in results:
            return bool(results.get("count_has_non_null", False) and results["count_all_positive"])
        return bool(
            results.get("count_has_non_null", False) and results.get("count_all_match", False)
        )


class Integer(LogicalType):
    INTEGER_REGEX = r"^-?\d+$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> dict[str, ir.Scalar]:
        if isinstance(col.type(), dt.Integer):
            return {"int_is_native": ibis.literal(True)}
        if isinstance(col.type(), dt.String):
            return {
                "int_has_non_null": col.notnull().any(),
                "int_all_match": (col.re_search(cls.INTEGER_REGEX) | col.isnull()).all(),
            }
        return {"int_is_native": ibis.literal(False)}

    @classmethod
    def evaluate(cls, results: dict[str, Any]) -> bool:
        if results.get("int_is_native", False):
            return True
        return bool(results.get("int_has_non_null", False) and results.get("int_all_match", False))


class Complex(LogicalType):
    COMPLEX_REGEX = r"^-?\d+(?:\.\d+)?(?:[+-]\d+(?:\.\d+)?)?j$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> dict[str, ir.Scalar]:
        if not isinstance(col.type(), dt.String):
            return {"complex_has_non_null": ibis.literal(False)}
        return {
            "complex_has_non_null": col.notnull().any(),
            "complex_all_match": (col.re_search(cls.COMPLEX_REGEX) | col.isnull()).all(),
        }

    @classmethod
    def evaluate(cls, results: dict[str, Any]) -> bool:
        return bool(
            results.get("complex_has_non_null", False) and results.get("complex_all_match", False)
        )


class Age(LogicalType):
    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> dict[str, ir.Scalar]:
        if not isinstance(col.type(), dt.Integer):
            return {"age_is_integer": ibis.literal(False)}
        return {
            "age_is_integer": ibis.literal(True),
            "age_has_non_null": col.notnull().any(),
            "age_in_range": (col.between(0, 120) | col.isnull()).all(),
            "age_percent_above_14": (col > 14).mean(),
        }

    @classmethod
    def evaluate(cls, results: dict[str, Any]) -> bool:
        return bool(
            results.get("age_is_integer", False)
            and results.get("age_has_non_null", False)
            and results.get("age_in_range", False)
            and results.get("age_percent_above_14", 0) > 0.5
        )


class Decimal(LogicalType):
    DECIMAL_REGEX = r"^-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> dict[str, ir.Scalar]:
        if isinstance(col.type(), (dt.Decimal, dt.Floating)):
            return {"dec_is_native": ibis.literal(True)}
        if isinstance(col.type(), dt.String):
            return {
                "dec_has_non_null": col.notnull().any(),
                "dec_all_match": (col.re_search(cls.DECIMAL_REGEX) | col.isnull()).all(),
            }
        return {"dec_is_native": ibis.literal(False)}

    @classmethod
    def evaluate(cls, results: dict[str, Any]) -> bool:
        if results.get("dec_is_native", False):
            return True
        return bool(results.get("dec_has_non_null", False) and results.get("dec_all_match", False))


class Ordinal(LogicalType):
    ORDINAL_GROUPS = [
        {"low", "medium", "high"},
        {"small", "medium", "large"},
        {"first", "second", "third"},
        {"very low", "low", "medium", "high", "very high"},
        {"jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"},
        {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"},
        {"mon", "tue", "wed", "thu", "fri", "sat", "sun"},
    ]

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> dict[str, ir.Scalar]:
        if not isinstance(col.type(), dt.String):
            return {"ord_has_non_null": ibis.literal(False)}
        checks = {
            f"group_{index}": (col.lower().isin(group) | col.isnull()).all()
            for index, group in enumerate(cls.ORDINAL_GROUPS)
        }
        return {"ord_has_non_null": col.notnull().any(), **checks}

    @classmethod
    def evaluate(cls, results: dict[str, Any]) -> bool:
        if not results.get("ord_has_non_null", False):
            return False
        return any(value for key, value in results.items() if key.startswith("group_"))


class Categorical(LogicalType):
    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> dict[str, ir.Scalar]:
        if not isinstance(col.type(), (dt.String, dt.Integer)):
            return {"cat_n_unique": ibis.literal(0)}
        return {
            "cat_n_unique": col.nunique(),
            "cat_total": col.count() + col.isnull().sum(),
        }

    @classmethod
    def evaluate(cls, results: dict[str, Any]) -> bool:
        n_unique = results.get("cat_n_unique", 0)
        total = results.get("cat_total", 0)
        if total == 0:
            return False
        is_low_cardinality = n_unique < 20 or (n_unique / total) < 0.05
        if total < 50:
            is_not_unique = n_unique < total * 0.5
        else:
            is_not_unique = n_unique < total * 0.8
        return bool(is_low_cardinality and is_not_unique)


Email = LogicalTypeRule(
    name="Email",
    display_label="Email",
    regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
)
URL = LogicalTypeRule(
    name="URL",
    display_label="URL",
    regex=r"^(?:http|ftp)s?://(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,6}\.?|[a-zA-Z0-9-]{2,}\.?)|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/?|[/?]\S+)$",
)
IPAddress = LogicalTypeRule(
    name="IPAddress",
    display_label="IP Address",
    regex=r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|^(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}$|^::1$|^([a-fA-F0-9]{1,4}:){1,7}:|^:([a-fA-F0-9]{1,4}:){1,7}|^[a-fA-F0-9]{1,4}(:[a-fA-F0-9]{1,4}){0,6}::([a-fA-F0-9]{1,4}(:[a-fA-F0-9]{1,4}){0,6})?$",
)
PhoneNumber = LogicalTypeRule(
    name="PhoneNumber",
    display_label="Phone Number",
    regex=r"^(?:\+?[0-9]{1,3}[-.\s]?)?\(?[0-9]{1,4}\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}(?:[-.\s]?[0-9]{1,9})?$",
)
CreditCard = LogicalTypeRule(
    name="CreditCard",
    display_label="Credit Card",
    regex=r"^(?:\d{4}[-\s]?){3}\d{4}$|^\d{15,16}$",
)
SSN = LogicalTypeRule(
    name="SSN",
    display_label="SSN",
    regex=r"^[1-8]\d{2}[-\s]?\d{2}[-\s]?\d{4}$",
)
JSON = LogicalTypeRule(
    name="JSON",
    display_label="JSON",
    regex=r"^\s*(?:\{.*\}|\[.*\])\s*$",
)
CUID = LogicalTypeRule(
    name="CUID",
    display_label="CUID",
    regex=r"^c[a-z0-9]{24}$",
)
NanoID = LogicalTypeRule(
    name="NanoID",
    display_label="NanoID",
    regex=r"^[a-zA-Z0-9_-]{21}$",
)
MACAddress = LogicalTypeRule(
    name="MACAddress",
    display_label="MAC Address",
    regex=r"^(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})$",
)
CountryCode = LogicalTypeRule(
    name="CountryCode",
    display_label="Country Code",
    regex=r"^[A-Z]{2,3}$",
)
FilePath = LogicalTypeRule(
    name="FilePath",
    display_label="File Path",
    regex=r"^(?:\/|[a-zA-Z]:\\|s3:\/\/|gs:\/\/).+$",
)
Geometry = LogicalTypeRule(
    name="Geometry",
    display_label="Geometry",
    regex=r"(?i)^(?:POINT|LINESTRING|POLYGON|MULTIPOINT|MULTILINESTRING|MULTIPOLYGON)\s?\(.+\)$",
)
Currency = LogicalTypeRule(
    name="Currency",
    display_label="Currency",
    regex=r"^[$€£¥]\s?-?\d+(?:,\d{3})*(?:\.\d{2})?$",
)
IBAN = LogicalTypeRule(
    name="IBAN",
    display_label="IBAN",
    regex=r"^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$",
)
SWIFT = LogicalTypeRule(
    name="SWIFT",
    display_label="SWIFT/BIC",
    regex=r"^[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?$",
)
TaxID = LogicalTypeRule(
    name="TaxID",
    display_label="Tax ID (EIN)",
    regex=r"^\d{2}-\d{7}$",
)
ISIN = LogicalTypeRule(
    name="ISIN",
    display_label="ISIN",
    regex=r"^[A-Z]{2}[A-Z0-9]{9}\d$",
)
StockTicker = LogicalTypeRule(
    name="StockTicker",
    display_label="Stock Ticker",
    regex=r"^[A-Z]{1,5}$",
)
Gender = LogicalTypeRule(
    name="Gender",
    display_label="Gender",
    allowed_values=frozenset(
        {"male", "female", "m", "f", "nb", "non-binary", "nonbinary", "other", "unknown", "u"}
    ),
)
LanguageCode = LogicalTypeRule(
    name="LanguageCode",
    display_label="Language Code",
    regex=r"^[a-z]{2}$",
)
Passport = LogicalTypeRule(
    name="Passport",
    display_label="Passport",
    regex=r"^[A-Z0-9]{6,9}$",
)
USState = LogicalTypeRule(
    name="USState",
    display_label="US State",
    allowed_values=frozenset(
        {
            "AL",
            "AK",
            "AZ",
            "AR",
            "CA",
            "CO",
            "CT",
            "DE",
            "FL",
            "GA",
            "HI",
            "ID",
            "IL",
            "IN",
            "IA",
            "KS",
            "KY",
            "LA",
            "ME",
            "MD",
            "MA",
            "MI",
            "MN",
            "MS",
            "MO",
            "MT",
            "NE",
            "NV",
            "NH",
            "NJ",
            "NM",
            "NY",
            "NC",
            "ND",
            "OH",
            "OK",
            "OR",
            "PA",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VT",
            "VA",
            "WA",
            "WV",
            "WI",
            "WY",
            "DC",
        }
    ),
)
USTerritory = LogicalTypeRule(
    name="USTerritory",
    display_label="US Territory",
    allowed_values=frozenset({"PR", "VI", "GU", "AS", "MP"}),
)
USMilitaryMail = LogicalTypeRule(
    name="USMilitaryMail",
    display_label="US Military Mail",
    allowed_values=frozenset({"AA", "AE", "AP"}),
)
USZipCode = LogicalTypeRule(
    name="USZipCode",
    display_label="US Zip Code",
    regex=r"^\d{5}(?:-\d{4})?$",
)
UUID = LogicalTypeRule(
    name="UUID",
    display_label="UUID",
    regex=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
)


LogicalTypeDefinition = type[LogicalType] | LogicalTypeRule


class IbisLogicalTypeSystem:
    def __init__(
        self,
        minimal: bool = False,
        n_unique_threshold: int = 100_000,
        inference_sample_size: int | None = 10_000,
        row_count: int | None = None,
    ):
        self.types: list[LogicalTypeDefinition] = [
            CreditCard,
            SSN,
            Email,
            IBAN,
            SWIFT,
            TaxID,
            ISIN,
            JSON,
            URL,
            IPAddress,
            DateTime,
            USZipCode,
            PhoneNumber,
            MACAddress,
            USState,
            USTerritory,
            USMilitaryMail,
            CountryCode,
            FilePath,
            Complex,
            Geometry,
            Currency,
            Boolean,
            Age,
            Ordinal,
            Count,
            UUID,
            CUID,
            NanoID,
            Passport,
            LanguageCode,
            Gender,
            Integer,
            Decimal,
            Categorical,
            StockTicker,
            String,
        ]
        self.minimal = minimal
        self.n_unique_threshold = n_unique_threshold
        self.inference_sample_size = inference_sample_size
        self.row_count = row_count

    def get_fallback_type(self, dtype: dt.DataType) -> LogicalTypeDefinition:
        """Map physical types to logical types without data-driven checks."""
        if isinstance(dtype, dt.Integer):
            return Integer
        if isinstance(dtype, (dt.Decimal, dt.Floating)):
            return Decimal
        if isinstance(dtype, (dt.Date, dt.Timestamp)):
            return DateTime
        if isinstance(dtype, dt.Boolean):
            return Boolean
        return String

    def infer_type(self, table: ibis.Table, column: str) -> LogicalTypeDefinition:
        results = self.infer_all_types(table, [column])
        return results.get(column, String)

    def infer_all_types(
        self, table: ibis.Table, columns: list[str] | Any | None = None
    ) -> dict[str, LogicalTypeDefinition]:
        """Infer logical types for all specified columns in one batch."""
        cols = list(table.columns) if columns is None else list(columns)

        if self.minimal:
            schema = table.schema()
            return {col: self.get_fallback_type(schema[col]) for col in cols}

        if self.inference_sample_size is not None:
            inference_table = table.head(self.inference_sample_size)
        else:
            inference_table = table

        check_records: list[tuple[str, LogicalTypeDefinition, str, ir.Scalar]] = []
        for col_name in cols:
            col = inference_table[col_name]
            for logical_type in self.types:
                if (
                    logical_type == Categorical
                    and self.row_count
                    and self.row_count > self.n_unique_threshold
                ):
                    continue
                for key, value in logical_type.get_check_exprs(col).items():
                    check_records.append((col_name, logical_type, key, value))

        chunk_size = 5
        results: dict[str, dict[LogicalTypeDefinition, dict[str, Any]]] = {}
        schema = table.schema()
        alias_counter = 0

        for index in range(0, len(cols), chunk_size):
            chunk_cols = cols[index : index + chunk_size]
            chunk_records = [record for record in check_records if record[0] in chunk_cols]
            alias_map: dict[str, tuple[str, LogicalTypeDefinition, str]] = {}
            chunk_exprs = []
            for col_name, logical_type, check_name, value in chunk_records:
                alias = f"c{alias_counter}"
                alias_counter += 1
                alias_map[alias] = (col_name, logical_type, check_name)
                chunk_exprs.append(value.name(alias))
            if not chunk_exprs:
                continue
            try:
                batch_results = inference_table.aggregate(chunk_exprs).to_pyarrow().to_pydict()
                for alias, value in batch_results.items():
                    col_name, logical_type, check_name = alias_map[alias]
                    results.setdefault(col_name, {}).setdefault(logical_type, {})[check_name] = (
                        value[0]
                    )
            except Exception as error:
                logging.warning("Logical inference failed for batch %s: %s", chunk_cols, error)

        inferred = {}
        for col_name in cols:
            col_inferred = self.get_fallback_type(schema[col_name])
            col_results = results.get(col_name, {})
            if col_results:
                for logical_type in self.types:
                    type_results = col_results.get(logical_type, {})
                    if type_results and logical_type.evaluate(type_results):
                        col_inferred = logical_type
                        break
            inferred[col_name] = col_inferred

        return inferred
