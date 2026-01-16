from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import marketing_model, product_model, order_model, notification_model

channel_layer = get_channel_layer()


def broadcast(message: dict):
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        "notifications", {"type": "notify", "message": message}
    )

@receiver(post_save, sender=product_model.Product)
def product_saved(sender, instance, created, **kwargs):
    broadcast(
        {
            "event": "product_created" if created else "product_updated",
            "id": instance.id,
            "name": instance.name,
            "price": str(instance.price),
            "stock": instance.stock,
            "image": instance.image,
        }
    )


@receiver(post_save, sender=order_model.Order)
def order_saved(sender, instance, created, **kwargs):
    broadcast(
        {
            "event": "order_created" if created else "order_updated",
            "id": instance.id,
            "customer_name": instance.customer.username,
            "total": str(instance.total),
        }
    )


@receiver(post_save, sender=marketing_model.Marketing)
def marketing_saved(sender, instance, created, **kwargs):
    broadcast(
        {
            "event": "marketing_created" if created else "marketing_updated",
            "id": instance.id,
            "title": instance.title,
            "cover": instance.cover,
        }
    )

@receiver(post_save, sender=notification_model.Notification)
def notification_saved(sender, instance, created, **kwargs):
    if created:
        broadcast(
            {
                "event": "notification_created",
                "id": instance.id,
                "title": instance.title,
                "content": instance.content,
                "customer_id": instance.customer.id,
            }
        )