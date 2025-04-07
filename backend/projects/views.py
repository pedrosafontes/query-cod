from django.shortcuts import render

from .models import Project
from rest_framework import viewsets

from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
