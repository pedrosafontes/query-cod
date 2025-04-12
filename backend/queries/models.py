from django.db import models

from common.models import IndexedTimeStampedModel
from databases.services.execution import execute_sql
from databases.types import QueryExecutionResult
from databases.utils.conversion import from_model
from projects.models import Project
from queries.types import QueryError, QueryValidationResult

from .services.validation import validate_sql


class Query(IndexedTimeStampedModel):
    name = models.CharField(max_length=255)
    text = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='queries')

    def execute(self) -> QueryExecutionResult:
        return execute_sql(self.text, from_model(self.project.database))

    def validate(self) -> QueryValidationResult:
        return validate_sql(self.text, from_model(self.project.database))

    @property
    def validation_errors(self) -> list[QueryError]:
        return self.validate().get('errors', [])

    class Meta:
        ordering = [  # noqa: RUF012
            '-modified'
        ]

    objects: models.Manager['Query']
