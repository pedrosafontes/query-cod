from typing import cast

from django.db import models

from databases.models.database import Database
from queries.models import AbstractQuery, Language
from users.models import User

from .exercise import Exercise


class Attempt(AbstractQuery):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    completed = models.BooleanField(default=False)

    @property
    def language(self) -> Language:
        return cast(Language, self.exercise.language)

    @property
    def database(self) -> Database:
        return cast(Database, self.exercise.database)

    objects: models.Manager['Attempt']
