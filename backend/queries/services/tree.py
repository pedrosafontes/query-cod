from collections.abc import Mapping

from .ra.parser.ast import RAQuery
from .ra.tree.builder import RATreeBuilder
from .ra.tree.types import RATree
from .types import QueryAST


QueryTree = RATree | None  # TODO: Replace with SQLTree
Subqueries = Mapping[int, QueryAST]


def build_query_tree(ast: QueryAST) -> tuple[QueryTree, Subqueries]:
    match ast:
        case RAQuery():
            return RATreeBuilder().build(ast)
        case _:
            return None, {}
