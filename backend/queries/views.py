from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Query
from .serializers import QueryExecutionSerializer, QueryPartialUpdateSerializer, QuerySerializer


class QueryViewSet(viewsets.ModelViewSet):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = [permissions.AllowAny] # noqa: RUF012
    pagination_class = None

    @extend_schema(
        request=QuerySerializer,
        responses={200: QueryPartialUpdateSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        base_response = super().partial_update(request, *args, **kwargs)
        query = self.get_object()
        return Response({
            'query': base_response.data,
            'errors': query.parse().get('errors'),
        })

    @extend_schema(
        request=None,
        responses=QueryExecutionSerializer,
    )
    @action(detail=True, methods=['post'], url_path='executions')
    def run(self, request, pk=None):
        query = self.get_object()
        if not query.parse()['valid']:
            return Response({
                'success': False,
            })
        return Response({
            'success': True,
            'results': query.execute()
        })