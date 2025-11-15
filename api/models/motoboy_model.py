from django.db import models


class Courier(models.Model):
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15, unique=True)
    license_plate = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} - {self.vehicle_type} ({self.license_plate})"
