from queries.services.ra.parser.ast import RAQuery, Relation
from sqlglot.expressions import Subquery, Table

from ..scope.query import SelectScope
from ..types import SQLTable


class TableTranspiler:
    def __init__(self, scope: SelectScope) -> None:
        self.scope = scope

    def transpile(self, table: SQLTable) -> RAQuery:
        from .query import QueryTranspiler

        match table:
            case Table():
                return Relation(name=table.name)

            case Subquery() as subquery:
                subquery_scope = self.scope.tables.derived_table_scopes[subquery.alias_or_name]
                return QueryTranspiler.transpile(subquery_scope)
