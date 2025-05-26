from collections.abc import Iterator

from queries.services.ra.ast import (
    Attribute,
    RAQuery,
)
from queries.services.sql.scope.query import SelectScope
from queries.services.sql.types import AggregateFunction, aggregate_functions
from sqlglot.expressions import Alias, Column, Expression, Star, column

from .expression import ExpressionTranspiler
from .group_by import GroupByTranspiler
from .join import JoinTranspiler
from .table import TableTranspiler
from .where import WhereTranspiler


def transpile_select(scope: SelectScope) -> RAQuery:
    from_query = _transpile_from(scope)
    join_query = _transpile_joins(scope, from_query)
    where_query, parameters = _transpile_where(scope, join_query)
    group_by_query, aggregates = _transpile_group_by(scope, where_query, parameters)
    having_query = _transpile_having(scope, group_by_query, aggregates)
    projection_query = _transpile_projection(scope, having_query, aggregates, parameters)
    return projection_query


def _transpile_from(scope: SelectScope) -> RAQuery:
    if not scope.from_:
        raise ValueError('FROM clause is required in SELECT query')

    return TableTranspiler(scope).transpile(scope.from_.this)


def _transpile_joins(scope: SelectScope, subquery: RAQuery) -> RAQuery:
    left = subquery
    for join in scope.joins:
        left = JoinTranspiler(scope).transpile(join, left)
    return left


def _transpile_where(scope: SelectScope, subquery: RAQuery) -> tuple[RAQuery, list[Attribute]]:
    if scope.where:
        where_transpiler = WhereTranspiler(scope)
        return where_transpiler.transpile(subquery), where_transpiler.parameters
    else:
        return subquery, []


def _transpile_group_by(
    scope: SelectScope, subquery: RAQuery, parameters: list[Attribute]
) -> tuple[RAQuery, dict[AggregateFunction, str]]:
    transpiler = GroupByTranspiler(scope)
    return transpiler.transpile(subquery, parameters), transpiler.aggregates


def _transpile_having(
    scope: SelectScope, subquery: RAQuery, aggregates: dict[AggregateFunction, str]
) -> RAQuery:
    if scope.having:
        condition: Expression = scope.having.this
        aggregate_exprs: Iterator[AggregateFunction] = condition.find_all(*aggregate_functions)
        for aggregate in aggregate_exprs:
            aggregate.replace(column(aggregates[aggregate]))
        return subquery.select(ExpressionTranspiler(scope).transpile(condition))
    return subquery


def _transpile_projection(
    scope: SelectScope,
    subquery: RAQuery,
    aggregates: dict[AggregateFunction, str],
    parameters: list[Attribute],
) -> RAQuery:
    attributes: list[Attribute] = parameters
    for expr in scope.select.expressions:
        match expr:
            case Column():
                attributes.append(ExpressionTranspiler(scope).transpile_column(expr))
            case Star():
                return subquery
            case Alias():
                inner = expr.this
                if isinstance(inner, AggregateFunction):
                    attributes.append(Attribute(name=aggregates[inner]))
            case _:
                raise NotImplementedError(f'Unsupported projection expression: {type(expr)}')
    return subquery.project(attributes)
