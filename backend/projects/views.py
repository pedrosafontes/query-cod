from django.db.models import QuerySet

from rest_framework import viewsets
from rest_framework.serializers import BaseSerializer

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet[Project]):
    queryset = Project.with_last_modified()
    serializer_class = ProjectSerializer
    pagination_class = None

    def get_queryset(self) -> QuerySet[Project]:
        return Project.with_last_modified().filter(user=self.request.user)

    def perform_create(self, serializer: BaseSerializer[Project]) -> None:
        serializer.save(user=self.request.user)
