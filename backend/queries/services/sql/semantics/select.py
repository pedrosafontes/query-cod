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


def validate_select(select: SelectScope) -> None:
    validate_from(select)
    validate_joins(select)
    validate_where(select)
    validate_group_by(select)
    validate_having(select)
    validate_projection(select)
    validate_order_by(select)


def validate_from(select: SelectScope) -> None:
    if select.from_:
        TableValidator(select).validate(select.from_.this)


def validate_joins(select: SelectScope) -> None:
    join_validator = JoinValidator(select)
    for join in select.joins:
        join_validator.validate(join)


def validate_where(select: SelectScope) -> None:
    if select.where:
        ExpressionValidator(select).validate_boolean(
            select.where.this, ValidationContext(in_where=True)
        )


def validate_group_by(select: SelectScope) -> None:
    if select.group:
        for expr in select.group.expressions:
            ExpressionValidator(select).validate(expr)


def validate_having(select: SelectScope) -> None:
    if select.having:
        ExpressionValidator(select).validate_boolean(
            select.having.this, ValidationContext(in_having=True)
        )


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


def validate_order_by(select: SelectScope) -> None:
    if select.order_by:
        order_by_validator = OrderByValidator(select)
        for expr in select.order_by.expressions:
            order_by_validator.validate(expr)
