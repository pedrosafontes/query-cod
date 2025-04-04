from rest_framework import serializers

from .models import Query


class QuerySerializer(serializers.ModelSerializer):
    # This field is required to be present in the request payload,
    # but it can be an empty string (i.e., blank=True at the model level).
    text = serializers.CharField(required=True, allow_blank=True)

    class Meta:
        model = Query
        fields = [  # noqa: RUF012
            'id',
            'text',
            'created',
            'modified',
        ]


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


class QueryErrorSerializer(serializers.Serializer):
    message = serializers.CharField()
    line = serializers.IntegerField()
    start_col = serializers.IntegerField()
    end_col = serializers.IntegerField()


class QueryPartialUpdateSerializer(serializers.Serializer):
    query = QuerySerializer(help_text='The updated query object after partial update.')
    errors = serializers.ListField(
        required=False,
        help_text='Errors, if any, that occurred during update.',
        child=QueryErrorSerializer(),
    )
