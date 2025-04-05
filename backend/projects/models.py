from django.db import models

from databases.models import Database


class Project(models.Model):
    name = models.CharField(max_length=255)
    database = models.ForeignKey(Database, on_delete=models.CASCADE, related_name='projects')
