from django.db.models import QuerySet

from queries.views import SubqueriesMixin
from rest_framework import mixins, viewsets

from ..models import Attempt
from ..serializers import AttemptSerializer


class AttemptViewSet(
    SubqueriesMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet[Attempt],
):
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer

    def get_queryset(self) -> QuerySet[Attempt]:
        return Attempt.objects.filter(user=self.request.user)
