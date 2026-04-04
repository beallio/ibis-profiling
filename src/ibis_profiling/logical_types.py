import ibis
import ibis.expr.datatypes as dt
import ibis.expr.types as ir
from abc import ABC, abstractmethod
from typing import Type, Dict, Any, List


class LogicalType(ABC):
    @classmethod
    @abstractmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        """Returns a dict of Ibis expressions to be aggregated."""
        ...

    @classmethod
    @abstractmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        """Evaluates results from the aggregate call to decide if it's a match."""
        ...

    @classmethod
    def matches(cls, table: ibis.Table, column: str) -> bool:
        """Helper for single-type checks."""
        exprs = {f"{cls.__name__}_{k}": v for k, v in cls.get_check_exprs(table[column]).items()}
        res = table.aggregate([v.name(k) for k, v in exprs.items()]).to_pandas().iloc[0].to_dict()
        type_results = {
            k[len(cls.__name__) + 1 :]: v
            for k, v in res.items()
            if k.startswith(cls.__name__ + "_")
        }
        return cls.evaluate(type_results)


class String(LogicalType):
    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        return {"is_string": ibis.literal(isinstance(col.type(), dt.String))}

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        return bool(results.get("is_string", False))


class Email(LogicalType):
    EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        if not isinstance(col.type(), dt.String):
            return {"email_has_non_null": ibis.literal(False)}

        return {
            "email_has_non_null": col.notnull().any(),
            "email_all_match": (col.re_search(cls.EMAIL_REGEX) | col.isnull()).all(),
        }

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        return bool(
            results.get("email_has_non_null", False) and results.get("email_all_match", False)
        )


class URL(LogicalType):
    URL_REGEX = r"^(?:http|ftp)s?://(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,6}\.?|[a-zA-Z0-9-]{2,}\.?)|localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/?|[/?]\S+)$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        if not isinstance(col.type(), dt.String):
            return {"url_has_non_null": ibis.literal(False)}

        return {
            "url_has_non_null": col.notnull().any(),
            "url_all_match": (col.re_search(cls.URL_REGEX) | col.isnull()).all(),
        }

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        return bool(results.get("url_has_non_null", False) and results.get("url_all_match", False))


class IPAddress(LogicalType):
    # Regex for IPv4 and simplified IPv6
    IP_REGEX = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|^(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}$|^::1$|^([a-fA-F0-9]{1,4}:){1,7}:|^:([a-fA-F0-9]{1,4}:){1,7}|^[a-fA-F0-9]{1,4}(:[a-fA-F0-9]{1,4}){0,6}::([a-fA-F0-9]{1,4}(:[a-fA-F0-9]{1,4}){0,6})?$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        if not isinstance(col.type(), dt.String):
            return {"ip_has_non_null": ibis.literal(False)}

        return {
            "ip_has_non_null": col.notnull().any(),
            "ip_all_match": (col.re_search(cls.IP_REGEX) | col.isnull()).all(),
        }

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        return bool(results.get("ip_has_non_null", False) and results.get("ip_all_match", False))


class DateTime(LogicalType):
    # Broad ISO8601 regex
    ISO8601_REGEX = (
        r"^\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?$"
    )

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        if isinstance(col.type(), (dt.Date, dt.Timestamp)):
            return {"dt_is_native": ibis.literal(True)}

        if isinstance(col.type(), dt.String):
            return {
                "dt_has_non_null": col.notnull().any(),
                "dt_all_match": (col.re_search(cls.ISO8601_REGEX) | col.isnull()).all(),
            }

        return {"dt_is_native": ibis.literal(False)}

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        if results.get("dt_is_native", False):
            return True
        return bool(results.get("dt_has_non_null", False) and results.get("dt_all_match", False))


class PhoneNumber(LogicalType):
    # Basic phone regex covering E.164 and common US/International formats
    PHONE_REGEX = r"^(?:\+?[0-9]{1,3}[-.\s]?)?\(?[0-9]{1,4}\)?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}(?:[-.\s]?[0-9]{1,9})?$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        if not isinstance(col.type(), dt.String):
            return {"phone_has_non_null": ibis.literal(False)}

        return {
            "phone_has_non_null": col.notnull().any(),
            "phone_all_match": (col.re_search(cls.PHONE_REGEX) | col.isnull()).all(),
        }

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        return bool(
            results.get("phone_has_non_null", False) and results.get("phone_all_match", False)
        )


