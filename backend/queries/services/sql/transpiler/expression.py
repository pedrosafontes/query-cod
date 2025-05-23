from queries.services.ra.parser.ast import (
    Attribute,
    BinaryBooleanExpression,
    BinaryBooleanOperator,
    BooleanExpression,
    Comparison,
    ComparisonOperator,
    ComparisonValue,
    NotExpression,
)
from queries.services.sql.scope.query import SelectScope
from sqlglot import Expression
from sqlglot import expressions as exp

from ..types import (
    BooleanExpression as SQLBooleanExpression,
)
from ..types import (
    Comparison as SQLComparison,
)


class ExpressionTranspiler:
    def __init__(self, scope: SelectScope) -> None:
        self.scope = scope

    def transpile(self, expr: Expression) -> BooleanExpression:
        match expr:
            case exp.Column():
                return self.transpile_column(expr)

            case exp.Paren():
                return self.transpile(expr.this)

            case comp if isinstance(comp, SQLComparison):
                return self._transpile_comparison(comp)

            case expr if isinstance(expr, SQLBooleanExpression):
                return self._transpile_boolean_expr(expr)

            case _:
                raise NotImplementedError(f'Expression {type(expr)} not supported')

    def transpile_column(self, expr: exp.Column) -> Attribute:
        return Attribute(name=str(expr.this), relation=expr.table or None)

    def _transpile_value(self, value: Expression) -> ComparisonValue:
        match value:
            case exp.Column():
                return self.transpile_column(value)
            case exp.Literal():
                if value.is_string:
                    return str(value.this)
                elif value.is_number:
                    return float(value.this)
                else:
                    raise NotImplementedError(f'Literal type {type(value)} not supported')
            case exp.Boolean():
                return bool(value.this)
            case _:
                raise NotImplementedError(f'Value {type(value)} not supported')

    def _transpile_comparison(self, comp: SQLComparison) -> Comparison:
        operator: ComparisonOperator
        match comp:
            case exp.EQ():
                operator = ComparisonOperator.EQUAL
            case exp.NEQ():
                operator = ComparisonOperator.NOT_EQUAL
            case exp.GT():
                operator = ComparisonOperator.GREATER_THAN
            case exp.GTE():
                operator = ComparisonOperator.GREATER_THAN_EQUAL
            case exp.LT():
                operator = ComparisonOperator.LESS_THAN
            case exp.LTE():
                operator = ComparisonOperator.LESS_THAN_EQUAL
        return Comparison(
            operator=operator,
            left=self._transpile_value(comp.left),
            right=self._transpile_value(comp.right),
        )

    def _transpile_boolean_expr(self, expr: SQLBooleanExpression) -> BooleanExpression:
        match expr:
            case exp.And():
                return BinaryBooleanExpression(
                    operator=BinaryBooleanOperator.AND,
                    left=self.transpile(expr.left),
                    right=self.transpile(expr.right),
                )

            case exp.Or():
                return BinaryBooleanExpression(
                    operator=BinaryBooleanOperator.OR,
                    left=self.transpile(expr.left),
                    right=self.transpile(expr.right),
                )

            case exp.Not():
                return NotExpression(
                    expression=self.transpile(expr.this),
                )
