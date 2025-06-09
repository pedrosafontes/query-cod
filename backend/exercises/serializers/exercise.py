from typing import Any

from databases.serializers import DatabaseSummarySerializer
from drf_spectacular.utils import extend_schema_field
from queries.models import Language
from queries.serializers.execution import QueryResultDataSerializer
from rest_framework import serializers

from ..models import Attempt, Exercise
from .attempt import AttemptSerializer


class BaseExerciseSerializer(serializers.ModelSerializer[Exercise]):
    language = serializers.ChoiceField(choices=Language.choices)
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [  # noqa: RUF012
            'language',
            'completed',
        ]

    def get_completed(self, obj: Exercise) -> bool:
        return obj.completed_by(self.context['request'].user)


class ExerciseSerializer(BaseExerciseSerializer):
    database = DatabaseSummarySerializer(read_only=True)
    attempt = serializers.SerializerMethodField()
    solution_data = QueryResultDataSerializer(read_only=True)

    class Meta:
        model = Exercise
        fields = [  # noqa: RUF012
            'id',
            'language',
            'title',
            'difficulty',
            'description',
            'solution',
            'database',
            'completed',
            'attempt',
            'solution_data',
        ]

    @extend_schema_field(AttemptSerializer)
    def get_attempt(self, obj: Exercise) -> dict[str, Any]:
        attempt, _ = Attempt.objects.get_or_create(user=self.context['request'].user, exercise=obj)
        return AttemptSerializer(attempt).data


class ExerciseSummarySerializer(BaseExerciseSerializer):
    database = DatabaseSummarySerializer(read_only=True)

    class Meta:
        model = Exercise
        fields = [  # noqa: RUF012
            'id',
            'title',
            'difficulty',
            'language',
            'database',
            'completed',
        ]
