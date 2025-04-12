from rest_framework import mixins, viewsets

from .models import Database
from .serializers import DatabaseSerializer


class DatabaseViewSet(mixins.ListModelMixin, viewsets.GenericViewSet[Database]):
    queryset = Database.objects.all().order_by('name')
    serializer_class = DatabaseSerializer
    pagination_class = None
