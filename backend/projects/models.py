from django.db import models

from common.models import IndexedTimeStampedModel
from databases.models import Database


class Project(IndexedTimeStampedModel):
    name = models.CharField(max_length=255)
    database = models.ForeignKey(Database, on_delete=models.CASCADE, related_name='projects')
