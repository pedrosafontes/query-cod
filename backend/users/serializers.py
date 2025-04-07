from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [  # noqa: RUF012
            'id',
            'email',
            'created',
            'modified',
        ]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})


class LogoutSerializer(serializers.Serializer):
    pass
