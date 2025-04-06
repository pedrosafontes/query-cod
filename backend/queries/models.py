from django.db import models

from databases.utils.conversion import from_model
from databases.services.execution import execute_sql
from common.models import IndexedTimeStampedModel
from projects.models import Project

from .services.sql_parser import parse_sql


class Query(IndexedTimeStampedModel):
    name = models.CharField(max_length=255)
    text = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='queries')

    def execute(self):
        return execute_sql(self.text, from_model(self.project.database))

    def parse(self):
        return parse_sql(self.text, from_model(self.project.database))
