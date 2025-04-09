from django.shortcuts import get_object_or_404

from drf_spectacular.utils import OpenApiParameter, extend_schema
from projects.models import Project
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Query
from .serializers import QueryExecutionSerializer, QueryPartialUpdateSerializer, QuerySerializer


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
class ProjectQueryViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = QuerySerializer

    def perform_create(self, serializer):
        project = get_object_or_404(Project, id=self.kwargs['project_pk'])
        serializer.save(project=project)


class QueryViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Query.objects.all()
    serializer_class = QuerySerializer

    def get_queryset(self):
        return Query.objects.filter(project__user=self.request.user)

    @extend_schema(
        request=QuerySerializer,
        responses={200: QueryPartialUpdateSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        base_response = super().partial_update(request, *args, **kwargs)
        query = self.get_object()
        return Response(
            {
                'query': base_response.data,
                'errors': query.parse().get('errors'),
            }
        )

    @extend_schema(
        request=None,
        responses=QueryExecutionSerializer,
    )
    @action(detail=True, methods=['post'], url_path='executions')
    def run(self, request, pk=None):
        query = self.get_object()
        if not query.parse()['valid']:
            return Response(
                {
                    'success': False,
                }
            )
        return Response({'success': True, 'results': query.execute()})
