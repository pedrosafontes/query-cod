from queries.services.types import RelationalSchema, SQLQuery
from queries.types import QueryError
from sqlglot import Expression

from .errors.base import SQLSemanticError
from .validators.query import QueryValidator


def validate_sql_semantics(query: SQLQuery, schema: RelationalSchema) -> list[QueryError]:
    try:
        SQLSemanticAnalyzer(schema).validate(query)
    except SQLSemanticError as e:
        semantic_error: QueryError = {'title': e.title}
        if e.description:
            semantic_error['description'] = e.description
        if e.hint:
            semantic_error['hint'] = e.hint
        return [semantic_error]

    return []


class SQLSemanticAnalyzer:
    def __init__(self, schema: RelationalSchema) -> None:
        self.query_validator = QueryValidator(schema)

    def validate(self, query: Expression) -> None:
        self.query_validator.validate(query, outer_scope=None)