class Boolean(LogicalType):
    BOOLEAN_STRINGS = {"true", "false", "t", "f", "yes", "no", "y", "n", "1", "0"}

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        if isinstance(col.type(), dt.Boolean):
            return {"bool_is_native": ibis.literal(True)}

        if isinstance(col.type(), dt.String):
            # Check if all non-null values are in the boolean string set
            return {
                "bool_has_non_null": col.notnull().any(),
                "bool_all_match": (col.lower().isin(cls.BOOLEAN_STRINGS) | col.isnull()).all(),
            }

        if isinstance(col.type(), dt.Integer):
            # Check if all non-null values are 0 or 1
            return {
                "bool_has_non_null": col.notnull().any(),
                "bool_all_match": (col.isin([0, 1]) | col.isnull()).all(),
            }

        return {"bool_is_native": ibis.literal(False)}

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        if results.get("bool_is_native", False):
            return True
        return bool(
            results.get("bool_has_non_null", False) and results.get("bool_all_match", False)
        )


class Count(LogicalType):
    COUNT_REGEX = r"^\d+$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
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
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        if "count_all_positive" in results:
            return bool(results.get("count_has_non_null", False) and results["count_all_positive"])
        return bool(
            results.get("count_has_non_null", False) and results.get("count_all_match", False)
        )


class Integer(LogicalType):
    INTEGER_REGEX = r"^-?\d+$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        if isinstance(col.type(), dt.Integer):
            return {"int_is_native": ibis.literal(True)}

        if isinstance(col.type(), dt.String):
            return {
                "int_has_non_null": col.notnull().any(),
                "int_all_match": (col.re_search(cls.INTEGER_REGEX) | col.isnull()).all(),
            }

        return {"int_is_native": ibis.literal(False)}

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        if results.get("int_is_native", False):
            return True
        return bool(results.get("int_has_non_null", False) and results.get("int_all_match", False))


class CreditCard(LogicalType):
    # Simplified standard formats: Visa, Mastercard, Amex, Discover
    # Handles spaces or dashes
    CARD_REGEX = r"^(?:\d{4}[-\s]?){3}\d{4}$|^\d{15,16}$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        if not isinstance(col.type(), dt.String):
            return {"cc_has_non_null": ibis.literal(False)}

        return {
            "cc_has_non_null": col.notnull().any(),
            "cc_all_match": (col.re_search(cls.CARD_REGEX) | col.isnull()).all(),
        }

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        return bool(results.get("cc_has_non_null", False) and results.get("cc_all_match", False))


class SSN(LogicalType):
    # US Social Security Numbers: XXX-XX-XXXX or XXXXXXXXX
    SSN_REGEX = r"^\d{3}[-\s]?\d{2}[-\s]?\d{4}$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        if not isinstance(col.type(), dt.String):
            return {"ssn_has_non_null": ibis.literal(False)}

        return {
            "ssn_has_non_null": col.notnull().any(),
            "ssn_all_match": (col.re_search(cls.SSN_REGEX) | col.isnull()).all(),
        }

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        return bool(results.get("ssn_has_non_null", False) and results.get("ssn_all_match", False))


class Decimal(LogicalType):
    # Regex for decimal numbers (including scientific notation)
    DECIMAL_REGEX = r"^-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        if isinstance(col.type(), (dt.Decimal, dt.Floating)):
            return {"dec_is_native": ibis.literal(True)}

        if isinstance(col.type(), dt.String):
            return {
                "dec_has_non_null": col.notnull().any(),
                "dec_all_match": (col.re_search(cls.DECIMAL_REGEX) | col.isnull()).all(),
            }

        return {"dec_is_native": ibis.literal(False)}

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
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
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        if not isinstance(col.type(), dt.String):
            return {"ord_has_non_null": ibis.literal(False)}

        # Optimization: only check unique values if count is low
        # But we need to do it in aggregate.
        # We'll check if ALL non-null values belong to ONE of the groups.
        checks = {}
        for i, group in enumerate(cls.ORDINAL_GROUPS):
            checks[f"group_{i}"] = (col.lower().isin(group) | col.isnull()).all()

        return {"ord_has_non_null": col.notnull().any(), **checks}

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        if not results.get("ord_has_non_null", False):
            return False
        return any(v for k, v in results.items() if k.startswith("group_"))


class UUID(LogicalType):
    UUID_REGEX = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"

    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        if not isinstance(col.type(), dt.String):
            return {"uuid_has_non_null": ibis.literal(False)}

        return {
            "uuid_has_non_null": col.notnull().any(),
            "uuid_all_match": (col.re_search(cls.UUID_REGEX) | col.isnull()).all(),
        }

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        return bool(
            results.get("uuid_has_non_null", False) and results.get("uuid_all_match", False)
        )


