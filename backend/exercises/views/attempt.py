from django.db.models import QuerySet

from drf_spectacular.utils import extend_schema, inline_serializer
from queries.views import SubqueriesMixin
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from ..models import Attempt
from ..serializers import AttemptSerializer
from ..services.mark_attempt import mark_attempt


class AttemptViewSet(
    SubqueriesMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet[Attempt],
):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer

    def get_queryset(self) -> QuerySet[Attempt]:
        return Attempt.objects.filter(user=self.request.user)

    @extend_schema(
        request=None,
        responses=inline_serializer(
            name='SubmissionResponse', fields={'correct': serializers.BooleanField()}
        ),
    )
    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request: Request, pk: str) -> Response:
        attempt = self.get_object()
        correct = mark_attempt(attempt)
        return Response({'correct': correct}, status=200)
