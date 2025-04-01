from rest_framework import serializers

from .models import Query


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = [  # noqa: RUF012
            "id",
            "text",
            "created",
            "modified",
        ]

class QueryResultDataSerializer(serializers.Serializer):
    columns = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of column names from the query"
    )
    rows = serializers.ListSerializer(
        child=serializers.ListField(
            child=serializers.CharField(allow_null=True),
            help_text="Values in a single row"
        ),
        help_text="List of query result rows"
    )

class QueryExecutionSerializer(serializers.Serializer):
    results = QueryResultDataSerializer()
