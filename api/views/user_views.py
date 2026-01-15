from rest_framework import generics, permissions
from ..models import user_model
from api.serializers import UserSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class UserUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = user_model.User.objects.all()
    lookup_field = "id"

    def get_object(self):
        return self.request.user

class DeleteAccountView(generics.DestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = user_model.User.objects.all()
    lookup_field = "id"

    def get_object(self):
        return self.request.user

class GetMeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    @method_decorator(cache_page(60 * 60 * 2), name="dispatch")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)   