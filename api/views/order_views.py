from rest_framework import views, permissions, status, generics
from rest_framework.response import Response
from django.db import transaction
from django.template.loader import render_to_string
import os
import subprocess
from django.conf import settings

from ..models import product_model, order_model, invoice_model
from ..serializers import OrderDetailSerializer
from ..utils import sms
from ..utils.cloud import upload_to_cloudinary_invoice

try:
    import pdfkit
except Exception:
    pdfkit = None


class CheckoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, format=None):
        data = request.data
        items = data.get('items', [])
        if not items:
            return Response({'detail': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)

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

        order = order_model.Order.objects.create(customer=request.user, total=total, delivery_address=data.get('delivery_address', ''))

        for pid, (p, qty) in product_objs.items():
            order_item = order_model.OrderItem.objects.create(order=order, product=p, qty=qty, price=p.price)
            p.stock = p.stock - qty
            p.save()

        order.status = 'paid'
        order.save()

        invoice = invoice_model.Invoice(order=order)
        invoice.save()  

        try:
            html = invoice.render_html(request=request)
        except Exception:
            html = render_to_string('invoice_template.html', {
                'user': request.user,
                'order': order,
                'invoice': invoice,
                'items': [{'name': i.product.name, 'qty': i.qty, 'price': str(i.price), 'total': float(i.price) * i.qty} for i in order.items.all()],
                'total': str(order.total)
            })

        tmp_dir = os.path.join(settings.BASE_DIR, 'tmp') if hasattr(settings, 'BASE_DIR') else 'tmp'
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_html_path = os.path.join(tmp_dir, f'invoice_{order.id}.html')
        with open(tmp_html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        pdf_saved = False
        if pdfkit:
            try:
                pdf_bytes = pdfkit.from_string(html, False)
                tmp_pdf_path = os.path.join(tmp_dir, f'invoice_{order.id}.pdf')
                with open(tmp_pdf_path, 'wb') as f:
                    f.write(pdf_bytes)
                invoice.pdf_url = upload_to_cloudinary_invoice(tmp_pdf_path)
                pdf_saved = True
                os.unlink(tmp_pdf_path)
            except Exception as e:
                print(f"pdfkit error: {e}")
                pdf_saved = False

        if not pdf_saved:
            try:
                tmp_pdf_path = os.path.join(tmp_dir, f'invoice_{order.id}.pdf')
                subprocess.run(['wkhtmltopdf', tmp_html_path, tmp_pdf_path], check=True)
                invoice.pdf_url = upload_to_cloudinary_invoice(tmp_pdf_path)
                pdf_saved = True
                os.unlink(tmp_pdf_path)
            except Exception as e:
                print(f"wkhtmltopdf error: {e}")
                pdf_saved = False

        if not pdf_saved:
            try:
                invoice.pdf_url = upload_to_cloudinary_invoice(tmp_html_path)
            except Exception as e:
                print(f"HTML upload error: {e}")

        invoice.save()

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
