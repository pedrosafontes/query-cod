from databases.types import QueryResult
from queries.types import QueryExecutionResponse
from rest_framework import serializers


class QueryResultDataSerializer(serializers.Serializer[QueryResult]):
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
