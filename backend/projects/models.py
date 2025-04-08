from django.db import models
from django.db.models import Max, DateTimeField
from django.db.models.functions import Greatest

from users.models import User
from common.models import IndexedTimeStampedModel
from databases.models import Database


class Project(IndexedTimeStampedModel):
    name = models.CharField(max_length=255)
    database = models.ForeignKey(Database, on_delete=models.CASCADE, related_name='projects')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')

    @classmethod
    def with_last_modified(cls):
        return cls.objects.annotate(
            last_modified=Greatest(
                Max('queries__created'),
                Max('queries__modified'),
                Max('modified'),
                output_field=DateTimeField(),
            )
        ).order_by('-last_modified')
