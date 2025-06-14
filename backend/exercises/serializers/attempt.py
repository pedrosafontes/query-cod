from assistant.serializers import MessageSerializer
from queries.models import Language
from queries.serializers.error import QueryErrorSerializer
from rest_framework import serializers

from ..models.attempt import Attempt


class AttemptSerializer(serializers.ModelSerializer[Attempt]):
    validation_errors = QueryErrorSerializer(many=True, read_only=True)
    assistant_messages = MessageSerializer(many=True, read_only=True)
    language = serializers.ChoiceField(choices=Language.choices, read_only=True)

    class Meta:
        model = Attempt
        fields = [  # noqa: RUF012
            'id',
            'text',
            'validation_errors',
            'completed',
            'language',
            'assistant_messages',
        ]
