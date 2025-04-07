from rest_framework import serializers

from databases.serializers import DatabaseSerializer
from databases.models import Database
from queries.serializers import QuerySerializer
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    database_id = serializers.PrimaryKeyRelatedField(
        queryset=Database.objects.all(), source='database', write_only=True
    )
    database = DatabaseSerializer(read_only=True)
    queries = QuerySerializer(many=True, read_only=True)

    class Meta:
        model = Project
        exclude = ['user']
