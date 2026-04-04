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
        return n_unique < 20 or (n_unique / total) < 0.05


class IbisLogicalTypeSystem:
    def __init__(self):
        # Ordered by specificity
        self.types: List[Type[LogicalType]] = [
            Email,
            URL,
            IPAddress,
            PhoneNumber,
            Boolean,
            UUID,
            Categorical,
            String,
        ]

    def infer_type(self, table: ibis.Table, column: str) -> Type[LogicalType]:
        col = table[column]

        # 1. Collect all expressions
        all_exprs = {}
        for ltype in self.types:
            all_exprs.update(
                {f"{ltype.__name__}_{k}": v for k, v in ltype.get_check_exprs(col).items()}
            )

        # 2. Execute in one batch
        try:
            res = (
                table.aggregate([v.name(k) for k, v in all_exprs.items()])
                .to_pandas()
                .iloc[0]
                .to_dict()
            )
        except Exception:
            # Fallback if batching fails
            return LogicalType

        # 3. Evaluate results in order
        for ltype in self.types:
            type_results = {
                k[len(ltype.__name__) + 1 :]: v
                for k, v in res.items()
                if k.startswith(ltype.__name__ + "_")
            }
            if ltype.evaluate(type_results):
                return ltype

        return LogicalType
