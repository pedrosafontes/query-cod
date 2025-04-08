from .models import Project
from rest_framework import viewsets

from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.with_last_modified()

    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.with_last_modified().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
