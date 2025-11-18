from django.db import models


class Notification(models.Model):
    title = models.CharField(max_length=255, default="")
    types = models.CharField(max_length=50, default="")
    description = models.TextField()
    start_date = models.DateTimeField(default=None)
    end_date = models.DateTimeField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for users"
