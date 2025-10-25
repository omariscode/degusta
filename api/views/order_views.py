from rest_framework import views, permissions, status, generics
from rest_framework.response import Response
from django.db import transaction
from django.template.loader import render_to_string
import os

from ..models import product_model, order_model, invoice_model
from ..serializers import OrderDetailSerializer
from ..utils import sms

try:
    import pdfkit
except Exception:
    pdfkit = None


class CheckoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, format=None):
        """Expect payload:
        {
            "delivery_address": "Rua X",
            "items": [{"product": product_id, "qty": 2}, ...]
        }
        """
        data = request.data
        items = data.get('items', [])
        if not items:
            return Response({'detail': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)

        # calculate total and check stock
        total = 0
        product_objs = {}
        for it in items:
            pid = it.get('product')
            qty = int(it.get('qty', 0))
            try:
                p = product_model.Product.objects.select_for_update().get(pk=pid)
            except product_model.Product.DoesNotExist:
                return Response({'detail': f'Product {pid} not found'}, status=status.HTTP_400_BAD_REQUEST)
            if p.stock < qty:
                return Response({'detail': f'Not enough stock for product {p.id}'}, status=status.HTTP_400_BAD_REQUEST)
            product_objs[pid] = (p, qty)
            total += float(p.price) * qty

        # create order
        order = order_model.Order.objects.create(customer=request.user, total=total, delivery_address=data.get('delivery_address', ''))

        # create items and decrement stock
        for pid, (p, qty) in product_objs.items():
            order_item = order_model.OrderItem.objects.create(order=order, product=p, qty=qty, price=p.price)
            p.stock = p.stock - qty
            p.save()

        # mark as paid for this example and create invoice
        order.status = 'paid'
        order.save()

        # generate invoice (pdf or html) and attach to Invoice model
        context = {'user': request.user, 'items': [{'name': i.product.name, 'qty': i.qty, 'price': str(i.price)} for i in order.items.all()], 'total': str(order.total)}
        html = render_to_string('invoice_template.html', context)
        invoice = invoice_model.Invoice(order=order)
        if pdfkit:
            try:
                pdf = pdfkit.from_string(html, False)
                # write to a temporary file then save to model
                tmp_path = f'tmp/invoice_{order.id}.pdf'
                os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
                with open(tmp_path, 'wb') as f:
                    f.write(pdf)
                invoice.pdf.name = tmp_path
            except Exception:
                # fallback: save HTML as .html file
                tmp_path = f'tmp/invoice_{order.id}.html'
                with open(tmp_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                invoice.pdf.name = tmp_path
        else:
            tmp_path = f'tmp/invoice_{order.id}.html'
            os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(html)
            invoice.pdf.name = tmp_path

        invoice.save()

        # notify motoqueiros (placeholder)
        sms.send_sms('923000000', f'Novo pedido #{order.id} - {order.total}')

        return Response(OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = order_model.Order.objects.all()
    serializer_class = OrderDetailSerializer


class MyOrdersView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return order_model.Order.objects.filter(customer=self.request.user).order_by('-created_at')
