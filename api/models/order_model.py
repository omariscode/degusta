from django.db import models
# Use app label string references to avoid circular imports

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("paid", "Pago"),
        ("on_the_way", "A caminho"),
        ("delivered", "Entregue"),
        ("canceled", "Cancelado"),
    ]

    customer = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.CharField(max_length=255)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.customer.username}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('api.Product', on_delete=models.CASCADE)
    qty = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)