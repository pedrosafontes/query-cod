from django.db import models

from common.models import IndexedTimeStampedModel
from databases.models.database import Database
from queries.models import Language


class Exercise(IndexedTimeStampedModel):
    language = models.CharField(
        max_length=16,
        choices=Language,
        default=Language.SQL,
        db_column='language',
    )
    database = models.ForeignKey(Database, on_delete=models.CASCADE, related_name='exercises')
    title = models.CharField(max_length=255)
    description = models.TextField()
    solution = models.TextField()

    objects: models.Manager['Exercise']
