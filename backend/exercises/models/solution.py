from typing import TYPE_CHECKING, cast

from databases.models.database import Database
from queries.models import AbstractQuery, Language


if TYPE_CHECKING:
    from .exercise import Exercise


class Solution(AbstractQuery):
    def __init__(self, exercise: 'Exercise'):
        self.exercise = exercise

    @property
    def query(self) -> str:
        return self.exercise.solution

    @property
    def language(self) -> Language:
        return cast(Language, self.exercise.language)

    @property
    def database(self) -> Database:
        return cast(Database, self.exercise.database)
