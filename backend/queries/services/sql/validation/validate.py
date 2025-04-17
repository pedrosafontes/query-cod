from databases.models import DatabaseConnectionInfo
from databases.services.execution import execute_sql
from queries.services.sql.parser import parse_sql
from queries.types import QueryError, QueryValidationResult
from queries.utils.tokens import to_error_position
from sqlalchemy.exc import SQLAlchemyError
from sqlglot import ParseError


def validate_sql(query_text: str, db: DatabaseConnectionInfo) -> QueryValidationResult:
    if not query_text.strip():
        return {'valid': False}

    # Check for syntax errors
    try:
        parse_sql(query_text, db)
    except ParseError as e:
        syntax_errors: list[QueryError] = [
            {
                'message': err['description'],
                'position': to_error_position(err['line'], err['col'], len(err['highlight'])),
            }
            for err in e.errors
        ]

        return {'valid': False, 'errors': syntax_errors}
    
    explain_errors = _explain(query_text, db)
    if explain_errors:
        return {'valid': False, 'errors': explain_errors}

    return {'valid': True}


def _explain(query_text: str, db: DatabaseConnectionInfo) -> list[QueryError]:
    try:
        execute_sql(f'EXPLAIN {query_text}', db)
    except SQLAlchemyError as e:
        return [
            {
                'message': f'{e.__class__.__name__}: {e}',
            }
        ]
    return []
