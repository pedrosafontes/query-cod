from databases.serializers import DatabaseSerializer, DatabaseSummarySerializer
from queries.models import Language
from rest_framework import serializers

from ..models import Exercise


class ExerciseSerializer(serializers.ModelSerializer[Exercise]):
    database = DatabaseSerializer(read_only=True)
    language = serializers.SerializerMethodField()

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
        ]

    def get_language(self, obj: Exercise) -> Language:
        return obj.language


class ExerciseSummarySerializer(serializers.ModelSerializer[Exercise]):
    database = DatabaseSummarySerializer(read_only=True)
    language = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [  # noqa: RUF012
            'id',
            'title',
            'difficulty',
            'language',
            'database',
        ]

    def get_language(self, obj: Exercise) -> Language:
        return obj.language
