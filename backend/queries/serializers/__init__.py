from queries.models import Query
from queries.serializers.tree import RATreeSerializer, SQLTreeSerializer
from rest_framework import serializers


class QuerySerializer(serializers.ModelSerializer[Query]):
    sql_tree = SQLTreeSerializer(required=False)
    ra_tree = RATreeSerializer(required=False)

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
            'sql_tree',
            'ra_tree',
        ]


class QuerySummarySerializer(serializers.ModelSerializer[Query]):
    class Meta:
        model = Query
        fields = [  # noqa: RUF012
            'id',
            'name',
        ]
