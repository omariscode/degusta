from django.db import models
class Invoice(models.Model):
    # refer to Order by app label to avoid import cycles
    order = models.OneToOneField('api.Order', on_delete=models.CASCADE, related_name='invoice')
    pdf = models.FileField(upload_to='invoices/')
    issued_at = models.DateTimeField(auto_now_add=True)
