from ra_sql_visualisation.types import DataType
from sqlglot import Expression
from sqlglot.expressions import (
    DataType as SQLGLotDataType,
)

from .errors import (
    TypeMismatchError,
)
from .types import AggregateFunction


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


def convert_sqlglot_type(sqlglot_type: SQLGLotDataType) -> DataType:
    type_mapping = {
        SQLGLotDataType.Type.BOOLEAN: DataType.BOOLEAN,
        SQLGLotDataType.Type.CHAR: DataType.CHAR,
        SQLGLotDataType.Type.VARCHAR: DataType.VARCHAR,
        SQLGLotDataType.Type.TEXT: DataType.VARCHAR,
        SQLGLotDataType.Type.INT: DataType.INTEGER,
        SQLGLotDataType.Type.BIGINT: DataType.INTEGER,
        SQLGLotDataType.Type.SMALLINT: DataType.SMALLINT,
        SQLGLotDataType.Type.FLOAT: DataType.FLOAT,
        SQLGLotDataType.Type.DOUBLE: DataType.DOUBLE_PRECISION,
        SQLGLotDataType.Type.DECIMAL: DataType.DECIMAL,
        SQLGLotDataType.Type.DATE: DataType.DATE,
        SQLGLotDataType.Type.TIME: DataType.TIME,
        SQLGLotDataType.Type.TIMESTAMP: DataType.TIMESTAMP,
        SQLGLotDataType.Type.BIT: DataType.BIT,
    }

    base_type = sqlglot_type.this
    if base_type not in type_mapping:
        raise ValueError(f'Unsupported SQLGlot type: {base_type}')

    return type_mapping[base_type]
