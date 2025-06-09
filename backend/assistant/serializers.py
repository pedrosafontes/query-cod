from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer[Message]):
    class Meta:
        model = Message
        fields = ['id', 'author', 'content', 'created']  # noqa: RUF012
        read_only_fields = ['id', 'author', 'created']  # noqa: RUF012
