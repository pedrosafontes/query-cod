from databases.types import QueryExecutionResult
from drf_spectacular.helpers import lazy_serializer
from drf_spectacular.utils import extend_schema_field
from queries.types import QueryExecutionResponse
from rest_framework import serializers

from .models import Query
from .services.ra.tree.types import RATree


class RATreeSerializer(serializers.Serializer[RATree]):
    id = serializers.IntegerField()
    label = serializers.CharField()  # type: ignore[assignment]
    sub_trees = serializers.SerializerMethodField()

    @extend_schema_field(
        lazy_serializer('queries.serializers.RATreeSerializer')(many=True, required=False)
    )
    def get_sub_trees(self, obj: RATree) -> list[RATree] | None:
        return obj.get('sub_trees')


class QuerySerializer(serializers.ModelSerializer[Query]):
    tree = RATreeSerializer(required=False)

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
            'tree',
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
