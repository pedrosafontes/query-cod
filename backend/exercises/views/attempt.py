from django.db.models import QuerySet

from assistant.views import MessagesMixin
from drf_spectacular.utils import extend_schema
from exercises.serializers.feedback import FeedbackSerializer
from queries.views import SubqueriesMixin
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from ..models import Attempt
from ..serializers import AttemptSerializer
from ..services.mark_attempt import mark_attempt


class AttemptViewSet(
    MessagesMixin,
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
        responses=FeedbackSerializer,
    )
    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request: Request, pk: str) -> Response:
        attempt = self.get_object()
        return Response(mark_attempt(attempt), status=200)
