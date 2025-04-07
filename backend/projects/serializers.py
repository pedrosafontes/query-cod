from rest_framework import serializers

from queries.serializers import QuerySerializer
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    database = serializers.StringRelatedField()
    queries = QuerySerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