class Categorical(LogicalType):
    @classmethod
    def get_check_exprs(cls, col: ibis.Column) -> Dict[str, ir.Scalar]:
        if not isinstance(col.type(), (dt.String, dt.Integer)):
            return {"cat_n_unique": ibis.literal(0)}

        return {
            "cat_n_unique": col.nunique(),
            "cat_total": col.count() + col.isnull().sum(),  # table.count() replacement
        }

    @classmethod
    def evaluate(cls, results: Dict[str, Any]) -> bool:
        n_unique = results.get("cat_n_unique", 0)
        total = results.get("cat_total", 0)
        if total == 0:
            return False

        # Improved heuristic:
        # 1. Must have low absolute cardinality (< 20) OR low relative cardinality (< 5%)
        # 2. MUST NOT be essentially unique (n_unique < total * 0.8)
        #    to avoid marking ID columns [1, 2, 3...10] as categorical.
        # 3. If total count is very low, we require even lower cardinality.

        is_low_cardinality = n_unique < 20 or (n_unique / total) < 0.05

        # Guard against small datasets where 1..10 is both low cardinality and high relative cardinality
        if total < 50:
            is_not_unique = n_unique < total * 0.5
        else:
            is_not_unique = n_unique < total * 0.8

        return bool(is_low_cardinality and is_not_unique)


class IbisLogicalTypeSystem:
    def __init__(
        self,
        minimal: bool = False,
        n_unique_threshold: int = 100_000,
        row_count: int | None = None,
    ):
        # Ordered by specificity
        self.types: List[Type[LogicalType]] = [
            CreditCard,
            SSN,
            Email,
            URL,
            IPAddress,
            DateTime,
            PhoneNumber,
            Boolean,
            Ordinal,
            Count,
            UUID,
            Integer,
            Decimal,
            Categorical,
            String,
        ]
        self.minimal = minimal
        self.n_unique_threshold = n_unique_threshold
        self.row_count = row_count

    def get_fallback_type(self, dtype: dt.DataType) -> Type[LogicalType]:
        """Maps physical types to logical types without expensive data-driven checks."""
        if isinstance(dtype, dt.Integer):
            return Integer
        if isinstance(dtype, (dt.Decimal, dt.Floating)):
            return Decimal
        if isinstance(dtype, (dt.Date, dt.Timestamp)):
            return DateTime
        if isinstance(dtype, dt.Boolean):
            return Boolean
        return String

    def infer_type(self, table: ibis.Table, column: str) -> Type[LogicalType]:
        results = self.infer_all_types(table, [column])
        return results.get(column, String)

    def infer_all_types(
        self, table: ibis.Table, columns: List[str] | Any | None = None
    ) -> Dict[str, Type[LogicalType]]:
        """Infers logical types for all specified columns in one batch."""
        if columns is None:
            cols = list(table.columns)
        else:
            cols = list(columns)

        # Optimization: In minimal mode, only use native type mapping
        if self.minimal:
            schema = table.schema()
            return {col: self.get_fallback_type(schema[col]) for col in cols}

        # 1. Collect all expressions for all columns
        all_exprs = {}
        for col_name in cols:
            col = table[col_name]

            for ltype in self.types:
                # Skip expensive Categorical checks if row count exceeds threshold
                if ltype == Categorical:
                    if self.row_count and self.row_count > self.n_unique_threshold:
                        continue

                type_exprs = ltype.get_check_exprs(col)
                for k, v in type_exprs.items():
                    all_exprs[f"{col_name}__{ltype.__name__}_{k}"] = v

        # 2. Execute in CHUNKED batches to avoid backend expression limits
        # Typical limits are ~2000 expressions. With ~30 per column, we use 5 cols per batch.
        chunk_size = 5
        res = {}
        schema = table.schema()

        for i in range(0, len(cols), chunk_size):
            chunk_cols = cols[i : i + chunk_size]
            chunk_exprs = [
                v.name(k) for k, v in all_exprs.items() if k.split("__")[0] in chunk_cols
            ]

            if not chunk_exprs:
                continue

            try:
                batch_res = table.aggregate(chunk_exprs).to_pandas().iloc[0].to_dict()
                res.update(batch_res)
            except Exception:
                # Individual column fallback if chunk fails - results remain empty for this chunk
                pass

        # 3. Evaluate results per column
        inferred = {}
        for col_name in cols:
            # Default to physical-based fallback
            col_inferred = self.get_fallback_type(schema[col_name])

            # If results were successfully fetched for this column, try to find a more specific inferred type
            # We check if at least one key for this column exists in res
            col_results_exist = any(k.startswith(f"{col_name}__") for k in res.keys())

            if col_results_exist:
                for ltype in self.types:
                    prefix = f"{col_name}__{ltype.__name__}_"
                    # Filter results for this specific column and type
                    type_results = {
                        k[len(prefix) :]: v for k, v in res.items() if k.startswith(prefix)
                    }
                    if type_results and ltype.evaluate(type_results):
                        col_inferred = ltype
                        break
            inferred[col_name] = col_inferred

        return inferred
