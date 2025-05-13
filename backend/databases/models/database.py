from django.db import models
from django.utils.functional import cached_property

from common.models import IndexedTimeStampedModel

from .database_connection_info import DatabaseConnectionInfo


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
    database_type = models.CharField(
        max_length=16,
        choices=DatabaseType,
        default=DatabaseType.POSTGRESQL,
    )

    def __str__(self) -> str:
        return f'{self.name}'

    objects: models.Manager['Database']

    @cached_property
    def connection_info(self) -> DatabaseConnectionInfo:
        return DatabaseConnectionInfo(
            database_type=self.database_type,
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            name=self.database_name,
        )
