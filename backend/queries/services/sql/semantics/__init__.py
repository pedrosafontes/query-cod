from databases.types import Schema
from sqlglot import Expression

from .query import QueryValidator


class SQLSemanticAnalyzer:
    def __init__(self, schema: Schema) -> None:
        self.schema = schema

    def validate(self, query: Expression) -> None:
        QueryValidator(self.schema).validate(query, outer_scope=None)
