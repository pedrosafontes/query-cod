from queries.models import Query
from rest_framework import serializers

from .error import QueryErrorSerializer


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
