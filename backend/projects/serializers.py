from databases.models import Database
from databases.serializers import DatabaseSerializer
from drf_spectacular.utils import extend_schema_field
from queries.serializers import QuerySerializer
from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    database_id = serializers.PrimaryKeyRelatedField(
        queryset=Database.objects.all(), source='database', write_only=True
    )
    database = DatabaseSerializer(read_only=True)
    queries = QuerySerializer(many=True, read_only=True)
    last_modified = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Project
        exclude = [  # noqa: RUF012
            'user'
        ]

    @extend_schema_field(serializers.DateTimeField())
    def get_last_modified(self, obj):
        return obj.last_modified if hasattr(obj, 'last_modified') else obj.modified
