from assistant.serializers import MessageSerializer
from queries.models import Language
from queries.serializers.error import QueryErrorSerializer
from rest_framework import serializers

from ..models import Query


class QuerySerializer(serializers.ModelSerializer[Query]):
    validation_errors = QueryErrorSerializer(many=True, read_only=True)
    assistant_messages = MessageSerializer(many=True, read_only=True)
    language = serializers.ChoiceField(source='_language', choices=Language.choices)

    class Meta:
        model = Query
        fields = [  # noqa: RUF012
            'id',
            'name',
            'text',
            'language',
            'created',
            'modified',
            'validation_errors',
            'assistant_messages',
        ]


class QuerySummarySerializer(serializers.ModelSerializer[Query]):
    language = serializers.ChoiceField(source='_language', choices=Language.choices)

    class Meta:
        model = Query
        fields = [  # noqa: RUF012
            'id',
            'name',
            'language',
        ]
