from django.db import connection, models

from common.models import IndexedTimeStampedModel


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