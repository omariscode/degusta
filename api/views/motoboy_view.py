from rest_framework import generics, permissions, status
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from ..models import motoboy_model, order_model
from ..serializers import CourierSerializer
from rest_framework.decorators import api_view
from rest_framework.views import Response
from ..utils.sms import send_sms


class MotoboyListCreateView(generics.ListCreateAPIView):
    queryset = motoboy_model.Courier.objects.all()
    serializer_class = CourierSerializer
    permission_classes = [permissions.IsAdminUser]

    @method_decorator(cache_page(60 * 5), name="dispatch")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MotoboyDelete(generics.DestroyAPIView):
    lookup_field = "id"

    queryset = motoboy_model.Courier.objects.all()
    serializer_class = CourierSerializer
    permission_classes = [permissions.IsAdminUser]


class MotoboyUpdate(generics.UpdateAPIView):
    lookup_field = "id"

    queryset = motoboy_model.Courier.objects.all()
    serializer_class = CourierSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(["POST"])
def send_order_to_courier(request, order_id):
    try:
        courier_id = request.data.get("courier_id")

        if not courier_id:
            return Response(
                {"error": "courier_id é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = order_model.Order.objects.get(id=order_id)
        except order_model.Order.DoesNotExist:
            return Response(
                {"error": "Pedido não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            courier = motoboy_model.Courier.objects.get(id=courier_id)
        except motoboy_model.Courier.DoesNotExist:
            return Response(
                {"error": "Motoboy não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        message = (
            f"📦 Novo Pedido\n"
            f"Cliente: {order.customer.name}\n"
            f"Endereço: {order.delivery_address}\n"
            f"Total: Kz {order.total}\n"
            f"Status: {order.get_status_display()}"
        )

        result = send_sms(message, to=courier.phone_number)

        if result["success"]:
            return Response(
                {"message": "Pedido enviado ao motoboy por SMS!"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": result["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
