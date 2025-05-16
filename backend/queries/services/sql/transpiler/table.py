from queries.services.ra.parser.ast import RAQuery, Relation
from sqlglot.expressions import Subquery, Table


class TableTranspiler:
    def transpile(self, table: Table | Subquery) -> RAQuery:
        from .query import SQLtoRATranspiler

        match table:
            case Table():
                return Relation(name=table.name)

            case Subquery():
                return SQLtoRATranspiler().transpile(table)
