from queries.services.ra.parser.ast import Attribute, RAQuery
from queries.services.sql.scope.query import SQLScope
from queries.services.sql.scope.tables import Source
from sqlglot.expressions import Column, Expression, Table

from .table import TableTranspiler


class ContextRelationInferrer:
    def __init__(self, scope: SQLScope):
        self.scope = scope

    def infer(self, expr: Expression) -> tuple[list[RAQuery], list[Attribute]]:
        sources: list[Source] = []
        for column in expr.find_all(Column):
            if column not in self.scope.tables and (
                source := self.scope.tables.find_column_source(column)
            ):
                sources.append(source)

        relations = [self._transpile_source(source) for source in sources]
        parameters = [
            Attribute(name=name, relation=source.name)
            for source in sources
            for name in source.attributes
        ]
        return relations, parameters

    def _transpile_source(self, source: Source) -> RAQuery:
        from .query import QueryTranspiler

        match source.table:
            case Table():
                return TableTranspiler(self.scope).transpile(source.table)
            case SQLScope():
                return QueryTranspiler.transpile(source.table)
