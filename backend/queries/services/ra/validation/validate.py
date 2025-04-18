from databases.models.database_connection_info import DatabaseConnectionInfo
from databases.services.schema import get_schema
from queries.types import QueryValidationResult

from ..parser import parse_ra
from ..parser.errors import RASyntaxError
from .semantics import RASemanticAnalyzer


def validate_ra(query_text: str, db: DatabaseConnectionInfo) -> QueryValidationResult:
    try:
        expr = parse_ra(query_text)
    except RASyntaxError as e:
        return {
            'valid': False,
            'errors': [
                {
                    'message': str(e),
                    'position': {
                        'line': e.line,
                        'start_col': e.column,
                        'end_col': e.column + 1,
                    },
                }
            ],
        }

    schema = get_schema(db)
    schema_errors = RASemanticAnalyzer(schema).validate(expr)
    if schema_errors:
        return {
            'valid': False,
            'errors': [
                {
                    'message': str(e),
                }
                for e in schema_errors
            ],
        }

    return {'valid': True}
