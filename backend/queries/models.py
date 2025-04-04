from django.db import connection, models

from common.models import IndexedTimeStampedModel

from .services.sql_parser import parse_sql


class Query(IndexedTimeStampedModel):
    text = models.TextField(blank=True)

    def execute(self):
        with connection.cursor() as cursor:
            cursor.execute(self.text)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
        return {'columns': columns, 'rows': rows}

    def parse(self):
        return parse_sql(self.text)
