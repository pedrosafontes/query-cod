from django.db import DatabaseError, connection

from sqlglot import ParseError, parse_one


def parse_sql(query_text, dialect='postgres'):
        query_text = query_text.strip()
        if not query_text:
            return {
                'valid': False,
                'errors': []
            }

        # Syntax check with sqlglot
        try:
            tree = parse_one(query_text, read=dialect)
        except ParseError as e:
            return { 
                'valid': False,
                'errors': [{
                    "message": err['description'],
                    "line": err['line'],
                    "start_col": err['col'],
                    "end_col": err['col'] + len(err['highlight'] or " "),
                } for err in e.errors]
            }
        
        if tree.key != 'select':
            return {
                'valid': False,
                'errors': [{
                    'message': 'Only SELECT queries are allowed.',
                    'line': 1,
                    'start_col': 1,
                    'end_col': 7,
                }]
            }

        # Semantic check with EXPLAIN
        try:
            with connection.cursor() as cursor:
                cursor.execute(f'EXPLAIN {query_text}')
        except DatabaseError as e:
            return {
                'valid': False,
                'errors': [{
                    'message': f'Semantic error: {e!s}',
                    'line': 1,
                    'start_col': 1,
                    'end_col': 7,
                }]
            }

        return { 'valid': True }