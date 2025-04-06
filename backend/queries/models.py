from django.db import connection, models

from common.models import IndexedTimeStampedModel
from projects.models import Project

from .services.sql_parser import parse_sql


class Query(IndexedTimeStampedModel):
    name = models.CharField(max_length=255)
    text = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='queries')

    def execute(self):
        with connection.cursor() as cursor:
            cursor.execute(self.text)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
        return {'columns': columns, 'rows': rows}

    def parse(self):
        return parse_sql(self.text)
