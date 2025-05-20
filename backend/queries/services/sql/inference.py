import re
from typing import cast

from ra_sql_visualisation.types import DataType
from sqlglot.expressions import (
    Alias,
    Boolean,
    Cast,
    Column,
    Count,
    CurrentDate,
    CurrentTime,
    CurrentTimestamp,
    Expression,
    Length,
    Literal,
    Paren,
)

from .scope import SQLScope
from .types import (
    AggregateFunction,
    ArithmeticOperation,
    BooleanExpression,
    Comparison,
    Predicate,
    StringOperation,
)
from .utils import convert_sqlglot_type


class TypeInferrer:
    def __init__(self, scope: SQLScope) -> None:
        self.scope = scope

    def infer(self, node: Expression) -> DataType:
        match node:
            case Boolean():
                return DataType.BOOLEAN

            case Literal():
                return self._infer_literal_type(node)

            case CurrentDate():
                return DataType.DATE

            case CurrentTime():
                return DataType.TIME

            case CurrentTimestamp():
                return DataType.TIMESTAMP

            case Alias():
                return self.infer(node.this)

            case Column():
                return cast(DataType, self.scope.tables.resolve_column(node))

            case Alias() | Paren():
                return self.infer(node.this)

            case expr if isinstance(expr, Comparison | BooleanExpression | Predicate):
                return DataType.BOOLEAN

            case agg if isinstance(expr, AggregateFunction):
                return self._infer_aggregate_type(agg)

            case expr if isinstance(expr, ArithmeticOperation):
                lt = self.infer(expr.left)
                rt = self.infer(expr.right)
                return DataType.dominant([lt, rt])

            case expr if isinstance(expr, StringOperation):
                return self._infer_string_operation_type(expr)

            case Cast():
                return convert_sqlglot_type(node.args['to'])

            case _:
                raise NotImplementedError(f'Unsupported expression: {type(node)}')

    def _infer_literal_type(self, node: Literal) -> DataType:
        value = node.this

        if node.is_int:
            return DataType.INTEGER
        elif node.is_number:
            return DataType.FLOAT
        elif node.is_string:
            value = str(value).lower()
            if self._is_date_format(value):
                return DataType.DATE
            elif self._is_time_format(value):
                return DataType.TIME
            elif self._is_timestamp_format(value):
                return DataType.TIMESTAMP
            else:
                return DataType.VARCHAR
        else:
            raise ValueError(f'Unsupported literal: {node}')

    def _is_date_format(self, s: str) -> bool:
        return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', s))

    def _is_time_format(self, s: str) -> bool:
        return bool(re.fullmatch(r'\d{2}:\d{2}(:\d{2})?', s))

    def _is_timestamp_format(self, s: str) -> bool:
        return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?', s))

    def _infer_aggregate_type(self, agg: Expression) -> DataType:
        if isinstance(agg, Count):
            return DataType.INTEGER
        else:
            return self.infer(agg.this)

    def _infer_string_operation_type(self, expr: StringOperation) -> DataType:
        if isinstance(expr, Length):
            return DataType.INTEGER
        else:
            return DataType.VARCHAR
