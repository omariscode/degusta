from rest_framework import views, permissions, status, generics
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from ..utils.notification import create_order_notification
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
    lookup_field = "id"

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

class RejectOrderView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, id):
        order = get_object_or_404(order_model.Order, id=id)

        order.status = "rejected"
        order.save()

        create_order_notification(order)

        return Response(
            {"detail": "Order rejected successfully."},
            status=status.HTTP_200_OK,
        )

class AdvanceStatusView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    STATUS_SEQUENCE = [
        "pending",
        "accepted",
        "on_the_way",
        "delivered",
    ]

    def post(self, request, id):
        order = get_object_or_404(order_model.Order, id=id)

        if order.status not in self.STATUS_SEQUENCE:
            return Response(
                {"detail": "Order status cannot be advanced."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_index = self.STATUS_SEQUENCE.index(order.status)

        if current_index == len(self.STATUS_SEQUENCE) - 1:
            return Response(
                {"detail": "Order is already in the final status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = self.STATUS_SEQUENCE[current_index + 1]
        order.save()

        create_order_notification(order)

        return Response(
            {"detail": f"Order status advanced to {order.status}."},
            status=status.HTTP_200_OK,
        )
    
