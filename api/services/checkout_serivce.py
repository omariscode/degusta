from django.db import transaction
from ..models import product_model, order_model, invoice_model
from ..utils.invoice_utils import generate_invoice_pdf
from ..utils.sms import send_sms


class CheckoutService:

    @staticmethod
    @transaction.atomic
    def process_checkout(user, data):
        items = data.get("items", [])
        if not items:
            raise ValueError("No items provided")

        total = 0
        product_objs = {}

        for item in items:
            product_id = item.get("product")
            qty = int(item.get("qty", 0))
            product = (
                product_model.Product.objects.select_for_update()
                .filter(id=product_id)
                .first()
            )
            if not product:
                raise ValueError(f"Product {product_id} not found")
            if product.stock < qty:
                raise ValueError(f"Not enough stock for product {product.id}")
            product_objs[product_id] = (product, qty)
            total += float(product.price) * qty

        order = order_model.Order.objects.create(
            customer=user,
            total=total,
            delivery_address=data.get("delivery_address", ""),
        )

        for product, qty in product_objs.values():
            order_model.OrderItem.objects.create(
                order=order, product=product, qty=qty, price=product.price
            )
            product.stock -= qty
            product.save()

        order.status = "pending"
        order.save()

        invoice = invoice_model.Invoice.objects.create(order=order)
        invoice.pdf_url = generate_invoice_pdf(invoice, user)
        invoice.save()

        send_sms(
            ["+18777804236"],
            f"Novo pedido de {invoice.billing_name}, local de entrega: {order.delivery_address}, com o pagamento total de {order.total}Kz.",
        )

        return order
