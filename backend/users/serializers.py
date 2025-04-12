from rest_framework import serializers

from .models import User
from .types import LoginCredentials


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = [  # noqa: RUF012
            'id',
            'email',
            'created',
            'modified',
        ]


class LoginSerializer(serializers.Serializer[LoginCredentials]):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})


class LogoutSerializer(serializers.Serializer[None]):
    pass
