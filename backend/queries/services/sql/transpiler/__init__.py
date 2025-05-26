from queries.services.ra.parser.ast import RAQuery
from queries.services.types import RelationalSchema, SQLQuery

from ..scope.builder import build_scope
from .normaliser import SQLQueryNormaliser
from .query import QueryTranspiler


class SQLtoRATranspiler:
    def __init__(self, schema: RelationalSchema):
        self.schema = schema

    def transpile(self, query: SQLQuery) -> RAQuery:
        normalised = SQLQueryNormaliser.normalise(query, self.schema)
        scope = build_scope(normalised, self.schema)
        return QueryTranspiler.transpile(scope)
