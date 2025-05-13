from queries.models import Query
from rest_framework import serializers


class QuerySerializer(serializers.ModelSerializer[Query]):
    class Meta:
        model = Query
        fields = [  # noqa: RUF012
            'id',
            'name',
            'sql_text',
            'ra_text',
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
        ]
