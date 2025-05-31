from queries.serializers.error import QueryErrorSerializer
from rest_framework import serializers

from ..models.attempt import Attempt


class AttemptSerializer(serializers.ModelSerializer[Attempt]):
    validation_errors = QueryErrorSerializer(many=True, read_only=True)

    class Meta:
        model = Attempt
        fields = [  # noqa: RUF012
            'id',
            'text',
            'validation_errors',
            'completed',
            'language',
        ]
