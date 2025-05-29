from django.db import models

from common.models import IndexedTimeStampedModel
from databases.models.database import Database
from queries.models import Language


class Exercise(IndexedTimeStampedModel):
    class Difficulty(models.TextChoices):
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'

    difficulty = models.CharField(
        max_length=16,
        choices=Difficulty,
    )
    language = models.CharField(
        max_length=16,
        choices=Language,
    )
    database = models.ForeignKey(Database, on_delete=models.CASCADE, related_name='exercises')
    title = models.CharField(max_length=255)
    description = models.TextField()
    solution = models.TextField()

    objects: models.Manager['Exercise']
