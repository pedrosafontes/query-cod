from rest_framework import mixins, serializers, viewsets

from .models.exercise import Exercise
from .serializers.exercise import ExerciseSerializer, ExerciseSummarySerializer


class ExerciseViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet[Exercise]
):
    queryset = Exercise.objects.all()
    pagination_class = None

    def get_serializer_class(self) -> type[serializers.ModelSerializer[Exercise]]:
        if self.action == 'list':
            return ExerciseSummarySerializer
        return ExerciseSerializer
