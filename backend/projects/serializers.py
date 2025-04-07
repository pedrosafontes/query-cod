from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    database = serializers.StringRelatedField()

    class Meta:
        model = Project
        fields = '__all__'
