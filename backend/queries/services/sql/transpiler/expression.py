import queries.services.ra.ast as ra
from queries.services.sql.scope.query import SelectScope
from queries.services.types import sql_to_ra_bin_bool_ops, sql_to_ra_comparisons
from sqlglot import Expression
from sqlglot import expressions as sql

from ..types import (
    BooleanExpression,
    Comparison,
)


class ExpressionTranspiler:
    def __init__(self, scope: SelectScope) -> None:
        self.scope = scope

    def transpile(self, expr: Expression) -> ra.BooleanExpression:
        match expr:
            case sql.Column():
                return self.transpile_column(expr)

            case sql.Paren():
                return self.transpile(expr.this)

            case comp if isinstance(comp, Comparison):
                return self._transpile_comparison(comp)

            # Expressions
            case expr if isinstance(expr, BooleanExpression):
                return self._transpile_boolean_expr(expr)

            case _:
                raise NotImplementedError(f'Expression {type(expr)} not supported')

    def transpile_column(self, expr: sql.Column) -> ra.Attribute:
        return ra.Attribute(name=str(expr.this), relation=expr.table or None)

    def _transpile_value(self, value: Expression) -> ra.ComparisonValue:
        match value:
            case sql.Column():
                return self.transpile_column(value)
            case sql.Literal():
                if value.is_string:
                    return str(value.this)
                elif value.is_number:
                    return float(value.this)
                else:
                    raise NotImplementedError(f'Literal type {type(value)} not supported')
            case sql.Boolean():
                return bool(value.this)
            case _:
                raise NotImplementedError(f'Value {type(value)} not supported')

    def _transpile_comparison(self, comp: Comparison) -> ra.Comparison:
        ra_comparison = sql_to_ra_comparisons[type(comp)]
        return ra_comparison(self._transpile_value(comp.left), self._transpile_value(comp.right))

    def _transpile_boolean_expr(self, expr: BooleanExpression) -> ra.BooleanExpression:
        match expr:
            case sql.And() | sql.Or():
                ra_operator = sql_to_ra_bin_bool_ops[type(expr)]
                return ra_operator(
                    self.transpile(expr.left),
                    self.transpile(expr.right),
                )

            case sql.Not():
                return ra.Not(
                    expression=self.transpile(expr.this),
                )
