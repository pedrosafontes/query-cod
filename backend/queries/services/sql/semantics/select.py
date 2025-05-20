from typing import cast

from sqlglot.expressions import (
    Expression,
    From,
)

from ..scope import SelectScope
from .context import ValidationContext
from .expression import ExpressionValidator
from .join import JoinValidator
from .order_by import OrderByValidator
from .star import StarValidator
from .table import TableValidator


class SelectValidator:
    @staticmethod
    def validate(scope: SelectScope) -> None:
        SelectValidator.validate_from(scope)
        SelectValidator.validate_joins(scope)
        SelectValidator.validate_where(scope)
        SelectValidator.validate_group_by(scope)
        SelectValidator.validate_having(scope)
        SelectValidator.validate_projection(scope)
        SelectValidator.validate_order_by(scope)

    @staticmethod
    def validate_from(scope: SelectScope) -> None:
        from_clause: From | None = scope.query.args.get('from')
        if from_clause:
            TableValidator(scope).validate(from_clause.this)

    @staticmethod
    def validate_joins(scope: SelectScope) -> None:
        join_validator = JoinValidator(scope)
        for join in scope.query.args.get('joins', []):
            join_validator.validate(join)

    @staticmethod
    def validate_where(scope: SelectScope) -> None:
        where: Expression | None = scope.query.args.get('where')
        if where:
            ExpressionValidator(scope).validate_boolean(
                where.this, ValidationContext(in_where=True)
            )

    @staticmethod
    def validate_group_by(scope: SelectScope) -> None:
        group = scope.query.args.get('group')
        if group:
            for expr in group.expressions:
                ExpressionValidator(scope).validate(expr)

    @staticmethod
    def validate_having(scope: SelectScope) -> None:
        having: Expression | None = scope.query.args.get('having')
        if having:
            ExpressionValidator(scope).validate_boolean(
                having.this, ValidationContext(in_having=True)
            )

    @staticmethod
    def validate_projection(scope: SelectScope) -> None:
        for expr in cast(list[Expression], scope.query.expressions):
            inner: Expression = expr.unalias()  # type: ignore[no-untyped-call]
            if inner.is_star:
                StarValidator(scope).validate(inner)
            elif not scope.group_by.contains(inner):
                ExpressionValidator(scope).validate(inner, ValidationContext(in_select=True))

    @staticmethod
    def validate_order_by(scope: SelectScope) -> None:
        order = scope.query.args.get('order')
        if order:
            order_by_validator = OrderByValidator(scope)
            for expr in order.expressions:
                order_by_validator.validate(expr)
