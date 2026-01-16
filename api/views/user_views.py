from rest_framework import generics, permissions
from ..models import user_model, notification_model, order_model
from api.serializers import UserSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..serializers import NotificationSerializer, OrderDetailSerializer



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


class UserNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = (
            notification_model.Notification.objects
            .filter(customer=request.user)
            .order_by("-created_at")
        )

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class MyOrdersView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return order_model.Order.objects.filter(customer=self.request.user).order_by(
            "-created_at"
        )
    
    @method_decorator(cache_page(60 * 5), name="dispatch")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    