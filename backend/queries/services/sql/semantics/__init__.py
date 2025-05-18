from queries.services.types import RelationalSchema, SQLQuery, to_sqlglot_schema
from queries.types import QueryError
from sqlglot.optimizer.annotate_types import annotate_types
from sqlglot.optimizer.qualify_columns import qualify_columns

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
        self.schema = schema

    def validate(self, query: SQLQuery) -> None:
        sqlglot_schema = to_sqlglot_schema(self.schema)
        qualified: SQLQuery = qualify_columns(
            query, schema=sqlglot_schema, expand_stars=False, expand_alias_refs=False
        )
        typed: SQLQuery = annotate_types(qualified, schema=sqlglot_schema)
        QueryValidator(self.schema).validate(typed, outer_scope=None)
