from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from databases.types import QueryResult
from drf_spectacular.utils import OpenApiParameter, extend_schema
from projects.models import Project
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from .models import Query
from .serializers import QueryExecutionSerializer, QuerySerializer
from .services.execution import execute_query, execute_subquery


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='project_pk',
            type=int,
            location=OpenApiParameter.PATH,
            description='ID of the parent project',
        )
    ]
)
class ProjectQueryViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet[Query]):
    serializer_class = QuerySerializer

    def perform_create(self, serializer: BaseSerializer[Query]) -> None:
        project = get_object_or_404(Project, id=self.kwargs['project_pk'])
        serializer.save(project=project)


class QueryViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet[Query],
):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer

    def get_queryset(self) -> QuerySet[Query]:
        return Query.objects.filter(project__user=self.request.user)

    @extend_schema(
        request=None,
        responses=QueryExecutionSerializer,
    )
    @action(detail=True, methods=['post'], url_path='executions')
    def execute(self, request: Request, pk: str) -> Response:
        query = self.get_object()
        results = execute_query(query)
        return self._handle_execution(results)

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
        query = self.get_object()
        results = execute_subquery(query, int(subquery_id))
        return self._handle_execution(results)

    def _handle_execution(self, results: QueryResult | None) -> Response:
        if results:
            return Response({'success': True, 'results': results})
        else:
            return Response({'success': False})
