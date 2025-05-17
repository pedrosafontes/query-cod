from queries.services.ra.parser.ast import (
    Attribute,
    Projection,
    RAQuery,
    Selection,
)
from queries.services.sql.semantics.types import AggregateFunction, aggregate_functions
from queries.services.types import SQLQuery
from sqlglot.expressions import Alias, Column, Select, Star, column

from .expression import ExpressionTranspiler
from .group_by import GroupByTranspiler
from .join import JoinTranspiler
from .table import TableTranspiler


class SQLtoRATranspiler:
    def transpile(self, query: SQLQuery) -> RAQuery:
        match query:
            case Select():
                return self._transpile_select(query)
            case _:
                raise NotImplementedError(f'Unsupported query type: {type(query)}')

    def _transpile_select(self, query: Select) -> RAQuery:
        from_query = self._transpile_from(query)
        join_query = self._transpile_joins(query, from_query)
        where_query = self._transpile_where(query, join_query)
        group_by_query, aggregates = self._transpile_group_by(query, where_query)
        having_query = self._transpile_having(query, group_by_query, aggregates)
        projection_query = self._transpile_projection(query, having_query, aggregates)
        return projection_query

    def _transpile_from(self, query: Select) -> RAQuery:
        from_clause = query.args.get('from')
        if from_clause:
            return TableTranspiler().transpile(from_clause.this)
        else:
            raise ValueError('FROM clause is required in SELECT query')

    def _transpile_joins(self, query: Select, subquery: RAQuery) -> RAQuery:
        left = subquery
        for join in query.args.get('joins', []):
            left = JoinTranspiler().transpile(join, left)
        return left

    def _transpile_where(self, query: Select, subquery: RAQuery) -> RAQuery:
        where = query.args.get('where')
        if where:
            return Selection(
                subquery=subquery,
                condition=ExpressionTranspiler().transpile(where.this),
            )
        return subquery

    def _transpile_group_by(
        self, query: Select, subquery: RAQuery
    ) -> tuple[RAQuery, dict[AggregateFunction, str]]:
        transpiler = GroupByTranspiler()
        return transpiler.transpile(query, subquery), transpiler.aggregates

    def _transpile_having(
        self, query: Select, subquery: RAQuery, aggregates: dict[AggregateFunction, str]
    ) -> RAQuery:
        having = query.args.get('having')
        if having:
            condition = having.this
            for aggregate in condition.find_all(*aggregate_functions):
                aggregate.replace(column(aggregates[aggregate]))
            return Selection(
                subquery=subquery,
                condition=ExpressionTranspiler().transpile(condition),
            )
        return subquery

    def _transpile_projection(
        self, query: Select, subquery: RAQuery, aggregates: dict[AggregateFunction, str]
    ) -> RAQuery:
        attributes: list[Attribute] = []
        for expr in query.expressions:
            match expr:
                case Column():
                    attributes.append(ExpressionTranspiler().transpile_column(expr))
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
