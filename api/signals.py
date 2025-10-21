from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import product_model, order_model

channel_layer = get_channel_layer()


def broadcast(message: dict):
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)('notifications', {'type': 'notify', 'message': message})


@receiver(post_save, sender=product_model.Product)
def product_saved(sender, instance, created, **kwargs):
    broadcast({'event': 'product_created' if created else 'product_updated', 'id': instance.id, 'name': instance.name})


@receiver(post_save, sender=order_model.Order)
def order_saved(sender, instance, created, **kwargs):
    broadcast({'event': 'order_created' if created else 'order_updated', 'id': instance.id, 'total': str(instance.total)})
