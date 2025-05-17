from queries.services.types import RelationalSchema, SQLQuery
from queries.types import QueryError

from .errors.base import SQLSemanticError
from .validators.query import QueryValidator


def validate_sql_semantics(query: SQLQuery, schema: RelationalSchema) -> list[QueryError]:
    try:
        QueryValidator(schema).validate(query)
    except SQLSemanticError as e:
        semantic_error: QueryError = {'title': e.title}
        if e.description:
            semantic_error['description'] = e.description
        if e.hint:
            semantic_error['hint'] = e.hint
        return [semantic_error]

    return []
