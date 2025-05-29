from databases.types import QueryResult
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers.execution import QueryExecutionSerializer
from .serializers.tree import QueryTreeSerializer
from .services.execution import execute_subquery


class SubqueriesMixin:
    @extend_schema(
        request=None,
        responses=QueryExecutionSerializer,
        parameters=[
            OpenApiParameter(
                name='subquery_id',
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
            ),
        ],
    )
    @action(detail=True, methods=['post'], url_path='subqueries/(?P<subquery_id>[0-9]+)/executions')
    def execute_subquery(self, request: Request, pk: str, subquery_id: str) -> Response:
        query = self.get_object()  # type: ignore[attr-defined]
        results = execute_subquery(query, int(subquery_id))
        return self._handle_execution(results)

    @extend_schema(
        request=None,
        responses=QueryTreeSerializer,
    )
    @action(detail=True, methods=['get'], url_path='tree')
    def tree(self, request: Request, pk: str) -> Response:
        query = self.get_object()  # type: ignore[attr-defined]
        serializer = QueryTreeSerializer(query)
        return Response(serializer.data)

    def _handle_execution(self, results: QueryResult | None) -> Response:
        if results:
            return Response({'success': True, 'results': results})
        else:
            return Response({'success': False})
