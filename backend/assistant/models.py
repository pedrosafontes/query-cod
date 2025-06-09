from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from common.models import IndexedTimeStampedModel


class Message(IndexedTimeStampedModel):
    class Author(models.TextChoices):
        USER = 'user', 'User'
        ASSISTANT = 'assistant', 'Assistant'

    # Generic relation to either Query or Attempt
    object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    parent = GenericForeignKey('object_type', 'object_id')

    author = models.CharField(
        max_length=10,
        choices=Author.choices,
    )
    content = models.TextField()

    objects: models.Manager['Message']

    class Meta:
        ordering = ['created']  # noqa: RUF012
