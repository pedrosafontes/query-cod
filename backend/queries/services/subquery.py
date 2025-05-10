from collections.abc import Mapping

from .ra.parser.ast import RAQuery
from .ra.subquery import RASubqueryExtractor
from .types import QueryAST, SQLQuery


Subqueries = Mapping[int, QueryAST]


def get_subqueries(ast: QueryAST) -> Subqueries:
    match ast:
        case sql_query if isinstance(sql_query, SQLQuery):
            return {}
        case RAQuery():
            return RASubqueryExtractor().extract(ast)
