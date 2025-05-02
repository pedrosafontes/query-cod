from rest_framework import serializers

from .models import Database
from .services.schema import get_schema
from .types import Schema
from .utils.conversion import from_model


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
        db_info = from_model(obj)
        return get_schema(db_info)


class DatabaseSummarySerializer(serializers.ModelSerializer[Database]):
    class Meta:
        model = Database
        fields = [  # noqa: RUF012
            'id',
            'name',
        ]
