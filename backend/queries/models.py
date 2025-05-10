from django.db import models
from django.utils.functional import cached_property

from common.models import IndexedTimeStampedModel
from projects.models import Project

from .services.ra.tree.types import RATree
from .services.subquery import Subqueries, get_subqueries
from .services.types import QueryAST
from .types import QueryError


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
    def validation_result(self) -> tuple[QueryAST | None, list[QueryError]]:
        from .services.validation import validate_query

        return validate_query(self)

    @property
    def is_executable(self) -> bool:
        ast, errors = self.validation_result
        return ast is not None and not errors

    @property
    def ast(self) -> QueryAST | None:
        ast, _ = self.validation_result
        return ast

    @property
    def validation_errors(self) -> list[QueryError]:
        _, errors = self.validation_result
        return errors

    @property
    def tree(self) -> RATree | None:
        from .services.tree import transform_ast

        return transform_ast(self.ast) if self.ast else None

    @property
    def subqueries(self) -> Subqueries:
        return get_subqueries(self.ast) if self.ast else {}

    class Meta:
        ordering = [  # noqa: RUF012
            '-modified'
        ]

    objects: models.Manager['Query']
