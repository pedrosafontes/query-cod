from collections.abc import Mapping

from .ra.parser.ast import RAQuery
from .ra.tree.builder import RATreeBuilder
from .ra.tree.types import RATree
from .sql.tree.builder import SQLTreeBuilder
from .sql.tree.types import SQLTree
from .types import QueryAST, SQLQuery


QueryTree = RATree | SQLTree
Subqueries = Mapping[int, QueryAST]


def build_query_tree(ast: QueryAST) -> tuple[QueryTree | None, Subqueries]:
    match ast:
        case RAQuery():
            return RATreeBuilder().build(ast)
        case SQLQuery():
            return SQLTreeBuilder().build(ast)
