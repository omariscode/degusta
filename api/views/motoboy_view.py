from rest_framework import generics, permissions
from ..models import motoboy_model
from ..serializers import CourierSerializer

class MotoboyListCreateView(generics.ListCreateAPIView):
    queryset = motoboy_model.Courier.objects.all()
    serializer_class = CourierSerializer
    permission_classes = [permissions.IsAdminUser]