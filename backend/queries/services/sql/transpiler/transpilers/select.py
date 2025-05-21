from collections.abc import Iterator

from queries.services.ra.parser.ast import (
    Attribute,
    Projection,
    RAQuery,
    Selection,
)
from queries.services.sql.types import AggregateFunction, aggregate_functions
from sqlglot.expressions import Alias, Column, Expression, From, Select, Star, column

from .expression import ExpressionTranspiler
from .group_by import GroupByTranspiler
from .join import JoinTranspiler
from .table import TableTranspiler


class SelectTranspiler:
    @staticmethod
    def transpile(select: Select) -> RAQuery:
        from_query = SelectTranspiler._transpile_from(select)
        join_query = SelectTranspiler._transpile_joins(select, from_query)
        where_query = SelectTranspiler._transpile_where(select, join_query)
        group_by_query, aggregates = SelectTranspiler._transpile_group_by(select, where_query)
        having_query = SelectTranspiler._transpile_having(select, group_by_query, aggregates)
        projection_query = SelectTranspiler._transpile_projection(select, having_query, aggregates)
        return projection_query

    @staticmethod
    def _transpile_from(select: Select) -> RAQuery:
        from_clause: From | None = select.args.get('from')
        if from_clause:
            return TableTranspiler.transpile(from_clause.this)
        else:
            raise ValueError('FROM clause is required in SELECT query')

    @staticmethod
    def _transpile_joins(select: Select, subquery: RAQuery) -> RAQuery:
        left = subquery
        for join in select.args.get('joins', []):
            left = JoinTranspiler.transpile(join, left)
        return left

    @staticmethod
    def _transpile_where(select: Select, subquery: RAQuery) -> RAQuery:
        where: Expression | None = select.args.get('where')
        if where:
            return Selection(
                subquery=subquery,
                condition=ExpressionTranspiler.transpile(where.this),
            )
        return subquery

    @staticmethod
    def _transpile_group_by(
        select: Select, subquery: RAQuery
    ) -> tuple[RAQuery, dict[AggregateFunction, str]]:
        transpiler = GroupByTranspiler()
        return transpiler.transpile(select, subquery), transpiler.aggregates

    @staticmethod
    def _transpile_having(
        select: Select, subquery: RAQuery, aggregates: dict[AggregateFunction, str]
    ) -> RAQuery:
        having: Expression | None = select.args.get('having')
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
        select: Select, subquery: RAQuery, aggregates: dict[AggregateFunction, str]
    ) -> RAQuery:
        attributes: list[Attribute] = []
        for expr in select.expressions:
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
