from queries.serializers.error import QueryErrorSerializer
from rest_framework import serializers

from ..models import Query


class QuerySerializer(serializers.ModelSerializer[Query]):
    validation_errors = QueryErrorSerializer(many=True, read_only=True)

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
        ]


class QuerySummarySerializer(serializers.ModelSerializer[Query]):
    class Meta:
        model = Query
        fields = [  # noqa: RUF012
            'id',
            'name',
            'language',
        ]
