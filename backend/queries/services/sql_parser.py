from sqlglot import ParseError, parse_one

from databases.models import DatabaseConnectionInfo
from databases.services.execution import execute_sql

from sqlalchemy.exc import SQLAlchemyError


def parse_sql(query_text, db: DatabaseConnectionInfo):
    query_text = query_text.strip()
    if not query_text:
        return {'valid': False, 'errors': []}

    # Syntax check with sqlglot
    try:
        tree = parse_one(query_text, read=_database_type_to_sqlglot(db.type))
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

    if tree.key != 'select':
        return {
            'valid': False,
            'errors': [
                {
                    'message': 'Only SELECT queries are allowed.',
                    'line': 1,
                    'start_col': 1,
                    'end_col': 7,
                }
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
