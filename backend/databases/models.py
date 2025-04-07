from django.db import models
from dataclasses import dataclass

from common.models import IndexedTimeStampedModel

class Database(IndexedTimeStampedModel):
    class DatabaseType(models.TextChoices):
        POSTGRESQL = 'postgresql', 'PostgreSQL'

    name = models.CharField(max_length=255)
    description = models.TextField()
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    user = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    database_name = models.CharField(max_length=255)
    type = models.CharField(
        choices=DatabaseType.choices,
        default=DatabaseType.POSTGRESQL,
    )

    def __str__(self):
        return f'{self.name}'


@dataclass
class DatabaseConnectionInfo:
    type: str
    host: str
    port: int
    user: str
    password: str
    name: str
