from ..models import Notification

STATUS_MESSAGES = {
    "accepted": ("Pedido aceite", "O seu pedido foi aceite e está a ser preparado."),
    "on_the_way": ("Pedido a caminho", "O seu pedido já saiu para entrega."),
    "delivered": ("Pedido entregue", "O seu pedido foi entregue com sucesso."),
    "rejected": ("Pedido rejeitado", "O seu pedido foi rejeitado."),
}

def create_order_notification(order):
    data = STATUS_MESSAGES.get(order.status)

    if not data:
        return  

    title, content = data

    Notification.objects.create(
        title=title,
        content=content,
        customer=order.customer,
    )
