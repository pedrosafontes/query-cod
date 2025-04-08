from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, LogoutSerializer


class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]  # noqa: RUF012

    def post(self, request):
        form = AuthenticationForm(data=request.data)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return Response({'detail': 'Successfully logged in.'})
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.AllowAny]  # noqa: RUF012    s

    def post(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out.'})
