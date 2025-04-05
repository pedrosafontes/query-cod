from django.db import models


class Database(models.Model):
    class DatabaseType(models.TextChoices):
        POSTGRESQL = 'postgresql'
        MYSQL = 'mysql'
        SQLITE = 'sqlite'

    name = models.CharField(max_length=255)
    description = models.TextField()
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    database_name = models.CharField(max_length=255)
    type = models.CharField(
        choices=DatabaseType.choices,
        default=DatabaseType.POSTGRESQL,
    )
