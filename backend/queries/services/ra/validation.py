from databases.models.database_connection_info import DatabaseConnectionInfo
from databases.services.schema import get_schema
from queries.types import QueryError, QueryValidationResult

from .parser import parse_ra
from .parser.errors import RASyntaxError
from .semantics import RASemanticAnalyzer
from .semantics.errors import RASemanticError


def validate_ra(query_text: str, db: DatabaseConnectionInfo) -> QueryValidationResult:
    try:
        expr = parse_ra(query_text)
    except RASyntaxError as e:
        syntax_error: QueryError = {'title': e.title}
        if e.description:
            syntax_error['description'] = e.description
        return {
            'valid': False,
            'errors': [syntax_error],
        }

    try:
        RASemanticAnalyzer(get_schema(db)).validate(expr)
    except RASemanticError as e:
        semantic_error: QueryError = {'title': e.title}
        if e.description:
            semantic_error['description'] = e.description
        if e.position:
            semantic_error['position'] = e.position
        return {
            'valid': False,
            'errors': [semantic_error],
        }

    return {'valid': True}
