from typing import cast

from django.db import models

from common.models import IndexedTimeStampedModel
from databases.models.database import Database
from queries.models import AbstractQuery, Language

from .project import Project


class Query(AbstractQuery, IndexedTimeStampedModel):
    text = models.TextField(blank=True, default='')
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='queries')
    _language = models.CharField(
        max_length=16,
        choices=Language,
        default=Language.SQL,
        db_column='language',
    )

    @property
    def query(self) -> str:
        return self.text

    @property
    def language(self) -> Language:
        return cast(Language, self._language)

    @property
    def database(self) -> Database:
        return cast(Database, self.project.database)

    objects: models.Manager['Query']
