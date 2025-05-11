from django.db import models
from django.utils.functional import cached_property

from common.models import IndexedTimeStampedModel
from projects.models import Project

from .services.tree import QueryTree, Subqueries
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

    @cached_property
    def tree_with_subqueries(self) -> tuple[QueryTree, Subqueries] | None:
        from .services.tree import build_query_tree

        return build_query_tree(self.ast) if self.ast else None

    @property
    def tree(self) -> QueryTree | None:
        if self.tree_with_subqueries is None:
            return None

        tree, _ = self.tree_with_subqueries
        return tree

    @property
    def subqueries(self) -> Subqueries:
        if self.tree_with_subqueries is None:
            return {}

        _, subqueries = self.tree_with_subqueries
        return subqueries

    class Meta:
        ordering = [  # noqa: RUF012
            '-modified'
        ]

    objects: models.Manager['Query']
