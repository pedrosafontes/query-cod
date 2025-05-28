from collections.abc import Mapping

from databases.models import Database

from .ra.ast import RAQuery
from .ra.tree.builder import RATreeBuilder
from .ra.tree.types import RATree
from .sql.tree.builder import SQLTreeBuilder
from .sql.tree.types import SQLTree
from .types import QueryAST, SQLQuery, to_relational_schema


QueryTree = RATree | SQLTree
Subqueries = Mapping[int, QueryAST]


def build_query_tree(ast: QueryAST, db: Database) -> tuple[QueryTree | None, Subqueries]:
    schema = to_relational_schema(db.schema)
    match ast:
        case RAQuery():
            return RATreeBuilder(schema).build(ast)
        case SQLQuery():
            return SQLTreeBuilder(schema).build(ast)
