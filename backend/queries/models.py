from django.db import models
from django.utils.functional import cached_property

from common.models import IndexedTimeStampedModel
from projects.models import Project

from .services.ra.tree.types import RATree
from .services.types import QueryAST
from .types import QueryError, QueryValidationResult


class Query(IndexedTimeStampedModel):
    class QueryLanguage(models.TextChoices):
        SQL = 'sql', 'SQL'
        RA = 'ra', 'Relational Algebra'

    name = models.CharField(max_length=255)
    sql_text = models.TextField(blank=True, default='')
    ra_text = models.TextField(blank=True, default='')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='queries')
    language = models.CharField(
        max_length=16,
        choices=QueryLanguage,
        default=QueryLanguage.SQL,
    )

    @cached_property
    def validation_result(self) -> tuple[QueryValidationResult, QueryAST | None]:
        from .services.validation import validate_query

        return validate_query(self)

    @property
    def validation_errors(self) -> list[QueryError]:
        validation, _ = self.validation_result
        return validation.get('errors', [])

    @property
    def tree(self) -> RATree | None:
        from .services.tree import transform_ast

        _, ast = self.validation_result
        return transform_ast(ast) if ast else None

    class Meta:
        ordering = [  # noqa: RUF012
            '-modified'
        ]

    objects: models.Manager['Query']
