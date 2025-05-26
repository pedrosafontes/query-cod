from query_cod.types import DataType
from sqlglot import Expression

from ..types import AggregateFunction
from .errors import (
    TypeMismatchError,
)


def assert_comparable(lhs: DataType, rhs: DataType, source: Expression) -> None:
    if not lhs.is_comparable_with(rhs):
        raise TypeMismatchError(source, lhs, rhs)


def assert_boolean(t: DataType, source: Expression) -> None:
    if t is not DataType.BOOLEAN:
        raise TypeMismatchError(source, DataType.BOOLEAN, t)


def assert_numeric(t: DataType, source: Expression) -> None:
    if not t.is_numeric():
        raise TypeMismatchError(source, DataType.NUMERIC, t)


def assert_string(t: DataType, source: Expression) -> None:
    if not t.is_string():
        raise TypeMismatchError(source, DataType.VARCHAR, t)


def is_aggregate(expr: Expression) -> bool:
    return isinstance(expr, AggregateFunction)
