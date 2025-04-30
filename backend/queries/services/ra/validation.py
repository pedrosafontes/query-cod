from databases.models.database_connection_info import DatabaseConnectionInfo
from databases.services.schema import get_schema
from queries.types import QueryValidationResult

from .parser import parse_ra
from .parser.errors import RASyntaxError
from .semantics import RASemanticAnalyzer
from .semantics.errors import RASemanticError


def validate_ra(query_text: str, db: DatabaseConnectionInfo) -> QueryValidationResult:
    try:
        expr = parse_ra(query_text)
    except RASyntaxError as e:
        return {
            'valid': False,
            'errors': [
                {
                    'title': 'Syntax Error',
                    'description': str(e),
                }
            ],
        }

    try:
        RASemanticAnalyzer(get_schema(db)).validate(expr)
    except RASemanticError as e:
        return {
            'valid': False,
            'errors': [
                {
                    'title': e.title,
                    'description': e.description,
                    'position': {
                        'line': 0,
                        'start_col': e.start_col,
                        'end_col': e.end_col,
                    }
                    if e.source.position
                    else None,
                }
            ],
        }

    return {'valid': True}
