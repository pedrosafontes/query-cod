from django.db import DatabaseError, connection, models

from common.models import IndexedTimeStampedModel
from sqlglot import ParseError, parse_one


class Query(IndexedTimeStampedModel):
    text = models.TextField(blank=True)

    def execute(self):
        with connection.cursor() as cursor:
            cursor.execute(self.text)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
        return {
            'columns': columns,
            'rows': rows
        }
    
    def parse(self):
        if not self.text.strip():
            return { 'valid': False, 'error': 'Query is empty' }

        # Syntax check with sqlglot
        try:
            tree = parse_one(self.text, read='postgres')
        except ParseError as e:
            return { 'valid': False, 'error': str(e) }
        
        if tree.key != 'select':
            return {'valid': False, 'error': 'Only SELECT queries are allowed'}

        # Semantic check with EXPLAIN
        try:
            with connection.cursor() as cursor:
                cursor.execute(f'EXPLAIN {self.text}')
        except DatabaseError as e:
            return { 'valid': False, 'error': str(e) }

        return { 'valid': True }