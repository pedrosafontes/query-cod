import re

from ra_sql_visualisation.types import DataType
from sqlglot import Expression
from sqlglot.expressions import Avg, Count, Literal, Max, Min, Subquery, Sum

from .errors import (
    ScalarSubqueryError,
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


def assert_integer_literal(literal: Literal) -> None:
    if not literal.is_int:
        raise TypeMismatchError(literal, DataType.INTEGER, infer_literal_type(literal))


def assert_scalar_subquery(subquery: Subquery) -> None:
    select = subquery.this
    expressions = select.expressions

    if len(expressions) != 1:
        raise ScalarSubqueryError(subquery)

    [scalar] = expressions
    group = select.args.get('group')

    if not is_aggregate(scalar) or group:
        raise ScalarSubqueryError(subquery)


def is_aggregate(expr: Expression) -> bool:
    return isinstance(expr, Count | Sum | Avg | Min | Max)


def infer_literal_type(node: Literal) -> DataType:
    value = node.this

    if node.is_int:
        return DataType.INTEGER
    elif node.is_number:
        return DataType.FLOAT
    elif node.is_string:
        value = str(value).lower()
        if _is_date_format(value):
            return DataType.DATE
        elif _is_time_format(value):
            return DataType.TIME
        elif _is_timestamp_format(value):
            return DataType.TIMESTAMP
        else:
            return DataType.VARCHAR
    else:
        raise ValueError(f'Unsupported literal: {node}')


def _is_date_format(s: str) -> bool:
    return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', s))


def _is_time_format(s: str) -> bool:
    return bool(re.fullmatch(r'\d{2}:\d{2}(:\d{2})?', s))


def _is_timestamp_format(s: str) -> bool:
    return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?', s))
