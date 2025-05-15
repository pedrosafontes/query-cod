from queries.types import ErrorPosition, QueryError
from rest_framework import serializers


class ErrorPositionSerializer(serializers.Serializer[ErrorPosition]):
    line = serializers.IntegerField()
    start_col = serializers.IntegerField()
    end_col = serializers.IntegerField()


class QueryErrorSerializer(serializers.Serializer[QueryError]):
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    hint = serializers.CharField(required=False, allow_blank=True)
    position = ErrorPositionSerializer(required=False)
