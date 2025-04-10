from databases.models import DatabaseConnectionInfo
from databases.services.execution import execute_sql
from sqlalchemy.exc import SQLAlchemyError
from sqlglot import ParseError, parse_one, expressions


def validate_sql(query_text: str, db: DatabaseConnectionInfo):
    if not query_text.strip():
        return {'valid': False, 'errors': []}

    # Syntax check with sqlglot
    try:
        parse_one(
            query_text,
            read=_database_type_to_sqlglot(db.database_type),
            into=expressions.Select,
        )
    except ParseError as e:
        return {
            'valid': False,
            'errors': [
                {
                    'message': err['description'],
                    'line': err['line'],
                    'start_col': err['col'],
                    'end_col': err['col'] + len(err['highlight'] or ' '),
                }
                for err in e.errors
            ],
        }

    # Semantic check with EXPLAIN
    try:
        execute_sql(f'EXPLAIN {query_text}', db)
    except SQLAlchemyError as e:
        return {
            'valid': False,
            'errors': [
                {
                    'message': f'Semantic error: {e!s}',
                    'line': 1,
                    'start_col': 1,
                    'end_col': 7,
                }
            ],
        }

    return {'valid': True}


def _database_type_to_sqlglot(db_type: str) -> str:
    return {
        'postgresql': 'postgres',
    }.get(db_type, db_type)
