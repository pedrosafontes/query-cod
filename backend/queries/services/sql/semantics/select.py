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
    def validate(select: SelectScope) -> None:
        SelectValidator.validate_from(select)
        SelectValidator.validate_joins(select)
        SelectValidator.validate_where(select)
        SelectValidator.validate_group_by(select)
        SelectValidator.validate_having(select)
        SelectValidator.validate_projection(select)
        SelectValidator.validate_order_by(select)

    @staticmethod
    def validate_from(select: SelectScope) -> None:
        if select.from_:
            TableValidator(select).validate(select.from_.this)

    @staticmethod
    def validate_joins(select: SelectScope) -> None:
        join_validator = JoinValidator(select)
        for join in select.joins:
            join_validator.validate(join)

    @staticmethod
    def validate_where(select: SelectScope) -> None:
        if select.where:
            ExpressionValidator(select).validate_boolean(
                select.where.this, ValidationContext(in_where=True)
            )

    @staticmethod
    def validate_group_by(select: SelectScope) -> None:
        if select.group:
            for expr in select.group.expressions:
                ExpressionValidator(select).validate(expr)

    @staticmethod
    def validate_having(select: SelectScope) -> None:
        if select.having:
            ExpressionValidator(select).validate_boolean(
                select.having.this, ValidationContext(in_having=True)
            )

    @staticmethod
    def validate_projection(select: SelectScope) -> None:
        table_aliases: dict[str | None, set[str]] = defaultdict(set)
        for expr in cast(list[Expression], select.query.expressions):
            if expr.is_star:
                StarValidator(select).validate(expr)
                continue

            alias = expr.alias_or_name
            table = expr.args.get('table')
            if alias and alias in table_aliases[table]:
                raise DuplicateAliasError(expr)
            table_aliases[table].add(alias)

            if expr.unalias() not in select.group_by:  # type: ignore[no-untyped-call]
                ExpressionValidator(select).validate(expr, ValidationContext(in_select=True))

    @staticmethod
    def validate_order_by(select: SelectScope) -> None:
        if select.order_by:
            order_by_validator = OrderByValidator(select)
            for expr in select.order_by.expressions:
                order_by_validator.validate(expr)
