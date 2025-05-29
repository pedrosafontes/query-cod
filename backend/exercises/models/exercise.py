from django.db import models

from common.models import IndexedTimeStampedModel
from databases.models.database import Database
from queries.models import AbstractQuery as Query


class Exercise(IndexedTimeStampedModel):
    language = models.CharField(
        max_length=16,
        choices=Query.Language,
        default=Query.Language.SQL,
        db_column='language',
    )
    database = models.ForeignKey(Database, on_delete=models.CASCADE, related_name='exercises')
    description = models.TextField()
    solution = models.TextField()
