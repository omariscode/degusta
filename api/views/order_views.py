from rest_framework import views, permissions, status, generics
from rest_framework.response import Response
from ..services.checkout_serivce import CheckoutService

from ..models import order_model
from ..serializers import OrderDetailSerializer

class CheckoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            order = CheckoutService.process_checkout(request.user, request.data)
            return Response(OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Checkout error: {e}")
            return Response({'detail': 'Internal error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = order_model.Order.objects.all()
    serializer_class = OrderDetailSerializer


class MyOrdersView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return order_model.Order.objects.filter(customer=self.request.user).order_by('-created_at')
