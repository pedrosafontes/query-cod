from databases.types import Schema
from sqlglot import Expression

from .validators.query import QueryValidator


class SQLSemanticAnalyzer:
    def __init__(self, schema: Schema) -> None:
        self.query_validator = QueryValidator(schema)

    def validate(self, query: Expression) -> None:
        self.query_validator.validate(query, outer_scope=None)
