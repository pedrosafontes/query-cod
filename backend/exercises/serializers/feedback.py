from queries.serializers.execution import QueryResultDataSerializer
from rest_framework import serializers

from ..models.feedback import Feedback


class FeedbackSerializer(serializers.Serializer[Feedback]):
    correct = serializers.BooleanField()
    results = QueryResultDataSerializer(required=False)
