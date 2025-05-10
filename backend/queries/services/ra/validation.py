from databases.models.database_connection_info import DatabaseConnectionInfo
from databases.services.schema import get_schema
from queries.types import QueryError, QueryValidationResult

from ..types import to_relational_schema
from .parser import parse_ra
from .parser.ast import RAQuery
from .parser.errors import RASyntaxError
from .semantics import RASemanticAnalyzer
from .semantics.errors import RASemanticError


def validate_ra(
    query_text: str, db: DatabaseConnectionInfo
) -> tuple[QueryValidationResult, RAQuery | None]:
    if not query_text.strip():
        return {'executable': False}, None

    try:
        query = parse_ra(query_text)
    except RASyntaxError as e:
        syntax_error: QueryError = {'title': e.title}
        if e.description:
            syntax_error['description'] = e.description
        return {
            'executable': False,
            'errors': [syntax_error],
        }, None

    try:
        schema = to_relational_schema(get_schema(db))
        RASemanticAnalyzer(schema).validate(query)
    except RASemanticError as e:
        semantic_error: QueryError = {'title': e.title}
        if e.description:
            semantic_error['description'] = e.description
        if e.position:
            semantic_error['position'] = e.position
        if e.hint:
            semantic_error['hint'] = e.hint
        return {
            'executable': False,
            'errors': [semantic_error],
        }, query

    return {'executable': True}, query
