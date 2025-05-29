from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import OpenApiParameter, extend_schema
from projects.models import Project
from queries.models import Language
from queries.serializers.execution import QueryExecutionSerializer
from queries.services.execution import execute_query
from queries.services.transpiler import transpile_query
from queries.views import SubqueriesMixin
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from ..models import Query
from ..serializers import QuerySerializer


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
    SubqueriesMixin,
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
        responses=QuerySerializer,
    )
    @action(detail=True, methods=['post'], url_path='transpile')
    def transpile(self, request: Request, pk: str) -> Response:
        query = self.get_object()
        try:
            transpiled_text = transpile_query(query)
        except:  # noqa: E722
            return Response(status=status.HTTP_400_BAD_REQUEST)

        transpiled_query = Query.objects.create(
            name=query.name,
            text=transpiled_text,
            project=query.project,
            _language=Language.RA if query.language == Language.SQL else Language.SQL,
        )

        return Response(QuerySerializer(transpiled_query).data)
