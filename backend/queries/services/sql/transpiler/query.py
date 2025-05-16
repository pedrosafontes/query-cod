from queries.services.ra.parser.ast import (
    Attribute,
    Projection,
    RAQuery,
    Selection,
)
from queries.services.types import SQLQuery
from sqlglot.expressions import Column, Select, Star

from .expression import ExpressionTranspiler
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
        where_query = self._transpile_where(query, from_query)
        projection_query = self._transpile_projection(query, where_query)
        return projection_query

    def _transpile_from(self, query: Select) -> RAQuery:
        from_clause = query.args.get('from')
        if from_clause:
            return TableTranspiler().transpile(from_clause.this)
        else:
            raise ValueError('FROM clause is required in SELECT query')

    def _transpile_where(self, query: Select, subquery: RAQuery) -> RAQuery:
        where = query.args.get('where')
        if where:
            return Selection(
                subquery=subquery,
                condition=ExpressionTranspiler().transpile(where.this),
            )
        return subquery

    def _transpile_projection(self, query: Select, subquery: RAQuery) -> RAQuery:
        attributes: list[Attribute] = []
        for expr in query.expressions:
            if isinstance(expr, Star):
                return subquery
            elif isinstance(expr, Column):
                attributes.append(Attribute(name=expr.name, relation=expr.table))
            else:
                raise NotImplementedError(f'Unsupported projection expression: {type(expr)}')
        return Projection(
            subquery=subquery,
            attributes=attributes,
        )
