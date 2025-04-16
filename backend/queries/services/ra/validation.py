from .errors import RASyntaxError
from queries.types import QueryValidationResult

from .parser import parse_ra


def validate_ra(query_text: str) -> QueryValidationResult:
    try:
        parse_ra(query_text)
        return {
            'valid': True,
        }
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
    except Exception as e:
        return { 'valid': False }
