from assistant.serializers import MessageSerializer
from assistant.services import assist
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


class MessagesMixin:
    @extend_schema(
        request=MessageSerializer,
        responses=MessageSerializer,
    )
    @action(detail=True, methods=['post'], url_path='messages')
    def create_message(self, request: Request, pk: str) -> Response:
        parent = self.get_object()  # type: ignore[attr-defined]

        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        assistant_msg = assist(
            parent,
            user_message=serializer.validated_data['content'],
            system_prompt=self._system_prompt(),
        )

        return Response(MessageSerializer(assistant_msg).data, status=status.HTTP_201_CREATED)

    def _system_prompt(self) -> str | None:
        return None
