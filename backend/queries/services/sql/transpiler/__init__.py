from queries.services.ra.parser.ast import RAQuery
from queries.services.types import RelationalSchema, SQLQuery

from ..scope.builder import build_scope
from .query import QueryTranspiler


class SQLtoRATranspiler:
    def __init__(self, schema: RelationalSchema):
        self.schema = schema

    def transpile(self, query: SQLQuery) -> RAQuery:
        scope = build_scope(query, self.schema)
        return QueryTranspiler.transpile(scope)
