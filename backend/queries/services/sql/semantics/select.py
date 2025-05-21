from collections import defaultdict
from typing import cast

from sqlglot.expressions import (
    Expression,
)

from ..scope import SelectScope
from .context import ValidationContext
from .errors import DuplicateAliasError
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
        if scope.from_:
            TableValidator(scope).validate(scope.from_.this)

    @staticmethod
    def validate_joins(scope: SelectScope) -> None:
        join_validator = JoinValidator(scope)
        for join in scope.select.args.get('joins', []):
            join_validator.validate(join)

    @staticmethod
    def validate_where(scope: SelectScope) -> None:
        if scope.where:
            ExpressionValidator(scope).validate_boolean(
                scope.where.this, ValidationContext(in_where=True)
            )

    @staticmethod
    def validate_group_by(scope: SelectScope) -> None:
        if scope.group:
            for expr in scope.group.expressions:
                ExpressionValidator(scope).validate(expr)

    @staticmethod
    def validate_having(scope: SelectScope) -> None:
        if scope.having:
            ExpressionValidator(scope).validate_boolean(
                scope.having.this, ValidationContext(in_having=True)
            )

    @staticmethod
    def validate_projection(scope: SelectScope) -> None:
        table_aliases: dict[str | None, set[str]] = defaultdict(set)
        for expr in cast(list[Expression], scope.select.expressions):
            if expr.is_star:
                StarValidator(scope).validate(expr)
                continue

            alias = expr.alias_or_name
            table = expr.args.get('table')
            if alias and alias in table_aliases[table]:
                raise DuplicateAliasError(expr)
            table_aliases[table].add(alias)

            if expr.unalias() not in scope.group_by:  # type: ignore[no-untyped-call]
                ExpressionValidator(scope).validate(expr, ValidationContext(in_select=True))

    @staticmethod
    def validate_order_by(scope: SelectScope) -> None:
        if scope.order_by:
            order_by_validator = OrderByValidator(scope)
            for expr in scope.order_by.expressions:
                order_by_validator.validate(expr)
