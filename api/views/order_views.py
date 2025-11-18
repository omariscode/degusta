from rest_framework import views, permissions, status, generics
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from ..services.checkout_serivce import CheckoutService

from ..models import order_model
from ..serializers import OrderDetailSerializer


class CheckoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            order = CheckoutService.process_checkout(request.user, request.data)
            return Response(
                OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Checkout error: {e}")
            return Response(
                {"detail": "Internal error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OrderDetailView(generics.RetrieveAPIView):
    lookup_field = "pk"

    permission_classes = [permissions.IsAuthenticated]
    queryset = order_model.Order.objects.all()
    serializer_class = OrderDetailSerializer


class OrderList(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = order_model.Order.objects.all()
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return order_model.Order.objects.all().order_by("-created_at")
    
    @method_decorator(cache_page(60 * 5), name="dispatch")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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
    
