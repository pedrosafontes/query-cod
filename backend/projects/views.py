from django.shortcuts import render

from .models import Project
from rest_framework import permissions, mixins, viewsets

from .serializers import ProjectSerializer


class ProjectViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
