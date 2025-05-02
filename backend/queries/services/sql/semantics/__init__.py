from queries.services.types import RelationalSchema
from sqlglot import Expression

from .validators.query import QueryValidator


class SQLSemanticAnalyzer:
    def __init__(self, schema: RelationalSchema) -> None:
        self.query_validator = QueryValidator(schema)

    def validate(self, query: Expression) -> None:
        self.query_validator.validate(query, outer_scope=None)
