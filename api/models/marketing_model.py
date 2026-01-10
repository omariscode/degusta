from django.db import models


class Marketing(models.Model):
    title = models.CharField(max_length=255)
    cover = models.TextField()

    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_combo = models.BooleanField(default=False)

    start_date = models.DateTimeField(default="")
    end_date = models.DateTimeField(default="")

    is_active = models.BooleanField(default=True)

    products = models.ManyToManyField("api.Product", related_name="campaigns")


    def __str__(self):
        return f"Notification for users"
