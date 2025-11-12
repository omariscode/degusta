from rest_framework import generics
from ..models import notification_model
from ..serializers import NotificationSerializer
from rest_framework import permissions

class NotificationListView(generics.ListCreateAPIView):
    queryset = notification_model.Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [permissions.AllowAny]