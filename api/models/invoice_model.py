from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from ..cloud import upload_to_cloudinary_invoice
import uuid
import tempfile


def generate_invoice_number():
    # Simple invoice number: INV-YYYYMMDD-<short-uuid>
    now = timezone.now()
    short = uuid.uuid4().hex[:6].upper()
    return f"INV-{now.strftime('%Y%m%d')}-{short}"


class Invoice(models.Model):
    order = models.OneToOneField('api.Order', on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=64, unique=True, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    billing_name = models.CharField(max_length=255, blank=True)
    billing_address = models.CharField(max_length=500, blank=True)
    billing_email = models.CharField(max_length=255, blank=True)
    billing_cpf_cnpj = models.CharField(max_length=64, blank=True)

    pdf_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.invoice_number} - Order #{self.order.id}"

    def save(self, *args, **kwargs):

        if not self.invoice_number:
            self.invoice_number = generate_invoice_number()

        try:
            order = self.order
            items = order.items.all()
            if not self.total or float(self.total) == 0:
                self.total = sum([(item.price or 0) * (item.qty or 0) for item in items]) if items else 0

            user = getattr(order, 'customer', None)
            if user:
                if not self.billing_name:
                    self.billing_name = getattr(user, 'name', '') or getattr(user, 'username', '')
                if not self.billing_email:
                    self.billing_email = getattr(user, 'email', '')
            if not self.billing_address:
                self.billing_address = getattr(order, 'delivery_address', '') or ''
        except Exception:
            pass

        super().save(*args, **kwargs)

    def render_html(self, request=None):
        order = self.order
        items = order.items.select_related('product').all()

        items_ctx = []
        for it in items:
            items_ctx.append({
                'name': getattr(it.product, 'name', str(it.product)),
                'qty': it.qty,
                'price': it.price,
                'total': (it.price * it.qty) if it.price is not None else 0,
            })

        ctx = {
            'invoice': self,
            'order': order,
            'items': items_ctx,
            'total': self.total
        }
        return render_to_string('invoice_template.html', ctx, request=request)
