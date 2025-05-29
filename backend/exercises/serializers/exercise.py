from typing import Any, cast

from databases.serializers import DatabaseSerializer, DatabaseSummarySerializer
from drf_spectacular.utils import extend_schema_field
from queries.models import Language
from rest_framework import serializers

from ..models import Attempt, Exercise
from .attempt import AttemptSerializer


class BaseExerciseSerializer(serializers.ModelSerializer[Exercise]):
    language = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [  # noqa: RUF012
            'language',
            'completed',
        ]

    def get_language(self, obj: Exercise) -> Language:
        return cast(Language, obj.language)

    def get_completed(self, obj: Exercise) -> bool:
        return obj.completed_by(self.context['request'].user)


class ExerciseSerializer(BaseExerciseSerializer):
    database = DatabaseSerializer(read_only=True)
    attempt = serializers.SerializerMethodField()

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
