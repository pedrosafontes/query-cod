from queries.services.ra.parser.ast import RAQuery, Relation
from sqlglot.expressions import Subquery, Table

from ..scope.query import SQLScope
from ..types import SQLTable


class TableTranspiler:
    def __init__(self, scope: SQLScope) -> None:
        self.scope = scope

    def transpile(self, table: SQLTable) -> RAQuery:
        from .query import transpile_query

        relation: RAQuery
        match table:
            case Table():
                relation = Relation(name=table.name)

            case Subquery() as subquery:
                derived_table_scope = self.scope.tables.derived_table_scopes[subquery.alias_or_name]
                relation = transpile_query(derived_table_scope.child)

        if table.alias:
            relation = relation.rename(table.alias)

        return relation
