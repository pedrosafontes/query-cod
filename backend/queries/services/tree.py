from collections.abc import Mapping

from databases.models.database_connection_info import DatabaseConnectionInfo
from databases.services.schema import get_schema

from .ra.parser.ast import RAQuery
from .ra.tree.builder import RATreeBuilder
from .ra.tree.types import RATree
from .sql.tree.builder import SQLTreeBuilder
from .sql.tree.types import SQLTree
from .types import QueryAST, SQLQuery, to_relational_schema


QueryTree = RATree | SQLTree
Subqueries = Mapping[int, QueryAST]


def build_query_tree(
    ast: QueryAST, db: DatabaseConnectionInfo
) -> tuple[QueryTree | None, Subqueries]:
    match ast:
        case RAQuery():
            schema = to_relational_schema(get_schema(db))
            return RATreeBuilder(schema).build(ast)
        case SQLQuery():
            return SQLTreeBuilder().build(ast)
