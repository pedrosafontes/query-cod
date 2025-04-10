from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Query


class ErrorPositionSerializer(serializers.Serializer):
    line = serializers.IntegerField()
    start_col = serializers.IntegerField()
    end_col = serializers.IntegerField()


class QueryErrorSerializer(serializers.Serializer):
    message = serializers.CharField()
    position = ErrorPositionSerializer(required=False)


class QuerySerializer(serializers.ModelSerializer):
    text = serializers.CharField(required=True, allow_blank=True)
    errors = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Query
        fields = [  # noqa: RUF012
            'id',
            'name',
            'text',
            'created',
            'modified',
            'errors',
        ]

    @extend_schema_field(serializers.ListSerializer(child=QueryErrorSerializer()))
    def get_errors(self, obj):
        return obj.validate().get('errors', [])


class QueryResultDataSerializer(serializers.Serializer):
    columns = serializers.ListField(
        child=serializers.CharField(), help_text='List of column names from the query'
    )
    rows = serializers.ListSerializer(
        child=serializers.ListField(
            child=serializers.CharField(allow_null=True), help_text='Values in a single row'
        ),
        help_text='List of query result rows',
    )


class QueryExecutionSerializer(serializers.Serializer):
    results = QueryResultDataSerializer(
        required=False, help_text='Query result data if the query execution was successful'
    )
    success = serializers.BooleanField(help_text='Indicates if the query execution was successful')


class QuerySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = [  # noqa: RUF012
            'id',
            'name',
        ]
