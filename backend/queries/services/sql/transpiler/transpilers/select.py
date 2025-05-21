from collections.abc import Iterator

from queries.services.ra.parser.ast import (
    Attribute,
    Projection,
    RAQuery,
    Selection,
)
from queries.services.sql.scope.query import SelectScope
from queries.services.sql.transpiler.transpilers.from_ import FromTranspiler
from queries.services.sql.types import AggregateFunction, aggregate_functions
from sqlglot.expressions import Alias, Column, Expression, Star, column

from .expression import ExpressionTranspiler
from .group_by import GroupByTranspiler
from .join import JoinTranspiler


class SelectTranspiler:
    @staticmethod
    def transpile(scope: SelectScope) -> RAQuery:
        from_query = SelectTranspiler._transpile_from(scope)
        join_query = SelectTranspiler._transpile_joins(scope, from_query)
        where_query = SelectTranspiler._transpile_where(scope, join_query)
        group_by_query, aggregates = SelectTranspiler._transpile_group_by(scope, where_query)
        having_query = SelectTranspiler._transpile_having(scope, group_by_query, aggregates)
        projection_query = SelectTranspiler._transpile_projection(scope, having_query, aggregates)
        return projection_query

    @staticmethod
    def _transpile_from(scope: SelectScope) -> RAQuery:
        return FromTranspiler.transpile(scope)

    @staticmethod
    def _transpile_joins(scope: SelectScope, subquery: RAQuery) -> RAQuery:
        left = subquery
        for join in scope.select.args.get('joins', []):
            left = JoinTranspiler(scope).transpile(join, left)
        return left

    @staticmethod
    def _transpile_where(scope: SelectScope, subquery: RAQuery) -> RAQuery:
        where: Expression | None = scope.select.args.get('where')
        if where:
            return Selection(
                subquery=subquery,
                condition=ExpressionTranspiler.transpile(where.this),
            )
        return subquery

    @staticmethod
    def _transpile_group_by(
        scope: SelectScope, subquery: RAQuery
    ) -> tuple[RAQuery, dict[AggregateFunction, str]]:
        transpiler = GroupByTranspiler()
        return transpiler.transpile(scope.select, subquery), transpiler.aggregates

    @staticmethod
    def _transpile_having(
        scope: SelectScope, subquery: RAQuery, aggregates: dict[AggregateFunction, str]
    ) -> RAQuery:
        having: Expression | None = scope.select.args.get('having')
        if having:
            condition: Expression = having.this
            aggregate_exprs: Iterator[AggregateFunction] = condition.find_all(*aggregate_functions)
            for aggregate in aggregate_exprs:
                aggregate.replace(column(aggregates[aggregate]))
            return Selection(
                subquery=subquery,
                condition=ExpressionTranspiler.transpile(condition),
            )
        return subquery

    @staticmethod
    def _transpile_projection(
        scope: SelectScope, subquery: RAQuery, aggregates: dict[AggregateFunction, str]
    ) -> RAQuery:
        attributes: list[Attribute] = []
        for expr in scope.select.expressions:
            match expr:
                case Column():
                    attributes.append(ExpressionTranspiler.transpile_column(expr))
                case Star():
                    return subquery
                case Alias():
                    inner = expr.this
                    if isinstance(inner, AggregateFunction):
                        attributes.append(Attribute(name=aggregates[inner]))
                case _:
                    raise NotImplementedError(f'Unsupported projection expression: {type(expr)}')
        return Projection(
            subquery=subquery,
            attributes=attributes,
        )
