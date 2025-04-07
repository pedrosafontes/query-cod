from django.shortcuts import render

from .models import Project
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema

from .serializers import ProjectSerializer

from drf_spectacular.utils import OpenApiParameter


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
