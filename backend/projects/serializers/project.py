from databases.models import Database
from databases.serializers import DatabaseSummarySerializer
from rest_framework import serializers

from ..models import Project
from .query import QuerySummarySerializer


class ProjectSerializer(serializers.ModelSerializer[Project]):
    database_id = serializers.PrimaryKeyRelatedField(
        queryset=Database.objects.all(), source='database', write_only=True
    )
    database = DatabaseSummarySerializer(read_only=True)
    queries = QuerySummarySerializer(many=True, read_only=True)
    last_modified = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Project
        exclude = [  # noqa: RUF012
            'user'
        ]
