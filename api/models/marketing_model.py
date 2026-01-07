from django.db import models


class Marketing(models.Model):
    title = models.CharField(max_length=255, default="")
    cover = models.TextField(blank=False, null=False)

    def __str__(self):
        return f"Notification for users"
