from django.db import models


class Marketing(models.Model):
    cover = models.TextField(blank=False, null=False)

    def __str__(self):
        return f"Notification for users"
