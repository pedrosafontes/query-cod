from rest_framework import serializers

from .models import Database


class DatabaseSerializer(serializers.ModelSerializer[Database]):
    class Meta:
        model = Database
        fields = [  # noqa: RUF012
            'id',
            'name',
            'schema',
        ]


class DatabaseSummarySerializer(serializers.ModelSerializer[Database]):
    class Meta:
        model = Database
        fields = [  # noqa: RUF012
            'id',
            'name',
        ]
