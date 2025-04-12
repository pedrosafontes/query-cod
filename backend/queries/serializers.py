from databases.types import QueryExecutionResult
from queries.types import QueryExecutionResponse
from rest_framework import serializers

from .models import Query


class QuerySerializer(serializers.ModelSerializer[Query]):
    text = serializers.CharField(required=True, allow_blank=True)

    class Meta:
        model = Query
        fields = [  # noqa: RUF012
            'id',
            'name',
            'text',
            'created',
            'modified',
            'validation_errors',
        ]


class QueryResultDataSerializer(serializers.Serializer[QueryExecutionResult]):
    columns = serializers.ListField(
        child=serializers.CharField(), help_text='List of column names from the query'
    )
    rows: serializers.ListSerializer[list[str]] = serializers.ListSerializer(
        child=serializers.ListField(
            child=serializers.CharField(allow_null=True), help_text='Values in a single row'
        ),
        help_text='List of query result rows',
    )


class QueryExecutionSerializer(serializers.Serializer[QueryExecutionResponse]):
    results = QueryResultDataSerializer(
        required=False, help_text='Query result data if the query execution was successful'
    )
    success = serializers.BooleanField(help_text='Indicates if the query execution was successful')


class QuerySummarySerializer(serializers.ModelSerializer[Query]):
    class Meta:
        model = Query
        fields = [  # noqa: RUF012
            'id',
            'name',
        ]
