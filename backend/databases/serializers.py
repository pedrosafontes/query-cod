from rest_framework import serializers

from .models import Database
from .services.schema import get_schema
from .types import Schema


class DatabaseSerializer(serializers.ModelSerializer[Database]):
    schema = serializers.SerializerMethodField()

    class Meta:
        model = Database
        fields = [  # noqa: RUF012
            'id',
            'name',
            'schema',
        ]

    def get_schema(self, obj: Database) -> Schema:
        return get_schema(obj.connection_info)


class DatabaseSummarySerializer(serializers.ModelSerializer[Database]):
    class Meta:
        model = Database
        fields = [  # noqa: RUF012
            'id',
            'name',
        ]
