from typing import cast

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from common.models import IndexedTimeStampedModel
from databases.models.database import Database
from queries.models import AbstractQuery, Language
from users.models import User

from .exercise import Exercise


class Attempt(AbstractQuery, IndexedTimeStampedModel):
    text = models.TextField(blank=True, default='')
    exercise: Exercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, related_name='attempts'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    completed = models.BooleanField(default=False)

    @property
    def query(self) -> str:
        return self.text

    @property
    def language(self) -> Language:
        return cast(Language, self.exercise.language)

    @property
    def database(self) -> Database:
        return cast(Database, self.exercise.database)

    objects: models.Manager['Attempt']

    assistant_messages = GenericRelation(
        'assistant.Message',
        content_type_field='object_type',
        object_id_field='object_id',
    )
