from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from api import serializers as local_serializers


class AdminRegisterView(generics.CreateAPIView):
    serializer_class = local_serializers.AdminRegisterSerializer


class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        if not user.is_superuser:
            raise serializers.ValidationError('User is not an admin')
        token = super().get_token(user)
        return token


class AdminLoginView(TokenObtainPairView):
    serializer_class = AdminTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class RegisterView(generics.CreateAPIView):
    serializer_class = local_serializers.UserSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class GetMeView(generics.RetrieveAPIView):
    serializer_class = local_serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
