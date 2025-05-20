from typing import cast

from sqlglot.expressions import (
    Expression,
    From,
    Join,
)

from ..scope import SelectScope
from .context import ValidationContext
from .expression import ExpressionValidator
from .join import JoinValidator
from .order_by import OrderByValidator
from .star import StarValidator
from .table import TableValidator


class SelectValidator:
    def __init__(self, scope: SelectScope) -> None:
        self.scope = scope
        self.select = scope.query
        self.expr_validator = ExpressionValidator(scope)
        self.star_validator = StarValidator(scope)
        self.table_validator = TableValidator(scope)
        self.join_validator = JoinValidator(scope, self.expr_validator, self.table_validator)
        self.order_by_validator = OrderByValidator(scope, self.expr_validator)

    def validate(self) -> None:
        self.validate_from()
        self.validate_joins()
        self.validate_where()
        self.validate_group_by()
        self.validate_having()
        self.validate_projection()
        self.validate_order_by()

    def validate_from(self) -> None:
        from_clause: From | None = self.select.args.get('from')
        if from_clause:
            self.table_validator.validate(from_clause.this)

    def validate_joins(self) -> None:
        from_clause: From | None = self.select.args.get('from')
        if from_clause:
            left_cols = self.scope.get_schema(from_clause.this)
            joins: list[Join] = self.select.args.get('joins', [])
            for join in joins:
                left_cols = self.join_validator.validate(left_cols, join)

    def validate_where(self) -> None:
        where: Expression | None = self.select.args.get('where')
        if where:
            self.expr_validator._validate_boolean(where.this, ValidationContext(in_where=True))

    def validate_group_by(self) -> None:
        group = self.select.args.get('group')
        if group:
            for expr in group.expressions:
                self.expr_validator.validate_expression(expr)

    def validate_having(self) -> None:
        having: Expression | None = self.select.args.get('having')
        if having:
            self.expr_validator._validate_boolean(having.this, ValidationContext(in_having=True))

    def validate_projection(self) -> None:
        for expr in cast(list[Expression], self.select.expressions):
            inner: Expression = expr.unalias()  # type: ignore[no-untyped-call]
            if inner.is_star:
                self.star_validator.validate(inner)
            elif not self.scope.group_by.contains(inner):
                self.expr_validator.validate_expression(inner, ValidationContext(in_select=True))

    def validate_order_by(self) -> None:
        order = self.select.args.get('order')
        if order:
            self.order_by_validator.validate(order.expressions)
