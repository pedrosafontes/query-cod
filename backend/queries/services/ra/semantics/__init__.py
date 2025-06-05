from queries.services.types import RelationalSchema
from queries.types import QueryError

from ..ast import RAQuery
from .errors.base import RASemanticError
from .validator import RASemanticValidator


def validate_ra_semantics(query: RAQuery, schema: RelationalSchema) -> list[QueryError]:
    try:
        RASemanticValidator(schema).validate(query)
    except RASemanticError as e:
        semantic_error: QueryError = {'title': e.title}
        if e.description:
            semantic_error['description'] = e.description
        if e.hint:
            semantic_error['hint'] = e.hint
        return [semantic_error]

    return []
