from typing import TYPE_CHECKING

from django.core.cache import cache
from django.db import models

from common.models import IndexedTimeStampedModel
from databases.models.database import Database
from databases.types import QueryResult
from queries.models import Language
from queries.services.execution import execute_query
from users.models import User

from .solution import Solution


if TYPE_CHECKING:
    from .attempt import Attempt


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
    attempts: models.Manager['Attempt']

    def completed_by(self, user: User) -> bool:
        return self.attempts.filter(user=user, completed=True).exists()

    @property
    def solution_data(self) -> QueryResult | None:
        cache_key = f'exercise_{self.id}'
        result: QueryResult = cache.get(cache_key)

        if result is None:
            result = execute_query(Solution(self))
            cache.set(cache_key, result)

        return result
