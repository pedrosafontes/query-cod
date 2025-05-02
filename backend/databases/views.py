from rest_framework import mixins, viewsets

from .models import Database
from .serializers import DatabaseSerializer, DatabaseSummarySerializer


class DatabaseViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet[Database]
):
    queryset = Database.objects.all().order_by('name')
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'list':
            return DatabaseSummarySerializer
        return DatabaseSerializer
