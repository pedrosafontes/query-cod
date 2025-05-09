from django.db import models

from common.models import IndexedTimeStampedModel
from projects.models import Project
from queries.services.ra.parser import parse_ra
from queries.services.ra.parser.errors.base import RASyntaxError
from queries.services.ra.tree.converter import RATreeConverter
from queries.services.ra.tree.types import RATree
from queries.types import QueryError


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

    @property
    def validation_errors(self) -> list[QueryError]:
        from .services.validation import validate_query

        return validate_query(self).get('errors', [])

    @property
    def tree(self) -> RATree | None:
        match self.language:
            case Query.QueryLanguage.SQL:
                return None
            case Query.QueryLanguage.RA:
                try:
                    ast = parse_ra(self.ra_text)
                    return RATreeConverter().convert(ast)
                except RASyntaxError:
                    return None
            case _:
                raise ValueError(f'Unsupported query language: {self.language}')

    class Meta:
        ordering = [  # noqa: RUF012
            '-modified'
        ]

    objects: models.Manager['Query']
