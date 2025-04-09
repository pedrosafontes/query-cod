from rest_framework import viewsets

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.with_last_modified()
    serializer_class = ProjectSerializer
    pagination_class = None

    def get_queryset(self):
        return Project.with_last_modified().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
